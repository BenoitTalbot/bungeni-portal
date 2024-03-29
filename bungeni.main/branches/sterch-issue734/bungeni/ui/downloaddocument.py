# encoding: utf-8
# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt
from __future__ import with_statement
"""Views for download of documents in formats - PDF/ODT

$Id$
"""

log = __import__("logging").getLogger("bungeni.ui")


import re
import os
import time
import htmlentitydefs
import random
import base64
from tidylib import tidy_fragment
from lxml import etree

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from zope.component import getUtility
#from zope.lifecycleevent import ObjectCreatedEvent
#from zope.event import notify
from zope.component.interfaces import ComponentLookupError
from zc.table import column
from zope.app.component.hooks import getSite

from interfaces import IOpenOfficeConfig
from bungeni.alchemist import Session
from bungeni.models import domain, interfaces
from bungeni.ui.table import LinkColumn, SimpleContainerListing
from appy.pod.renderer import Renderer


from bungeni.utils.capi import capi
from bungeni.core.dc import IDCDescriptiveProperties
from bungeni.core.translation import translate_i18n
from bungeni.ui.i18n import _
from bungeni.ui.utils import url, misc

#!+ReportConfiguration(murithi, jul-2011) - Report configuration and templates
# should eventually be loaded from bungeni_custom
SUB_CONTAINERS = ["signatories", "files", "changes"]
CONTAINER_TITLES = {"changes": _(u"Timeline")}
EXTRA_COLUMNS = {"changes": ["description"],
                 "signatories": ["status"]
                }

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def cleanupText(text):
    """This method cleans up the text of the report using libtidy"""
    #tidylib options
    options = dict(output_xhtml=1,
                    add_xml_decl=1,
                    indent=1,
                    tidy_mark=0,
                    char_encoding="utf8",
                    quote_nbsp=0)
    #remove html entities from the text
    ubody_text = unescape(text)
    #clean up xhtml using tidy
    aftertidy, errors = tidy_fragment(ubody_text.encode("utf8"), options, keep_doc=False)
    #tidylib returns a <tidy.lib._Document object>
    return str(aftertidy)


def get_listings(context, request, sub_container_name=""):
    trusted = removeSecurityProxy(context)    
    if hasattr(trusted, sub_container_name):
        sub_container = removeSecurityProxy(
            getattr(trusted, sub_container_name)
        )
        #!+DESCRIPTOR_LOOKUP(murithi, jul-2011) descriptor lookup fails in 
        # testing - as at r8474 : use sub_container_name as title
        #table_title = (CONTAINER_TITLES.get(sub_container_name, None) or 
        #    IDCDescriptiveProperties(sub_container).title
        #)
        table_title = sub_container_name
        columns = [
            LinkColumn("title", lambda i,f:IDCDescriptiveProperties(i).title),
        ]
        for extra_col in EXTRA_COLUMNS.get(sub_container_name, []):
            columns.append(column.GetterColumn(extra_col, 
                    lambda i,f:getattr(IDCDescriptiveProperties(i), extra_col)
                )
            )
        if hasattr(sub_container, "values"):
            items = [ removeSecurityProxy(it) for it in sub_container.values() ]
        else:
            items = [ removeSecurityProxy(it) for it in sub_container ]
        if not len(items):
            return u""
        formatter = SimpleContainerListing(context, request, items,
            columns=columns
        )
        return formatter(translate_i18n(table_title))
    else:
        return u""

class DownloadDocument(BrowserView):
    """Abstact base class for ODT and PDF views"""
    #path to the odt template. Must be set by sub-class
    oo_template_file = None
    #Error page in case of failure to generate document
    error_template = ViewPageTemplateFile("templates/report_error.pt")
    #Custom Template selection UI
    document_template_select = ViewPageTemplateFile(
        "templates/choose_oo_template.pt"
    )
    #Source document
    document = None
    #document type to be produced
    document_type = None
    site_url = ""
    def __init__(self, context, request):
        self.document = removeSecurityProxy(context)
        self.site_url = url.absoluteURL(getSite(), request)
        super(DownloadDocument, self).__init__(context, request)

    def setHeader(self, document_type):
        content_type_mapping ={"pdf":"application/pdf",
                               "odt":"application/vnd.oasis.opendocument.text"}
        self.request.response.setHeader("Content-type",
            "%s" % content_type_mapping[document_type]
        )
        self.request.response.setHeader("Content-disposition", 
            'inline;filename="%s"' % self.file_name
        )
    def bodyText(self):
        """Returns body text of document. Must be implemented by subclass"""

    @property
    def file_name(self):
        fname = misc.slugify(self.document.short_name)
        if interfaces.IReport.providedBy(self.document):
            fname = misc.slugify(
                u'-'.join((self.document.short_name, 
                    self.document.start_date.isoformat(), 
                    self.document.end_date.isoformat()))
            )
        return u"%s.%s" %(fname, self.document_type)

    def generateDoc(self):
        """Generates ODT/PDF doc"""
        tempFileName = os.path.dirname(__file__) + "/tmp/%f-%f.%s" % (
                            time.time(),random.random(),self.document_type)
        params = {}
        params["body_text"] = cleanupText(self.bodyText())
        params["listings"] = cleanupText(
            u"".join(get_listings(self.context, self.request, listing_id) 
                for listing_id in SUB_CONTAINERS
            )
        )
        openofficepath = getUtility(IOpenOfficeConfig).getPath()
        ooport = getUtility(IOpenOfficeConfig).getPort()
        renderer = Renderer(self.oo_template_file, params, tempFileName,
                                               pythonWithUnoPath=openofficepath,
                                               ooPort=ooport)
        from globalSemaphore import globalOpenOfficeSemaphore
        try:
            # appy.pod only connects with openoffice when converting to
            # PDF. We need to restrict number of connections to the
            # max connections option set in openoffice.zcml
            if self.document_type == "pdf":
                with globalOpenOfficeSemaphore:
                    renderer.run()
            else:
                renderer.run()
        except:
            log.exception("An error occured during ODT/PDF generation")
            try:
                return self.error_template()
            # This should only happen in unit tests because the site config
            # has not been read in
            except ComponentLookupError:
                return u"An error occured during ODT/PDF generation."
        f = open(tempFileName, "rb")
        doc = f.read()
        f.close()
        os.remove(tempFileName)    
        self.setHeader(self.document_type)
        return doc
        
    def documentData(self, cached=False):
        """Either generate ODT/PDF doc or retrieve from attached files of the
        content item. Cached should only be True for content items that
        are immutable eg. reports."""
        #TODO : Either generate a hash of a mutable content item and store it 
        # with the odt/pdf doc or track changes to a doc
        # Add caching by state. items in terminal states do not change
        tempFileName = os.path.dirname(__file__) + "/tmp/%f.%s" % (
                                                time.time(),self.document_type)
        if cached:
            session = Session()
            d = [f.file_title for f in self.document.attached_files]
            if self.document_type not in d:
                file_type = session.query(domain.AttachedFileType) \
                               .filter(domain.AttachedFileType \
                                                .attached_file_type_name 
                                            == "system") \
                               .first()
                if file_type is None:
                    file_type = domain.AttachedFileType()
                    file_type.attached_file_type_name = "system"
                    file_type.language = self.document.language
                    session.add(file_type)
                    session.flush()
                attached_file = domain.AttachedFile()
                attached_file.file_title = self.document_type
                attached_file.file_data = self.generateDoc()
                attached_file.language = self.document.language
                attached_file.type = file_type
                self.document.attached_files.append(attached_file)
                session.add(self.document)
                session.flush()
                #!+ REPORTS(miano, apr-2011) Anonymous users may prompt 
                #the storage of a report if it hasn't been stored before.
                #Actions that are executed when an objectcreatedevent
                #is triggered may require a principal in the 
                #request eg. auditing. Report attachments are not displayed in 
                #listings or any other place so not triggering the event 
                #shouldn't do any harm.
                #notify(ObjectCreatedEvent(attached_file))
            for f in self.document.attached_files:
                if f.file_title == self.document_type: 
                    self.setHeader(self.document_type)
                    return f.file_data.__str__()
            #If file is not found
            try:
                return self.error_template()
            except ComponentLookupError:
                return u"An error occured during ODT/PDF generation."
        else:
            return self.generateDoc()
        
    def documentTemplates(self):
        templates = []
        templates_path = capi.get_path_for("reporting", "templates", 
            "templates.xml"
        )
        if os.path.exists(templates_path):
            template_config = etree.fromstring(open(templates_path).read())
            for template in template_config.iter(tag="template"):
                location = capi.get_path_for("reporting", "templates", 
                    template.get("file")
                )
                template_file_name = template.get("file")
                if os.path.exists(location):
                    template_dict = dict(
                        title = template.get("name"),
                        language = template.get("language"),
                        location = base64.encodestring(template_file_name)
                    )
                    templates.append(template_dict)
                else:
                    log.error("Template does noet exist. No file found at %s.", 
                        location
                    )
        return templates

    def templateSelected(self):
        """Check if a template was provided in the request as url/form 
        parameter.
        """
        template_selected = False
        template_encoded = self.request.form.get("template", "")
        if template_encoded != "":
            template_file_name = base64.decodestring(template_encoded)
            template_path = capi.get_path_for("reporting", "templates", 
                template_file_name
            )
            if os.path.exists(template_path):
                template_selected = True
                self.oo_template_file = template_path
        return template_selected

class ReportODT(DownloadDocument):
    oo_template_file = os.path.dirname(__file__) + "/templates/agenda.odt"
    document_type = "odt"
    
    def bodyText(self):
        return self.document.body_text

    def __call__(self):
        if self.documentTemplates():
            if not self.templateSelected():
                return self.document_template_select()
        return self.documentData(cached=True)


class ReportPDF(ReportODT):
    document_type = "pdf"

#The classes below generate ODT and PDF documents of bungeni content items
#TODO:This implementation displays a default set of the content item's attributes
#once the localisation API is complete it should get info on which attributes
#to display from there.
class BungeniContentODT(DownloadDocument):
    oo_template_file = os.path.dirname(__file__) + "/templates/bungenicontent.odt"  
    template = ViewPageTemplateFile("templates/bungenicontent.pt")
    document_type = "odt"
    
    def bodyText(self):
        if not hasattr(self.document,"group"):
            session = Session()
            self.document.group = session.query(domain.Group).get(self.document.parliament_id)
            # !+SESSION_CLOSE(taras.sterch, july-2011) there is no need to close the 
            # session. Transaction manager will take care of this. Hope it does not 
            # brake anything.
            #session.close()
        return self.template()
    
    def __call__(self):
        return self.documentData(cached=False)
            
class BungeniContentPDF(DownloadDocument):
    oo_template_file = os.path.dirname(__file__) + "/templates/bungenicontent.odt"  
    template = ViewPageTemplateFile("templates/bungenicontent.pt")
    document_type = "pdf"
    
    def bodyText(self):
        if not hasattr(self.document,"group"):
            session = Session()
            self.document.group = session.query(domain.Group).get(self.document.parliament_id)
            # !+SESSION_CLOSE(taras.sterch, july-2011) there is no need to close the 
            # session. Transaction manager will take care of this. Hope it does not 
            # brake anything.
            #session.close()
        return self.template()
    
    def __call__(self):
        return self.documentData(cached=False)
