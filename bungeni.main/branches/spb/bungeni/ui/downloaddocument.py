# encoding: utf-8

log = __import__("logging").getLogger("bungeni.ui")
import re
import os
import tidy
import time
import htmlentitydefs
from interfaces import IOpenOfficeConfig
from bungeni.alchemist import Session
from bungeni.models import domain
from zope import interface
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.security.proxy import removeSecurityProxy
from zope.component import getUtility
from zope.lifecycleevent import ObjectCreatedEvent
from zope.event import notify
from xml.dom import minidom
from appy.pod.renderer import Renderer

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
    #utidylib options
    options = dict(output_xhtml=1,
                    add_xml_decl=1,
                    indent=1,
                    tidy_mark=0,
                    char_encoding="utf8",
                    quote_nbsp=0)
    #remove html entities from the text
    ubody_text = unescape(text)
    #clean up xhtml using tidy
    aftertidy = tidy.parseString(ubody_text.encode("utf8"), **options)
    #tidy returns a <tidy.lib._Document object>
    dom = minidom.parseString(str(aftertidy))
    nodeList = dom.getElementsByTagName("body")
    text = ""
    for childNode in nodeList[0].childNodes:
        text += childNode.toxml()
    dom.unlink()
    return text

class DownloadDocument(BrowserView):
    """Abstact base class for ODT and PDF views"""
    #path to the odt template. Must be set by sub-class
    oo_template_file = None
    #Error page in case of failure to generate document
    error_template = ViewPageTemplateFile("templates/report_error.pt")
    #Source document
    document = None
    #document type to be produced
    document_type = None
    def __init__(self, context, request):
        self.document = removeSecurityProxy(context)
        super(DownloadDocument, self).__init__(context, request)

    def setHeader(self, document_type):
        content_type_mapping ={"pdf":"application/pdf",
                               "odt":"application/vnd.oasis.opendocument.text"}
        self.request.response.setHeader("Content-type", "%s" % 
                                            content_type_mapping[document_type])
        self.request.response.setHeader("Content-disposition", 
                                            'inline;filename="%s.%s"' %  
                                                (self.document.short_name,
                                                 document_type))
    def bodyText(self):
        """Returns body text of document. Must be implemented by subclass"""
    
    def generateDoc(self):
        """Generates ODT/PDF doc"""
        tempFileName = os.path.dirname(__file__) + "/tmp/%f.%s" % (time.time(),self.document_type)
        params = {}
        params["body_text"] = cleanupText(self.bodyText())
        openofficepath = getUtility(IOpenOfficeConfig).getPath()
        renderer = Renderer(self.oo_template_file, params, tempFileName,
                                               pythonWithUnoPath=openofficepath)
        try:
            renderer.run()
        except:
            log.exception("An error occured during ODT/PDF generation")
            return self.error_template()
        f = open(tempFileName, "rb")
        doc = f.read()
        f.close()
        os.remove(tempFileName)    
        return doc
        
    def documentData(self, cached=False):
        """Either generate ODT/PDF doc or retrieve from attached files of the
        content item. Cached should only be True for content items that
        are immutable eg. reports."""
        #TODO : Either generate a hash of a mutable content item and store it 
        # with the odt/pdf doc or track changes to a doc
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
                session.commit()
                notify(ObjectCreatedEvent(attached_file))
            for f in self.document.attached_files:
                if f.file_title == self.document_type: 
                    self.setHeader(self.document_type)
                    return f.file_data.__str__()
            #If file is not found
            return self.error_template()
        else:
            self.setHeader(self.document_type)
            return self.generateDoc()
        
class ReportODT(DownloadDocument):
    oo_template_file = os.path.dirname(__file__) + "/templates/agenda.odt"
    document_type = "odt"
    
    def bodyText(self):
        return self.document.body_text
        
    def __call__(self):
        return self.documentData(cached=True)
            
class ReportPDF(DownloadDocument):
    oo_template_file = os.path.dirname(__file__) + "/templates/agenda.odt"
    document_type = "pdf"
    
    def bodyText(self):
        return self.document.body_text
        
    def __call__(self):
        return self.documentData(cached=True)
        
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
        return self.template()
    
    def __call__(self):
        return self.documentData(cached=False)
