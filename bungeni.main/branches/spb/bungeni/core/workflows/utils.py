log = __import__("logging").getLogger("bungeni.core.workflows.utils")

import sys
import datetime

from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalRoleMap

from ore.workflow.interfaces import IWorkflowInfo
from ore.workflow.interfaces import NoTransitionAvailableError

import bungeni.models.interfaces as interfaces
#import bungeni.models.domain as domain
from bungeni.models.utils import get_principal_id
from bungeni.core.app import BungeniApp
import bungeni.core.interfaces
import bungeni.core.globalsettings as prefs
from bungeni.ui.utils import debug

import dbutils


''' !+UNUSED(mr, mar-2011)
def get_parliament(context):
    """go up until we find a parliament """
    parent = context.__parent__
    while parent:
        if  interfaces.IParliament.providedBy(parent):
            return parent
        else:
            try:
                parent = parent.__parent__
            except:
                parent = None
    if not parent:
        parliament_id = context.parliament_id
        session = Session()
        parliament = session.query(domain.Parliament).get(parliament_id)
        return parliament
'''

# !+WorkflowInfo(mr, mar-2011) drop passing "info" (unused) param everywhere,
# here and in actions, conditions?

# parliamentary item

def get_owner_login_pi(context):
    """Get the login of the user who has been previously set as the owner of 
    this ParliamentaryItem.
    """
    assert interfaces.IBungeniContent.providedBy(context), \
        "Not a Parliamentary Item: %s" % (context)
    return dbutils.get_user_login(context.owner_id)

def assign_owner_role(context, login):
    # throws IntegrityError when login is None
    IPrincipalRoleMap(context).assignRoleToPrincipal("bungeni.Owner", login)

def assign_owner_role_pi(context):
    """Assign bungeni.Owner role to the ParliamentaryItem.
    """
    current_user_login = get_principal_id()
    owner_login = get_owner_login_pi(context)
    log.debug("assign_owner_role_pi [%s] user:%s owner:%s" % (
        context, current_user_login, owner_login))
    if current_user_login:
        assign_owner_role(context, current_user_login)
    if owner_login and (owner_login != current_user_login):
        assign_owner_role(context, owner_login)

def create_version(info, context):
    """Create a new version of an object and return it."""
    instance = removeSecurityProxy(context)
    # capi.template_message_version_transition
    message_template = "New version on workflow transition from: %(status)s"
    message = message_template % instance.__dict__
    versions = bungeni.core.interfaces.IVersioned(instance)
    versions.create(message)


def set_pi_registry_number(info, context):
    """A parliamentary_item's registry_number should be set on the item being 
    submitted to parliament.
    """
    instance = removeSecurityProxy(context)
    if instance.registry_number == None:
        dbutils.set_pi_registry_number(instance)


# question
def setMinistrySubmissionDate(info, context):
    instance = removeSecurityProxy(context)
    if instance.ministry_submit_date == None:
        instance.ministry_submit_date = datetime.date.today()

# !+QuestionScheduleHistory(mr, mar-2011) rename appropriately e.g. "unschedule"
# !+QuestionScheduleHistory(mr, mar-2011) only pertinent if question is 
# transiting from a shceduled state... is this needed anyway?
def setQuestionScheduleHistory(info, context):
    question_id = context.question_id
    dbutils.removeQuestionFromItemSchedule(question_id)

''' !+UNUSUED (and incorrect) :
def getQuestionSchedule(info, context):
    question_id = context.question_id
    return dbutils.isItemScheduled(question_id)

def getMotionSchedule(info, context):
    motion_id = context.motion_id
    return dbutils.isItemScheduled(motion_id)

def getQuestionSubmissionAllowed(info, context):
    return prefs.getQuestionSubmissionAllowed()
'''

# bill
def setBillPublicationDate(info, context):
    instance = removeSecurityProxy(context)
    if instance.publication_date == None:
        instance.publication_date = datetime.date.today()

# question, motion, bill, agendaitem, tableddocument
# !+ParliamentID(mr, mar-2011) this is used in "create" transitions... 
# why is this needed here (as part fo transition logic... 
# should be part of the object creation logic?
def setParliamentId(info, context):
    instance = removeSecurityProxy(context)
    if not instance.parliament_id:
         instance.parliament_id = prefs.getCurrentParliamentId()

# tableddocument
def setTabledDocumentHistory(info, context):
    pass

# groups
def _set_group_local_role(context, unset=False):
    def get_group_local_role(group):
        if interfaces.IParliament.providedBy(group):
            return "bungeni.MP"
        elif interfaces.IMinistry.providedBy(group):
            return "bungeni.Minister"
        elif interfaces.ICommittee.providedBy(group): 
            return "bungeni.CommitteeMember"
        elif interfaces.IPoliticalGroup.providedBy(group):
            return "bungeni.PartyMember"
        elif interfaces.IGovernment.providedBy(group):
            return "bungeni.Government"
        elif interfaces.IOffice.providedBy(group):
            return group.office_role
        else:
            return "bungeni.GroupMember"
    def get_group_context(context):
        if interfaces.IOffice.providedBy(context):
            return BungeniApp() #get_parliament(context)
        else:
            return removeSecurityProxy(context)
    role = get_group_local_role(context)
    group = removeSecurityProxy(context)
    ctx = get_group_context(context)
    prm = IPrincipalRoleMap(ctx)
    if not unset:
        prm.assignRoleToPrincipal(role, group.group_principal_id)
    else:
        prm.unsetRoleForPrincipal(role, group.group_principal_id)
        
def set_group_local_role(context):
    _set_group_local_role(context, unset=False)
            
def unset_group_local_role(context):
    _set_group_local_role(context, unset=True)

def dissolveChildGroups(groups, context):
    for group in groups:
        IWorkflowInfo(group).fireTransition("active-dissolved", 
            check_security=False)
        
# groupsitting
def schedule_sitting_items(info, context):
    
    # !+fireTransitionToward(mr, dec-2010) sequence of fireTransitionToward 
    # calls was introduced in r5818, 28-jan-2010 -- here the code is reworked
    # to be somewhat more sane, and added logging of both SUCCESS and of 
    # FAILURE of each call to fireTransitionToward().
    #
    # The check/logging should be removed once it is understood whether
    # NoTransitionAvailableError is *always* raised (i.e. fireTransitionToward is
    # broken) or it is indeed raised correctly when it should be.
    
    def fireTransitionScheduled(item, check_security=False):
        try:
            IWorkflowInfo(item).fireTransitionToward("scheduled", 
                    check_security=False)
            raise RuntimeWarning(
                """It has WORKED !!! fireTransitionToward("scheduled")""")
        except (NoTransitionAvailableError, RuntimeWarning):
            debug.log_exc_info(sys.exc_info(), log.error)
    
    for schedule in removeSecurityProxy(context).item_schedule:
        item = schedule.item
        if interfaces.IQuestion.providedBy(item):
            fireTransitionScheduled(item)
        elif interfaces.IMotion.providedBy(item):
            fireTransitionScheduled(item)
        elif interfaces.IAgendaItem.providedBy(item):
            fireTransitionScheduled(item)
        elif interfaces.ITabledDocument.providedBy(item):
            fireTransitionScheduled(item)


