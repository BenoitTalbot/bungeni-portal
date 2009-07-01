import datetime
from zope import interface
from zope import schema
from zope.i18n import translate
from zope.formlib import form
from zope.formlib.namedtemplate import NamedTemplate
from zope.app.pagetemplate import ViewPageTemplateFile

from bungeni.models.interfaces import IParliament

from bungeni.ui.i18n import _
from bungeni.ui.cookies import get_date_range
from bungeni.ui.cookies import set_date_range
from bungeni.ui.cookies import unset_date_range
from bungeni.ui.widgets import SelectDateWidget

class ArchiveDatesForm(form.PageForm):
    class IDateRangeSchema(interface.Interface):
        start_date = schema.Date(
            title=_(u"Start date"),
            required=False)

        end_date = schema.Date(
            title=_(u"End date"),
            required=False)

        parliament = schema.Choice(
            title=_(u"Filter by parliament"),
            description=_(u"Set date range to that of a given particular parliament."),
            vocabulary="bungeni.vocabulary.Parliaments",
            required=False)

    template = NamedTemplate('alchemist.subform')
    form_fields = form.Fields(IDateRangeSchema, render_context=True)
    form_fields['start_date'].custom_widget = SelectDateWidget
    form_fields['end_date'].custom_widget = SelectDateWidget
    form_description = _(u"Filter the archive by date range.")

    def is_in_parliament(self, context):
        parent = context
        while not IParliament.providedBy(parent):
            parent = getattr(parent, '__parent__', None)            
            if parent is None:
                return False
        return True                
            
    def get_start_end_restictions(self, context):
        parent = context
        while not hasattr(parent,'start_date'):
            parent = getattr(parent, '__parent__', None)            
            if parent is None:
                return None, None           
        return getattr(parent, 'start_date', None), getattr(parent, 'end_date', None)

    def setUpWidgets(self, ignore_request=False, cookie=None):
        if ignore_request is False:
            start_date, end_date = get_date_range(self.request)
        else:
            start_date = end_date = None

        context = type("context", (), {
            'start_date': start_date,
            'end_date': end_date,
            'parliament': None})

        self.adapters = {
            self.IDateRangeSchema: context,
            }
        if self.is_in_parliament(self.context):
            self.form_fields = self.form_fields.omit('parliament')
            
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=True)
        try:
            self.widgets['parliament']._messageNoValue = _(
                u"Select parliament...")
        except KeyError:
            pass   
        start, end = self.get_start_end_restictions(self.context)                         
        self.widgets['start_date'].set_min_date(start)
        self.widgets['end_date'].set_min_date(start)                                        
        self.widgets['start_date'].set_max_date(end)
        self.widgets['end_date'].set_max_date(end)   
        
        
    @form.action(u"Filter")
    def handle_filter(self, action, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        params = {}

        if start_date and end_date:
            if start_date > end_date:
                self.status = _("Invalid Date Range")
                unset_date_range(self.request)
                return
        start, end = self.get_start_end_restictions(self.context)                        
        if start_date and end:            
            if start_date > end:                    
                  self.status = (_("Start date must be before %s") %
                        end.strftime("%d %B %Y"))
                  unset_date_range(self.request)
                  return                        
        if end_date and start:
            if end_date < start:
                  self.status = (_("End date must be after %s") %
                        start.strftime("%d %B %Y"))                                                
                  unset_date_range(self.request)
                  return
                                
        set_date_range(self.request, start_date, end_date)
        self.request.response.redirect(
            "?portal_status_message=%s" % translate(
                _(u"Date range set.")))

    @form.action(u"Clear")
    def handle_clear(self, action, data):
        unset_date_range(self.request)
        
        self.request.response.redirect(
            "?portal_status_message=%s" % translate(
                _(u"Date range cleared.")))
        
class ArchiveDatesViewlet(object):
    """Viewlet to allow users to choose start- and end-dates to frame
    a search into the archive.

    In effect, parameters ``start_date`` and ``end_date`` will be
    set as a cookie.
    """
    
    render = ViewPageTemplateFile("templates/archive-dates.pt")

    def update(self):
        self.form = ArchiveDatesForm(self.context, self.request)
