from datetime import datetime
from datetime import timedelta

from zope import interface
from zope import component
from zope import schema

from zope.location.interfaces import ILocation
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile

from zc.resourcelibrary import need

from bungeni.core.interfaces import ISchedulingContext
from bungeni.ui.calendar import utils
from bungeni.ui.proxy import ShortNameProxy
from bungeni.ui.i18n import _

def create_sittings_map(sittings):
    """Returns a dictionary that maps:

      (day, hour) -> {
         record  : sitting database record,
         span    : span
         }
         
      (day, hour) -> ``None``

    If the mapped value is a sitting, then a sitting begins on that
    day and hour, if it's ``None``, then a sitting is reaching into
    this day and hour.

    The utility of the returned structure is to aid rendering a
    template with columns spanning several rows.
    """

    mapping = {}
    for sitting in sittings:
        day = sitting.start_date.weekday()
        hour = sitting.start_date.hour
        mapping[day, hour] = {
            'record': sitting,
            'span': sitting.end_date.hour - sitting.start_date.hour
            }

        # make sure start- and end-date is the same year
        assert (sitting.start_date.day == sitting.end_date.day) and \
               (sitting.start_date.month == sitting.end_date.month) and \
               (sitting.start_date.year == sitting.end_date.year)

        for hour in range(sitting.start_date.hour+1, sitting.end_date.hour):
            mapping[day, hour] = None

    return mapping

class CalendarView(BrowserView):
    """Main calendar view."""

    template = ViewPageTemplateFile("main.pt")
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
            date = utils.datetimedict.now()
        else:
            try:
                timestamp = float(timestamp)
            except:
                raise TypeError(
                    "Timestamp must be floating-point (got %s)." % timestamp)
            date = utils.datetimedict.fromtimestamp(timestamp)

        return self.render_weekly(date)

    def publishTraverse(self, request, name):
        try:
            method = getattr(self, 'get_%s' % name)
        except AttributeError:
            return super(CalendarView, self).publishTraverse(request, name)

        obj = method()
        obj.__name__ = name
        return obj
        
    def get_sittings(self):
        group = self.context.get_group()
        group.__name__ = self.__name__
        group.__parent__ = self.__parent__
        group = ShortNameProxy(group, short_name=self.short_name)

        container = self.context.get_sittings_container()
        container.__parent__ = group

        return container

    def render_add_sitting_form(self):
        
        view = component.getMultiAdapter(
            (sittings, self.request), name="add")
        return view()

    def render_weekly(self, date):
        calendar_url = self.request.getURL()
        date = date - timedelta(days=date.weekday())
        days = tuple(date + timedelta(days=d) for d in range(7))

        sittings = self.context.get_sittings(
            start_date=date,
            end_date=days[-1],
            )
        
        return self.template(
            display="weekly",
            formatted_date=_(
                u"Showing the week starting on $m/$d-$g @ $r.",
                mapping=date),
            formatted_month=_(u"$B", mapping=date),
            days=[{
                'formatted': datetime.strftime(day, '%A %d'),
                'id': datetime.strftime(day, '%Y-%m-%d'),
                } for day in days],
            hours=range(7,21),
            week_no=date.isocalendar()[1],
            links={
                'previous_week': "%s?timestamp=%s" % (
                    calendar_url, (date - timedelta(days=7)).totimestamp()),
                'next_week': "%s?timestamp=%s" % (
                    calendar_url, (date + timedelta(days=7)).totimestamp()),

                # note that giving a date -28 or +32 days in the future
                # will work, because we always start the calendar on a
                # fixed day of the week
                'previous_month': "%s?timestamp=%s" % (
                    calendar_url, (date - timedelta(days=28)).totimestamp()),
                'next_month': "%s?timestamp=%s" % (
                    calendar_url, (date + timedelta(days=32)).totimestamp()),
                },
            sittings_map = create_sittings_map(sittings),
            )

    @property
    def macros(self):
        return self._macros.macros
