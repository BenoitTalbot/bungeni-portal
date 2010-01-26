# encoding: utf-8


import time
import datetime
import tempfile
timedelta = datetime.timedelta

import operator

from sqlalchemy.orm import eagerload
import sqlalchemy.sql.expression as sql

from zope import interface
from zope import component
from zope import schema
from zope.i18n import translate
from zope.formlib import form
from zope.formlib import namedtemplate
from zope.location.interfaces import ILocation
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.security.proxy import removeSecurityProxy
from zope.security.proxy import ProxyFactory
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.file.file import File
from zope.datetime import rfc1123_date
from zope.app.form.browser import MultiCheckBoxWidget as _MultiCheckBoxWidget
from zope.publisher.interfaces.http import IResult, IHTTPRequest
from zope.publisher.http import DirectResult

from bungeni.ui.widgets import SelectDateWidget
from bungeni.ui.calendar import utils
from bungeni.ui.i18n import _
from bungeni.ui.utils import is_ajax_request
from bungeni.ui.utils import get_wf_state
from bungeni.ui.menu import get_actions
from bungeni.ui.forms.common import set_widget_errors
from bungeni.core.location import location_wrapped
from bungeni.core.interfaces import ISchedulingContext
from bungeni.core.schedule import PlenarySchedulingContext
from bungeni.core.odf import OpenDocument
from bungeni.models.queries import get_parliament_by_date_range
from bungeni.models.queries import get_session_by_date_range
from bungeni.models import vocabulary
from bungeni.models import domain
from bungeni.models.utils import getUserId
from bungeni.models.interfaces import IGroupSitting
from bungeni.server.interfaces import ISettings

from ploned.ui.interfaces import IViewView
from ploned.ui.interfaces import IStructuralView
from ore.alchemist.container import stringKey
from ore.alchemist import Session
from ore.workflow.interfaces import IWorkflowInfo

from zc.resourcelibrary import need

from bungeni.core.workflows.groupsitting import states as sitting_wf_state

class TIME_SPAN:
    daily = _(u"Daily")
    weekly = _(u"Weekly")

def get_scheduling_actions(context, request):
    return get_actions("scheduling_actions", context, request)

def get_sitting_actions(context, request):
    return get_actions("sitting_actions", context, request)

def get_discussion_actions(context, request):
    return get_actions("discussion_actions", context, request)

def get_workflow_actions(context, request):
    return get_actions("context_workflow", context, request)

def get_sitting_items(sitting, request, include_actions=False):
    items = []

    if sitting.status in [sitting_wf_state[u'draft-agenda'].id , sitting_wf_state[u'published-agenda'].id]:
        order = "planned_order"
    else:
        order = "real_order"        

    schedulings = map(
        removeSecurityProxy,
        sitting.items.batch(order_by=order, limit=None))

    for scheduling in schedulings:
        item = ProxyFactory(location_wrapped(scheduling.item, sitting))
       
        props = IDCDescriptiveProperties.providedBy(item) and item or \
                IDCDescriptiveProperties(item)

        discussions = tuple(scheduling.discussions.values())
        discussion = discussions and discussions[0] or None

        info = IWorkflowInfo(item, None)
        state_title = info.workflow().workflow.states[item.status].title
        
        record = {
            'title': props.title,
            'description': props.description,
            'name': stringKey(scheduling),
            'status': item.status,
            'type': item.type.capitalize,            
            'state_title': state_title,
            'category_id': scheduling.category_id,
            'category': scheduling.category,
            'discussion': discussion,
            'delete_url': "%s/delete" % absoluteURL(scheduling, request),
            'url': absoluteURL(item, request)}
        
        if include_actions:
            record['actions'] = get_scheduling_actions(scheduling, request)
            record['workflow'] = get_workflow_actions(item, request)

            discussion_actions = get_discussion_actions(discussion, request)
            if discussion_actions:
                assert len(discussion_actions) == 1
                record['discussion_action'] = discussion_actions[0]
            else:
                record['discussion_action'] = None
        items.append(record)
    return items

def create_sittings_map(sittings, request):
    """Returns a dictionary that maps:

      (day, hour) -> {
         'record'   : sitting database record
         'actions'  : actions that apply to this sitting
         'class'    : sitting
         'span'     : span
         }
         
      (day, hour) -> ``None``
      
    If the mapped value is a sitting, then a sitting begins on that
    day and hour, if it's ``None``, then a sitting is reaching into
    this day and hour.
    
    The utility of the returned structure is to aid rendering a
    template with columns spanning several rows.
    """

    mapping = {}
    for sitting in sittings.values():
        day = sitting.start_date.weekday()
        hour = sitting.start_date.hour

        start_date = utils.timedict(
            sitting.start_date.hour,
            sitting.start_date.minute)

        end_date = utils.timedict(
            sitting.end_date.hour,
            sitting.end_date.minute)
        
        status = get_wf_state(sitting)
        
        mapping[day, hour] = {
            'url': "%s/schedule" % absoluteURL(sitting, request),
            'record': sitting,
            'class': u"sitting",
            'actions': get_sitting_actions(sitting, request),
            'span': sitting.end_date.hour - sitting.start_date.hour,
            'formatted_start_time': start_date,
            'formatted_end_time': end_date,
            'status' : status,
        }
        
        # make sure start- and end-date is the same DAY
        assert (sitting.start_date.day == sitting.end_date.day) and \
               (sitting.start_date.month == sitting.end_date.month) and \
               (sitting.start_date.year == sitting.end_date.year)

        for hour in range(sitting.start_date.hour+1, sitting.end_date.hour):
            mapping[day, hour] = None

    return mapping

class CalendarView(BrowserView):
    """Main calendar view."""

    interface.implements(IViewView, IStructuralView)

    template = ViewPageTemplateFile("main.pt")
    ajax = ViewPageTemplateFile("ajax.pt")
    
    _macros = ViewPageTemplateFile("macros.pt")

    short_name = u"Calendar"
    
    def __init__(self, context, request):
        super(CalendarView, self).__init__(
            ISchedulingContext(context), request)
        self.context.__name__ = self.__name__
        self.context.title = self.short_name
        interface.alsoProvides(self.context, ILocation)
        interface.alsoProvides(self.context, IDCDescriptiveProperties)
        self.__parent__ = context

    def __call__(self, timestamp=None):
        if timestamp is None:
            # start the week on the first weekday (e.g. Monday)
            date = utils.datetimedict.fromdate(datetime.date.today())
        else:
            try:
                timestamp = float(timestamp)
            except:
                raise TypeError(
                    "Timestamp must be floating-point (got %s)." % timestamp)
            date = utils.datetimedict.fromtimestamp(timestamp)

        if is_ajax_request(self.request):
            return self.render(date, template=self.ajax)
        return self.render(date)

    def publishTraverse(self, request, name):
        traverser = component.getMultiAdapter(
            (self.context, request), IPublishTraverse)
        return traverser.publishTraverse(request, name)

    def getTitle(self):
        group = self.context.get_group()
        if group is None:
            return u"N/A"
        else:
            if group.type == 'parliament':
                gtype = u'Plenary'
            else:
                gtype = group.type.capitalize()
                                
            return gtype + ': ' + group.short_name + ' - ' + group.full_name            
    
    def reorder_field(self):
        if self.context.status == "draft-agenda":
            return 'planned_order'
        elif self.context.status == "draft-minutes": 
            return 'real_order'            
        else:
            return None
            
    def render(self, date, template=None):
        if template is None:
            template = self.template

        group = self.context.get_group()
        if group is None:
            return template(
                display=None,
                status=_(u"Calendar is not available because "
                         "the scheduling group ($label) is inactive.",
                         mapping={'label': translate(self.context.label).lower()}
                         )
                )

        calendar_url = self.request.getURL()
        date = date - timedelta(days=date.weekday())
        today = utils.datetimedict.fromdate(datetime.date.today())
        days = tuple(date + timedelta(days=d) for d in range(7))

        sittings = self.context.get_sittings(
            start_date=date,
            end_date=days[-1],
            )

        return template(
            display="weekly",
            title=date,
            days=[{
                'formatted': datetime.datetime.strftime(day, '%A %d'),
                'id': datetime.datetime.strftime(day, '%Y-%m-%d'),
                'today': day == today,
                'url': "%s/%d" % (calendar_url, day.totimestamp()),
                } for day in days],
            hours=range(6,21),
            week_no=date.isocalendar()[1],
            links={
                'previous': "%s?timestamp=%s" % (
                    calendar_url, (date - timedelta(days=7)).totimestamp()),
                'next': "%s?timestamp=%s" % (
                    calendar_url, (date + timedelta(days=7)).totimestamp()),
                },
            sittings_map = create_sittings_map(sittings, self.request),
            )

    @property
    def macros(self):
        return self._macros.macros

class CommitteeCalendarView(CalendarView):
    """Calendar-view for a committee."""

class DailyCalendarView(CalendarView):
    """Daily calendar view."""

    interface.implementsOnly(IViewView)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def render(self, today, template=None):
        if template is None:
            template = self.template

        calendar_url = absoluteURL(self.context.__parent__, self.request)
        date = removeSecurityProxy(self.context.date)

        sittings = self.context.get_sittings()

        return template(
            display="daily",
#            title=_(u"$B $Y", mapping=date),
            title = date,
#
            day={
                'formatted': datetime.datetime.strftime(date, '%A %d'),
                'id': datetime.datetime.strftime(date, '%Y-%m-%d'),
                'today': date == today,
                'url': "%s/%d" % (calendar_url, date.totimestamp()),
                },
            hours=range(6,21),
            week_no=date.isocalendar()[1],
            week_day=date.weekday(),
            links={
                'previous': "%s/%d" % (
                    calendar_url, (date - timedelta(days=1)).totimestamp()),
                'next': "%s/%d" % (
                    calendar_url, (date + timedelta(days=1)).totimestamp()),
                },
            sittings_map = create_sittings_map(sittings, self.request),
            )

class GroupSittingScheduleView(CalendarView):
    """Group-sitting scheduling view.

    This view presents a sitting and provides a user interface to
    manage the agenda.
    """

    interface.implementsOnly(IViewView)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def render(self, date, template=None):
        need('yui-editor')
        need('yui-resize')
        
        if template is None:
            template = self.template

        container = self.context.__parent__
        schedule_url = self.request.getURL()
        container_url = absoluteURL(container, self.request)
        
        # determine position in container
        key = stringKey(self.context)
        keys = list(container.keys())
        pos = keys.index(key)

        links = {}
        if pos > 0:
            links['previous'] = "%s/%s/%s" % (
                container_url, keys[pos-1], self.__name__)
        if pos < len(keys) - 1:
            links['next'] = "%s/%s/%s" % (
                container_url, keys[pos+1], self.__name__)

        start_date = utils.datetimedict.fromdatetime(self.context.start_date)
        end_date = utils.datetimedict.fromdatetime(self.context.end_date)
        
        session = Session()
        sitting_type_dc = IDCDescriptiveProperties(self.context.sitting_type)

        site_url = absoluteURL(getSite(), self.request)

        return template(
            display="sitting",
            #title=_(u"$A $e, $B $Y", mapping=start_date),
            title = "%s: %s - %s" % (self.context.group.short_name, 
                self.context.start_date.strftime('%Y-%m-%d %H:%M'), 
                self.context.end_date.strftime('%H:%M')),
            description=_(u"$type &mdash; ${start}-${end}", mapping={
                'type': translate(sitting_type_dc.title),
                'start': self.context.start_date.strftime('%Y-%m-%d %H:%M'), 
                'end': self.context.end_date.strftime('%H:%M')
                }),
#            title = u"",
#            description = u"",
#
            links=links,
            actions=get_sitting_actions(self.context, self.request),
            items=get_sitting_items(
                self.context, self.request, include_actions=True),
            categories=vocabulary.ItemScheduleCategories(self.context),
            new_category_url="%s/admin/categories/add?next_url=..." % site_url,
            )

class SittingCalendarView(CalendarView):
    """Sitting calendar view."""

    interface.implementsOnly(IViewView)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)



def verticalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"verticalMultiCheckBoxWidget"
    widget.orientation='vertical'
    return widget 

def horizontalMultiCheckBoxWidget(field, request):
    vocabulary = field.value_type.vocabulary
    widget = _MultiCheckBoxWidget(field, vocabulary, request)
    widget.cssClass = u"horizontalMultiCheckBoxWidget"
    widget.orientation='horizontal'
    return widget 
    
#def MultiCheckBoxWidgetFactory(field, request):
#            return _MultiCheckBoxWidget(
#                field, field.vocabulary, request)
                
def availableItems(context):
    items = ('Bills',
                'Agenda Items',
                'Motions',
                'Questions',
                'Tabled Documents',
                )
    return SimpleVocabulary.fromValues(items)    
           
def billOptions(context):
    items = ('Title',  
             'Summary', 
             'Text', 
             'Owner',
             'Cosignatories',
            )
    return SimpleVocabulary.fromValues(items)

def agendaOptions(context):
    items = ('Title',   
             'Text', 
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def motionOptions(context):
    items = ('Title',  
             'Number', 
             'Text', 
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def tabledDocumentOptions(context):
    items = ('Title',  
             'Number', 
             'Text', 
             'Owner',
            )
    return SimpleVocabulary.fromValues(items)

def questionOptions(context):
    items = ('Title',  
             'Number', 
             'Text', 
             'Owner',
             'Response',
             'Type',
            )
    return SimpleVocabulary.fromValues(items)

class ReportingView(form.PageForm):
    """Reporting view base class.

    The context of the view is a scheduling context, which always
    relates to a principal group, e.g. 'Plenary'.

    A starting date must be specified, as well as a time span
    parameter, which can be one of the following:

    - Daily
    - Weekly

    The time span parameter is used as title and to generate canonical
    filenames and unique identification strings for publishing the
    reports, e.g.

      'Daily agenda 2009/30/12' (agenda-daily-2009-30-12.pdf)

    It's not enforced that weeks begin on Mondays or any other
    particular day; a week is always 7 days.

    A report is a listing of sittings that take place in the defined
    period. For each sitting, the summary may be different depending
    on the type of report. The ``get_sittings`` method will fetch the
    relevant sittings.
    """

    date = None
    display_minutes = None
    
    def __init__(self, context, request):
        super(ReportingView, self).__init__(context, request)
        
        if IGroupSitting.providedBy(context):
            self.date = datetime.date(
                context.start_date.year,
                context.start_date.month,
                context.start_date.day) 
        '''
        while not ISchedulingContext.providedBy(context):
            context = context.__parent__
            if context is None:
                break;
                #raise RuntimeError(
                #    "No scheduling context found.")
        if context is not None:
            self.scheduling_context = context'''

    class IReportingForm(interface.Interface):
        doc_type = schema.Choice(
                    title = _(u"Document Type"),
                    description = _(u"Type of document to be produced"),
                    values= ['Order of the day',
                             'Proceedings of the day',
                             'Weekly Business',
                             'Questions of the week'],
                    required=True
                    )
        date = schema.Date(
            title=_(u"Date"),
            description=_(u"Choose a starting date for this report."),
            required=True)
        
        #time_span = schema.Choice(
        #    title=_(u"Time span"),
        #    description=_("The time span is used to define the reporting interval "
        #                  "and will provide a name for the report."),
        #    vocabulary=SimpleVocabulary((
        #        SimpleTerm(TIME_SPAN.daily, "daily", TIME_SPAN.daily),
        #        SimpleTerm(TIME_SPAN.weekly, "weekly", TIME_SPAN.weekly),)),
        #    required=True)
        
        item_types = schema.List(title=u'Items to include',
                   required=False,
                   value_type=schema.Choice(
                    vocabulary="Available Items"),
                   )
        bill_options = schema.List( title=u'Bill options',
                       required=False,
                       value_type=schema.Choice(
                       vocabulary='Bill Options'),
                         )
        agenda_options = schema.List( title=u'Agenda options',
                                        required=False,
                                        value_type=schema.Choice(
                                        vocabulary='Agenda Options'),)
        motion_options = schema.List( title=u'Motion options',
                                        required=False,
                                        value_type=schema.Choice(
                                        vocabulary='Motion Options'),)  
        question_options = schema.List( title=u'Question options',
                                          required=False,
                                          value_type=schema.Choice(
                                          vocabulary='Question Options'),)
        tabled_document_options = schema.List( title=u'Tabled Document options',
                                          required=False,
                                          value_type=schema.Choice(
                                          vocabulary='Tabled Document Options'),)
        note = schema.TextLine( title = u'Note',
                                required=False,
                                description=u'Optional note regarding this report'
                        )
        draft = schema.Choice(
                    title = _(u"Include draft items"),
                    description = _(u"Whether or not to include dratf items"),
                    values= ['Yes',
                             'No'],
                    required=True
                    )
    template = namedtemplate.NamedTemplate('alchemist.form')
    form_fields = form.Fields(IReportingForm)
    form_fields['item_types'].custom_widget = horizontalMultiCheckBoxWidget
    form_fields['date'].custom_widget = SelectDateWidget
    form_fields['bill_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['agenda_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['motion_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['question_options'].custom_widget = verticalMultiCheckBoxWidget
    form_fields['tabled_document_options'].custom_widget = verticalMultiCheckBoxWidget
    odf_filename = None
        

    def get_odf_document(self):
        assert self.odf_filename is not None
        settings = component.getUtility(ISettings)
        filename = "%s/%s" % (settings['templates'], self.odf_filename)
        return OpenDocument(filename)

    def setUpWidgets(self, ignore_request=False):
        class context:
            date = self.date or datetime.date.today()
            #time_span = TIME_SPAN.daily
            doc_type = 'Order of the day'
            item_types = 'Bills'
            bill_options = 'Title'
            agenda_options = 'Title'
            question_options = 'Title'
            motion_options = 'Title'
            tabled_document_options = 'Title'
            note = None
            draft = 'No'
        self.adapters = {
            self.IReportingForm: context
            }
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request)

    def update(self):
        self.status = self.request.get('portal_status_message', '')
        super(ReportingView, self).update()
        set_widget_errors(self.widgets, self.errors)

    def validate(self, action, data):    
        errors = super(ReportingView, self).validate(action, data)
        time_span = TIME_SPAN.daily
        if data['doc_type'] == "Order of the day":
            time_span = TIME_SPAN.daily
        elif data['doc_type'] == "Proceedings of the day":
            time_span = TIME_SPAN.daily
        elif data['doc_type'] == "Weekly Business":
            time_span = TIME_SPAN.weekly      
        elif data['doc_type'] == "Questions of the week":
            time_span = TIME_SPAN.weekly          
        
        start_date = data['date']
        end_date = self.get_end_date(start_date, time_span)

        parliament = get_parliament_by_date_range(self, start_date, end_date)
        session = get_session_by_date_range(self, start_date, end_date)

        if parliament is None:
            errors.append(interface.Invalid(
                _(u"A parliament must be active in the period."),
                "date"))
        #elif session is None:
        #    errors.append(interface.Invalid(
        #        _(u"A session must be active in the period."),
        #        "date"))

        return errors
    
    def process_form(self, data):
        self.start_date = data['date']
        time_span = TIME_SPAN.daily 
        self.doc_type = data['doc_type']
        if self.doc_type == "Order of the day":
            time_span = TIME_SPAN.daily
        elif self.doc_type == "Weekly Business":
            time_span = TIME_SPAN.weekly      
        elif self.doc_type == "Questions of the week":
            time_span = TIME_SPAN.weekly     
        elif data['doc_type'] == "Proceedings of the day":
            time_span = TIME_SPAN.daily                 
        self.end_date = self.get_end_date(self.start_date, time_span)
        self.sitting_items = self.get_sittings_items(self.start_date, self.end_date)
        self.item_types = data['item_types']
        self.bill = False
        self.motion = False
        self.agenda = False
        self.question = False
        self.tabled_document = False
        self.bill_options = data['bill_options']
        self.agenda_options = data['agenda_options']
        self.motion_options = data['motion_options']
        self.question_options = data['question_options']
        self.note = data['note']
        self.tabled_document_options = data['tabled_document_options']
        for type in self.item_types:
            if type == 'Bills':
                self.bill_title = False
                self.bill_summary = False
                self.bill_text = False
                self.bill_owner = False
                self.bill_cosignatories = False
                for option in self.bill_options:
                    if option == 'Title':
                        self.bill_title = True
                    elif option == 'Summary':
                        self.bill_summary = True
                    elif option == 'Text':
                        self.bill_text = True
                    elif option == 'Owner':
                        self.bill_owner = True
                    elif option == 'Cosignatories':
                        self.bill_cosignatories = True
                self.bill = True
            elif type == 'Motions':
                self.motion_title = False
                self.motion_number = False
                self.motion_text = False
                self.motion_owner = False
                for option in self.motion_options:
                    if option == 'Title':
                        self.motion_title = True
                    elif option == 'Number':
                        self.motion_number = True
                    elif option == 'Text':
                        self.motion_text = True
                    elif option == 'Owner':
                        self.motion_owner = True
                self.motion = True
            elif type == 'Agenda Items':
                self.agenda_title = False
                self.agenda_text = False
                self.agenda_owner = False
                for option in self.agenda_options:
                    if option == 'Title':
                        self.agenda_title = True
                    elif option == 'Text':
                        self.agenda_text = True
                    elif option == 'Owner':
                        self.agenda_owner = True
                self.agenda = True
            elif type == 'Tabled Documents':
                self.tabled_document_title = False
                self.tabled_document_text = False
                self.tabled_document_owner = False
                self.tabled_document_number = False
                for option in self.tabled_document_options:
                    if option == 'Title':
                        self.tabled_document_title = True
                    elif option == 'Text':
                        self.tabled_document_text = True
                    elif option == 'Owner':
                        self.tabled_document_owner = True
                    elif option == 'Number':
                        self.tabled_document_number = True
                self.tabled_document = True
            elif type == 'Questions':
                self.question_title = False
                self.question_number = False
                self.question_text = False
                self.question_owner = False
                self.question_response = False
                self.question_type = False
                for option in self.question_options:
                    if option == 'Title':
                        self.question_title = True
                    elif option == 'Number':
                        self.question_number = True
                    elif option == 'Text':
                        self.question_text = True
                    elif option == 'Owner':
                        self.question_owner = True
                    elif option == 'Response':
                        self.question_response = True
                    elif option == 'Type':
                        self.question_type = True
                self.question = True    
        
        '''for item in self.sitting_items:
            if item.item_schedule.item.type in item_types:
                opt = item.type + '_option'
                for option in data[opt]:
                    item.options[option] = True
            else:
                self.sitting_items.remove(item) '''
        try:              
            self.group = self.context.get_group()
        except:
            session = Session()
            self.group = session.query(domain.Group).get(self.context.group_id)
        if IGroupSitting.providedBy(self.context):        
            self.back_link = absoluteURL(self.context, self.request)  + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            self.back_link = absoluteURL(self.context, self.request)  
    
        
    @form.action(_(u"Preview"))  
    def handle_preview(self, action, data):                
        self.process_form(data)
        return self.main_result_template()
    
    @form.action(_(u"Save"))
    def handle_save(self, action, data):                
        self.process_form(data)
        body_text = self.result_template()
        session = Session()
        report = domain.Report()
        report.start_date = self.start_date                      
        report.end_date = self.end_date                        
        report.created_date = datetime.datetime.now()   
        report.note = self.note
        if self.display_minutes:                                 
            report.report_type = 'minutes'
        else:
            report.report_type = 'agenda'                    
        report.body_text = body_text
        report.user_id = getUserId()
        report.group_id = self.group.group_id
        session.add(report)
        for sitting in self.sitting_items:
            sr = domain.SittingReport()
            sr.report = report
            sr.sitting = sitting
            session.add(sr)
        session.flush()
        if IGroupSitting.providedBy(self.context):        
            back_link = absoluteURL(self.context, self.request)  + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            back_link = absoluteURL(self.context, self.request)  
        else:   
            raise NotImplementedError                                                                     
        self.request.response.redirect(back_link)    
                 
    #@form.action(_(u"Create and Store"))
    def handle_create_and_store(self, action, data):
        next_url = ('save-report?date=' + data['date'].strftime('%Y-%m-%d') + 
            '&time_span=' + data['time_span'] + '&display_minutes=' +
            str(self.display_minutes))
        self.request.response.redirect(next_url)    

    #@form.action(_(u"Download"))
    def handle_download(self, action, data):
        return self.download_preview(
            data['date'], TIME_SPAN.daily, 'attachment')
            
    def html_preview(self, data):
        file = self.generate(data)
        self.request.response.setHeader('Content-Type', file.contentType)
        self.request.response.setHeader('Content-Length', file.getSize())
        self.request.response.setHeader(
            'Content-Disposition', '%s; filename="%s"' % (
                disposition, file.filename))
        self.request.response.setHeader('Last-Modified', rfc1123_date(time.time()))
        self.request.response.setHeader(
            'Cache-Control', 'no-cache, must-revalidate');
        self.request.response.setHeader('Pragma', 'no-cache')
        return file.data
        
    def download_preview(self, date, time_span, disposition):
        file = self.generate(date, time_span)
        self.request.response.setHeader('Content-Type', file.contentType)
        self.request.response.setHeader('Content-Length', file.getSize())
        self.request.response.setHeader(
            'Content-Disposition', '%s; filename="%s"' % (
                disposition, file.filename))
        self.request.response.setHeader('Last-Modified', rfc1123_date(time.time()))
        self.request.response.setHeader(
            'Cache-Control', 'no-cache, must-revalidate');
        self.request.response.setHeader('Pragma', 'no-cache')
        return file.data

    def generate(self, date, time_span):
        raise NotImplementedError("Must be implemented by subclass.")
    
    '''def get_sittings(self, start_date, time_span):
        end_date = self.get_end_date(start_date, time_span)
        container = self.scheduling_context.get_sittings(
            start_date=start_date, end_date=end_date)
        return container.values()'''

    def get_end_date(self, start_date, time_span):
        if time_span is TIME_SPAN.daily:
            return start_date + timedelta(days=1)
        elif time_span is TIME_SPAN.weekly:
            return start_date + timedelta(weeks=1)
        
        raise RuntimeError("Unknown time span: %s." % time_span)
    
class AgendaReportingView(ReportingView):
    """Agenda report."""
    
    form_name = _(u"Agenda")
    report_name = _(u"ORDER OF THE DAY")
    form_description = _(u"This form generates the agenda report.")
    odf_filename = "agenda.odt"
    display_minutes = False
    main_result_template = ViewPageTemplateFile('main_reports.pt')
    result_template = ViewPageTemplateFile('reports.pt')
    def get_archive(self, date, time_span):
        end_date = self.get_end_date(date, time_span)
        
        parliament = get_parliament_by_date_range(self, date, end_date)
        session = get_session_by_date_range(self, date, end_date)

        options = {
            'title': self.report_name,
            'date': _(u"$x", mapping=utils.datetimedict.fromdate(date)),
            'parliament': parliament,
            'session': session,
            'country': u"Republic of Kenya".upper(),
            'assembly': u"National Assembly".upper(),
         #   'sittings': self.get_sittings(date, time_span),
            'display_minutes': self.display_minutes,
            }

        document = self.get_odf_document()
        archive = tempfile.NamedTemporaryFile(suffix=".odt")
        document.process("content.xml", self, **options)
        document.save(archive.name)

        return archive
    def generate(self, date, time_span):
        archive = self.get_archive(date, time_span)
        file = File(archive, "application/vnd.oasis.opendocument.text")
        file.filename = "agenda-%s-%s-%s-%s.odt" % (
            str(time_span).lower(), date.year, date.month, date.day)
        
        return file
    
    def get_sittings_items(self, start, end):
            """ return the sittings with scheduled items for 
                the given daterange"""    
            session = Session()
            query = session.query(domain.GroupSitting).filter(
                sql.and_(
                    domain.GroupSitting.start_date.between(start,end),
                    domain.GroupSitting.group_id == self.context.group_id)
                    ).order_by(domain.GroupSitting.start_date
                    ).options(
                        eagerload('sitting_type'),
                        eagerload('item_schedule'), 
                        eagerload('item_schedule.item'),
                        eagerload('item_schedule.discussion'),
                        eagerload('item_schedule.category'))
            items = query.all()
        #items.sort(key=operator.attrgetter('start_date'))
            for item in items:
                if self.display_minutes:
                    item.item_schedule.sort(key=operator.attrgetter('real_order'))                              
                else:
                    item.item_schedule.sort(key=operator.attrgetter('planned_order'))  
                    item.sitting_type.sitting_type = item.sitting_type.sitting_type.capitalize() 
                    #s = get_session_by_date_range(self, item.start_date, item.end_date)  
                
            return items
            
class VotesAndProceedingsReportingView(AgendaReportingView):
    form_name = _(u"Votes and proceedings")
    form_description = _(u"This form generates the “votes and proceedings” report.")
    report_name = _(u"VOTES AND PROCEEDINGS")
    display_minutes = True
    
    def generate(self, date, time_span):
        archive = self.get_archive(date, time_span)
        file = File(archive, "application/vnd.oasis.opendocument.text")
        file.filename = "votes-and-proceedings-%s-%s-%s-%s.odt" % (
            str(time_span).lower(), date.year, date.month, date.day)

        return file


class htmlAgendaReportingView(ReportingView):
    """ preview Agenda and votes and proceedings as simple HTML """
    #interface.implements(IViewView)      
    
    def __call__():        
        return self.render() 
        #return (u'<html>\n<head>\n<title>raw</title>\n</head>\n<body>\nThis is a test\n</body>\n</html>')
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
    template = ViewPageTemplateFile('reports.pt')             
    
    def get_sittings_items(self, start, end):
        """ return the sittings with scheduled items for 
        the given daterange"""    
        session = Session()
        query = session.query(domain.GroupSitting).filter(
            sql.and_(
            domain.GroupSitting.start_date.between(start,end),
            domain.GroupSitting.group_id == self.context.group_id)
            ).order_by(domain.GroupSitting.start_date
            ).options(
                eagerload('sitting_type'),
                eagerload('item_schedule'), 
                eagerload('item_schedule.item'),
                eagerload('item_schedule.discussion'),
                eagerload('item_schedule.category'))
        items = query.all()
        #items.sort(key=operator.attrgetter('start_date'))
        for item in items:
            if self.display_minutes:
                item.item_schedule.sort(key=operator.attrgetter('real_order'))                              
            else:
                item.item_schedule.sort(key=operator.attrgetter('planned_order'))  
            item.sitting_type.sitting_type = item.sitting_type.sitting_type.capitalize() 
            #s = get_session_by_date_range(self, item.start_date, item.end_date)  
        return items
                          
    def render(self):
        #date = datetime.datetime.strptime(data['date'],
        #        '%Y-%m-%d').date()
        
        date = self.request.form['date']
        self.doc_type = self.request.form['doc_type']
        #items = self.request.form['items']
        if self.doc_type == "Order of the day":
            time_span = TIME_SPAN.daily
        elif self.doc_type == "Weekly Business":
            time_span = TIME_SPAN.weekly      
        elif self.doc_type == "Questions of the week":
            time_span = TIME_SPAN.weekly          
        end = self.get_end_date(date, time_span)
        self.sitting_items = self.get_sittings_items(date, end)
        ''' self.display_minutes = (data['display_minutes'] == "True")
        if self.display_minutes:
            self.title = _(u"Votes and Proceedings")
        else:
            self.title = _(u"Order of the day")
        try:              
            self.group = self.context.get_group()
        except:
            session = Session()
            self.group = session.query(domain.Group).get(self.context.group_id) '''
       
        if IGroupSitting.providedBy(self.context):        
            self.back_link = absoluteURL(self.context, self.request)  + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            self.back_link = absoluteURL(self.context, self.request)  
        else:   
            raise NotImplementedError
            
class HTMLPreviewPage(ReportingView):
    """ preview Agenda and votes and proceedings as simple HTML """
    template = ViewPageTemplateFile('reports.pt')        
        
    def get_sittings_items(self, start, end):
        """ return the sittings with scheduled items for 
        the given daterange"""    
        session = Session()
        query = session.query(domain.GroupSitting).filter(
            sql.and_(
            domain.GroupSitting.start_date.between(start,end),
            domain.GroupSitting.group_id == self.context.group_id)
            ).order_by(domain.GroupSitting.start_date
            ).options(
                eagerload('sitting_type'),
                eagerload('item_schedule'), 
                eagerload('item_schedule.item'),
                eagerload('item_schedule.discussion'),
                eagerload('item_schedule.category'))
        items = query.all()
        #items.sort(key=operator.attrgetter('start_date'))
        for item in items:
            if self.display_minutes:
                item.item_schedule.sort(key=operator.attrgetter('real_order'))                              
            else:
                item.item_schedule.sort(key=operator.attrgetter('planned_order'))  
            item.sitting_type.sitting_type = item.sitting_type.sitting_type.capitalize() 
            #s = get_session_by_date_range(self, item.start_date, item.end_date)  
        return items
                          
    def update(self):
        date = datetime.datetime.strptime(self.request.form['date'],
                '%Y-%m-%d').date()
        time_span = self.request.form['time_span']
        if time_span == TIME_SPAN.daily:
            time_span = TIME_SPAN.daily
        elif time_span == TIME_SPAN.weekly:
            time_span = TIME_SPAN.weekly                
        end = self.get_end_date(date, time_span)
        self.sitting_items = self.get_sittings_items(date, end)
        self.display_minutes = (self.request.form['display_minutes'] == "True")
        if self.display_minutes:
            self.title = _(u"Votes and Proceedings")
        else:
            self.title = _(u"Order of the day")
        try:              
            self.group = self.context.get_group()
        except:
            session = Session()
            self.group = session.query(domain.Group).get(self.context.group_id)
        if IGroupSitting.providedBy(self.context):        
            self.back_link = absoluteURL(self.context, self.request)  + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            self.back_link = absoluteURL(self.context, self.request)  
        else:   
            raise NotImplementedError                                               
                    
class StoreReportView(HTMLPreviewPage):
    template = ViewPageTemplateFile('save-reports.pt')  
          
    def __call__(self):
        date = datetime.datetime.strptime(self.request.form['date'],
                '%Y-%m-%d').date()
        self.display_minutes = (self.request.form['display_minutes'] == "True")                
        time_span = self.request.form['time_span']
        if time_span == TIME_SPAN.daily:
            time_span = TIME_SPAN.daily
        elif time_span == TIME_SPAN.weekly:
            time_span = TIME_SPAN.weekly            
        end = self.get_end_date(date, time_span)            
        body_text = super(StoreReportView, self).__call__()
        sitting_items = []            
        for sitting in self.sitting_items:
            if self.display_minutes:
                if sitting.status in ["published-minutes"]:
                    sitting_items.append(sitting)
            else:                
                if sitting.status in [ "published-agenda", "draft-minutes", "published-minutes"]:
                    sitting_items.append(sitting)
        if len(sitting_items) == 0:
            referer = self.request.getHeader('HTTP_REFERER')
            if referer:
                referer=referer.split('?')[0]
            else:
                referer = ""                
            self.request.response.redirect(referer + "?portal_status_message=No data found")
            return                     
        self.sitting_items = sitting_items                   
        session = Session()
        report = domain.Report()
        report.start_date = date                      
        report.end_date = end                        
        report.created_date = datetime.datetime.now()   
        if self.display_minutes:                                 
            report.report_type = 'minutes'
        else:
            report.report_type = 'agenda'                    
        report.body_text = body_text
        report.user_id = getUserId()
        report.group_id = self.group.group_id
        session.add(report)
        for sitting in self.sitting_items:
            sr = domain.SittingReport()
            sr.report = report
            sr.sitting = sitting
            session.add(sr)
        session.flush()
        if IGroupSitting.providedBy(self.context):        
            back_link = absoluteURL(self.context, self.request)  + '/schedule'
        elif ISchedulingContext.providedBy(self.context):
            back_link = absoluteURL(self.context, self.request)  
        else:   
            raise NotImplementedError                                                                     
        self.request.response.redirect(back_link)
