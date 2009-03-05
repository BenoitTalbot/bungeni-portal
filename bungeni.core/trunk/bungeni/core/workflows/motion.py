# encoding: utf-8

from zope import component
from bungeni.core.workflows.notification import Notification
from bungeni.core.workflows import interfaces
from bungeni.core import globalsettings as prefs
from bungeni.core.i18n import _
import zope.securitypolicy.interfaces
import bungeni.core.workflows.utils as utils

class actions:
    @staticmethod
    def denyAllWrites(motion):
        """
        remove all rights to change the question from all involved roles
        """
    #    rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Owner' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Speaker' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.MP' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.delete', u'bungeni.Owner' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.delete', u'bungeni.Clerk' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.delete', u'bungeni.Speaker' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.delete', u'bungeni.MP' )    

    @staticmethod
    def postpone(info,context):
        utils.setMotionHistory(info,context)

    @staticmethod
    def create( info, context ):
        user_id = utils.getUserId()
        if not user_id:
            user_id ='-'
        zope.securitypolicy.interfaces.IPrincipalRoleMap( context ).assignRoleToPrincipal( u'bungeni.Owner', user_id)   
        utils.setParliamentId(info, context)

    @staticmethod
    def submit( info, context ):
        utils.setSubmissionDate(info, context)
    #    motion = removeSecurityProxy(context)
    #    rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
    #    rpm.grantPermissionToRole( 'bungeni.motion.view', u'bungeni.Clerk' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Owner' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.delete', u'bungeni.Owner' )

    @staticmethod
    def recieved_by_clerk( info, context ):
        utils.createVersion(info, context)   
    #    motion = removeSecurityProxy(context)     
    #    zope.securitypolicy.interfaces.IRolePermissionMap( motion ).grantPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )

    @staticmethod
    def require_edit_by_mp( info, context ):
        utils.createVersion(info,context)
    #    motion = removeSecurityProxy(context)
    #    rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
    #    rpm.grantPermissionToRole( 'bungeni.motion.edit', u'bungeni.Owner' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )   

    @staticmethod
    def complete( info, context ):
        utils.createVersion(info,context)
    #    motion = removeSecurityProxy(context)
    #    rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
    #    rpm.grantPermissionToRole( 'bungeni.motion.view', u'bungeni.Speaker' )
    #    rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )     

    @staticmethod
    def approve( info, context ):
        #motion = removeSecurityProxy(context)
        #rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )    
        #rpm.grantPermissionToRole( 'bungeni.motion.edit', u'bungeni.Speaker' )
        #rpm.grantPermissionToRole( 'zope.View', u'zope.Anybody')
        #rpm.grantPermissionToRole( 'bungeni.motion.view', u'zope.Everybody')
        utils.setApprovalDate(info,context)

    @staticmethod
    def reject( info, context ):
        #motion = removeSecurityProxy(context)
        #denyAllWrites(motion)
        pass

    @staticmethod
    def require_amendment( info, context ):
        utils.createVersion(info,context)
        #motion = removeSecurityProxy(context)
        #rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
        #rpm.grantPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )
        #rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Speaker' ) 

    @staticmethod
    def complete_clarify( info, context ):
        utils.createVersion(info,context)
        #motion = removeSecurityProxy(context)
        #rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
        #rpm.grantPermissionToRole( 'bungeni.motion.view', u'bungeni.Speaker' )
        #rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' ) 

    @staticmethod
    def mp_clarify( info, context ):
        utils.createVersion(info,context)
        #motion = removeSecurityProxy(context)
        #rpm = zope.securitypolicy.interfaces.IRolePermissionMap( motion )
        #rpm.grantPermissionToRole( 'bungeni.motion.edit', u'bungeni.Owner' )
        #rpm.denyPermissionToRole( 'bungeni.motion.edit', u'bungeni.Clerk' )   

    @staticmethod
    def schedule( info, context ):
        pass

    @staticmethod
    def defer( info, context):
        pass

    @staticmethod
    def elapse( info, context ):
        pass

    @staticmethod
    def schedule( info, context ):
        pass

    @staticmethod
    def debate( info, context ):
        pass

    @staticmethod
    def withdraw( info, context ):
        #motion = removeSecurityProxy(context)
        #denyAllWrites(motion)    
        pass

class SendNotificationToMemberUponReceipt(Notification):
    component.adapts(interfaces.IMotionReceivedEvent)

    body = _('notification_email_to_member_upon_receipt_of_motion',
             default="Motion received.")
    
    @property
    def subject(self):
        return u'Motion received: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification

    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()
    
class SendNotificationToClerkUponSubmit(Notification):
    """Send notification to Clerk's office upon submit.

    We need to settings from a global registry to determine whether to
    send this notification and where to send it to.
    """

    component.adapts(interfaces.IMotionSubmittedEvent)

    body = _('notification_email_to_clerk_upon_submit_of_motion',
             default="Motion submitted.")

    @property
    def subject(self):
        return u'Motion submitted: %s' % self.context.title

    @property
    def condition(self):
        return prefs.getClerksOfficeRecieveNotification()
    
    @property
    def recipient_address(self):
        return prefs.getClerksOfficeEmail()

class SendNotificationToMemberUponReject(Notification):
    """Issued when a motion was rejected by the speakers office.
    Sends a notice that the Motion was rejected"""

    component.adapts(interfaces.IMotionRejectedEvent)

    body = _('notification_email_to_member_upon_rejection_of_motion',
             default="Motion rejected.")

    @property
    def subject(self):
        return u'Motion rejected: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getSpeakersOfficeEmail()

class SendNotificationToMemberUponNeedsClarification(Notification):
    """Issued when a motion needs clarification by the MP
    sends a notice that the motion needs clarification"""

    component.adapts(interfaces.IMotionClarifyEvent)

    body = _('notification_email_to_member_upon_need_clarification_of_motion',
             default="Your motion needs to be clarified.")

    @property
    def subject(self):
        return u'Motion needs clarification: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()

class SendNotificationToMemberUponDeferred(Notification):
    """Issued when a motion was deferred by Clerk's office."""

    component.adapts(interfaces.IMotionDeferredEvent)

    body = _('notification_email_to_member_upon_defer_of_motion',
             default="Motion deferred.")

    @property
    def subject(self):
        return u'Motion deferred: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getSpeakersOfficeEmail()

class SendNotificationToMemberUponSchedule(Notification):
    """Issued when a motion was scheduled by Speakers office.
    Sends a Notice that the motion is scheduled for ... """

    component.adapts(interfaces.IMotionScheduledEvent)

    body = _('notification_email_to_member_upon_schedule_of_motion',
             default="Motion scheduled.")

    @property
    def subject(self):
        return u'Motion scheduled: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()

class SendNotificationToMemberUponPostponed(Notification):
    """Issued when a motion was postponed by the speakers office.
    sends a notice that the motion could not be debated and was postponed"""

    component.adapts(interfaces.IMotionPostponedEvent)

    body = _('notification_email_to_member_upon_postpone_of_motion',
             default="Motion postponed.")

    @property
    def subject(self):
        return u'Motion postponed: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()

class SendNotificationToMemberUponDebated(Notification):
    """Issued when a motion was debated."""

    component.adapts(interfaces.IMotionDebatedEvent)

    body = _('notification_email_to_member_upon_debate_of_motion',
             default=u"Motion was debated.")
    @property
    def subject(self):
        return u'Motion was debated: %s' % self.context.title

    @property
    def condition(self):
        return self.context.receive_notification
    
    @property
    def from_address(self):
        return prefs.getClerksOfficeEmail()

