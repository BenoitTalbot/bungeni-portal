import time

from zope import interface
from zope import component

from bungeni.core.interfaces import ISchedulingContext
from bungeni.core.globalsettings import getCurrentParliamentId
from bungeni.models.interfaces import IBungeniApplication
from bungeni.models.domain import GroupSitting
from bungeni.models.domain import Group

from ore.alchemist import Session
from ore.alchemist.container import stringKey

def format_date(date):
    return time.strftime("%Y-%m-%d %H:%M:%S", date.timetuple())
                  
class PrincipalGroupSchedulingContext(object):
    interface.implements(ISchedulingContext)

    group_id = None

    def __init__(self, context):
        self.__parent__ = context

    def get_group(self, name="group"):
        session = Session()

        group = session.query(Group).filter_by(
            group_id=self.group_id)[0]

        group.__name__ = name
        group.__parent__ = self

        return group

    def get_sittings(self, start_date=None, end_date=None):
        session = Session()

        if start_date is None and end_date is None:
            sesions = session.query(GroupSitting).filter_by(
                group_id=self.group_id)

        else:
            assert start_date and end_date

            query = session.query(GroupSitting).filter(
                "group_id=:group_id and start_date>:start_date and end_date<:end_date")

            sittings = query.params(
                group_id=self.group_id,
                start_date=format_date(start_date),
                end_date=format_date(end_date))

        sittings = tuple(sittings)
        
        for sitting in sittings:
            sitting.__name__ = stringKey(sitting)
            sitting.__parent__ = self.get_group().sittings

        return sittings
    
class PlenarySchedulingContext(PrincipalGroupSchedulingContext):
    component.adapts(IBungeniApplication)

    @property
    def group_id(self):
        """Return current parliament's group id."""

        return getCurrentParliamentId()
        
