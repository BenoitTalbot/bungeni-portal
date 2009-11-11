#!/usr/bin/env python
# encoding: utf-8
"""
domain.py

Created by Kapil Thangavelu on 2007-11-22.

"""

import md5, random, string

from zope import interface, location, component
from ore.alchemist import model, Session
from alchemist.traversal.managed import one2many
from zope.location.interfaces import ILocation

import files
import logging
import interfaces

logger = logging.getLogger('bungeni.models')



#####

def object_hierarchy_type( object ):
    if isinstance( object, User ):
        return "user"
    if isinstance( object, Group ):
        return "group"
    if isinstance( object, ParliamentaryItem ):
        return "item"
    return ""


class Entity( object ):

    interface.implements( location.ILocation )

    __name__ = None
    __parent__ = None
    
    def __init__( self, **kw ):
        try:
            domain_schema = model.queryModelInterface( self.__class__ )
            known_names = [k for k,d in domain_schema.namesAndDescriptions(1)]
        except:
            known_names = None

        for k,v in kw.items():
            if known_names is None or k in known_names:
                setattr( self, k, v)
            else:
                logger.warn(
                    "Invalid attribute on %s %s" % (
                        self.__class__.__name__, k))

# sort_on is the column the query is sorted on by default
# sort_replace is a dictionary that maps one column to another
# so when the key is requested in a sort the value gets sorted
# eg: {'user_id':'sort_name'} when the sort on user_id is requested the 
# query gets sorted by sort_name
#
                
class User( Entity ):
    """Domain Object For A User.
    General representation of a person
    """
    
    interface.implements( interfaces.IBungeniUser  )
    
    def __init__( self,  login=None, **kw ):
        if login:
            self.login = login
        super( User, self ).__init__( **kw )
        self.salt = self._makeSalt()
    
    def _makeSalt( self ):
        return ''.join( random.sample( string.letters[:52], 12) )
        
    def setPassword( self, password ):
        self.password = self.encode( password )
        
    def encode( self, password ):
        return md5.md5( password + self.salt ).hexdigest()
        
    def checkPassword( self, password_attempt ):
        attempt = self.encode( password_attempt )
        return attempt == self.password

    @property
    def fullname(self):
        return "%s %s" % (self.first_name, self.last_name)

    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name']}    
    addresses = one2many( "addresses", "bungeni.models.domain.UserAddressContainer", "user_id" )    
    delegations = one2many( "delegations", "bungeni.models.domain.UserDelegationContainer", "user_id" )   


class UserDelegation(Entity):
    """ Delgate rights to act on behalf of a user 
    to another user """
    
  
#class HansardReporter( User ):
#    """ a reporter who reports on parliamentary procedings
#    """
 
    # rotas

    # takes
    
######    

class Group( Entity ):
    """ an abstract collection of users
    """
    interface.implements( interfaces.IBungeniGroup )

    users = one2many("users", "bungeni.models.domain.GroupMembershipContainer", "group_id")
    #sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")
    
    
class GroupMembership( Entity ):
    """ a user's membership in a group- abstract
    basis for ministers, committeemembers, etc
    """
    interface.implements( interfaces.IBungeniGroupMembership )
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name']}  

    @property
    def image(self):
        return self.user.image

class OfficesHeld( Entity ):
    """ Offices held by this group member """
    

class StaffGroupMembership( GroupMembership ):
    """ 
    staff assigned to groups (committees, ministries,...)
    """    
            
class CommitteeStaff( StaffGroupMembership ):
    """
    Comittee Staff
    """
    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )    
        
class GroupSitting( Entity ):
    """Scheduled meeting for a group (parliament, committee, etc)"""
    
    attendance = one2many(
        "attendance", "bungeni.models.domain.GroupSittingAttendanceContainer", "sitting_id" )

    items = one2many(
        "items", "bungeni.models.domain.ItemScheduleContainer", "sitting_id")

    @property
    def short_name( self ):
        return ( self.start_date ).strftime('%d %b %y %H:%M')
    
    
    
    
class SittingType(object):
    """ Type of sitting
    morning/afternoon/... """    
    
class GroupSittingAttendance( object ):
    """ a record of attendance at a meeting 
    """
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name',]}  
    
class AttendanceType( object ):
    """
    lookup for attendance type
    """    
    
class GroupItemAssignment( object ):
    """ the assignment of a parliamentary content object to a group
    """

class GroupGroupItemAssignment( GroupItemAssignment):
    """ assign a group to an item """

class ItemGroupItemAssignment( GroupItemAssignment ):
    """ assign an item to a group """


#############

    
class Parliament( Group ):
    """ a parliament
    """    
    sort_on = ['start_date']
    sessions = one2many("sessions", "bungeni.models.domain.ParliamentSessionContainer", "parliament_id")
    committees = one2many("committees", "bungeni.models.domain.CommitteeContainer", "parent_group_id")
    governments = one2many("governments","bungeni.models.domain.GovernmentContainer", "parent_group_id")
    parliamentmembers = one2many("parliamentmembers", 
                                 "bungeni.models.domain.MemberOfParliamentContainer", "group_id")
    #extensionmembers = one2many("extensionmembers", "bungeni.models.domain.ExtensionGroupContainer",
    #                             "parliament_id")
    politicalparties = one2many("politicalparties", "bungeni.models.domain.PoliticalPartyContainer", "parent_group_id")
    bills = one2many("bills", "bungeni.models.domain.BillContainer", "parliament_id")
    questions = one2many("questions", "bungeni.models.domain.QuestionContainer", "parliament_id")
    motions = one2many("motions", "bungeni.models.domain.MotionContainer", "parliament_id")  
    sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")       
    offices = one2many("offices", "bungeni.models.domain.OfficeContainer", "parent_group_id")   
    agendaitems = one2many("agendaitems", "bungeni.models.domain.AgendaItemContainer", "group_id")
    tableddocuments = one2many("tableddocuments", "bungeni.models.domain.TabledDocumentContainer", "parliament_id")

class MemberOfParliament ( GroupMembership ):    
    """
    defined by groupmembership and aditional data
    """    
    sort_on = ['last_name', 'first_name', 'middle_name']
    sort_replace = {'user_id': ['last_name', 'first_name'], 'constituency_id':['name']}      
    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )


class PoliticalParty( Group ):
    """ a political party
    """
    partymembers = one2many("partymembers","bungeni.models.domain.PartyMemberContainer", "group_id")
    

class PartyMember( GroupMembership ):
    """ 
    Member of a political party, defined by its group membership 
    """
    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )   
    


class Government( Group ):
    """ a government
    """
    sort_on = ['start_date']
    ministries = one2many("ministries", "bungeni.models.domain.MinistryContainer", "parent_group_id")
    

class Ministry( Group ):
    """ a government ministry
    """
    ministers = one2many("ministers","bungeni.models.domain.MinisterContainer", "group_id")
    questions = one2many("questions", "bungeni.models.domain.QuestionContainer", "ministry_id")
    bills = one2many("bills", "bungeni.models.domain.BillContainer", "ministry_id")    
         
    
class Minister( GroupMembership ):
    """ A Minister
    defined by its user_group_membership in a ministry (group)
    """    
    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )
    
class Committee( Group ):
    """ a parliamentary committee of MPs
    """        
    committeemembers = one2many("committeemembers", "bungeni.models.domain.CommitteeMemberContainer", "group_id")
    committeestaff = one2many("committeestaff", "bungeni.models.domain.CommitteeStaffContainer", "group_id")
    agendaitems = one2many("agendaitems", "bungeni.models.domain.AgendaItemContainer", "group_id")
    sittings = one2many("sittings", "bungeni.models.domain.GroupSittingContainer", "group_id")           
    sort_replace = {'committee_type_id': ['committee_type',]}  
    assigneditems = one2many("assigneditems", "bungeni.models.domain.ItemGroupItemAssignmentContainer", "group_id")               
    


class CommitteeMember( GroupMembership ):
    """ A Member of a committee
    defined by its membership to a committee (group)""" 

    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )  
    
class CommitteeType( object):
    """ Type of Committee """
        
        
class Office( Group ):
    """ parliamentary Office like speakers office,
    clerks office etc. internal only"""
    officemembers = one2many("officemembers", "bungeni.models.domain.OfficeMemberContainer", "group_id") 


        
class OfficeMember( GroupMembership ):
    """ clerks, .... """        
    titles = one2many( "titles", "bungeni.models.domain.MemberRoleTitleContainer", "membership_id" )    
            

   
#class Debate( Entity ):
#    """
#    Debates
#    """   

class AddressType( object ):
    """
    Address Types
    """

class UserAddress( Entity ):    
    """
    addresses of a user
    """
    
        
#############

class ItemLog( object ):
    """ an audit log of events in the lifecycle of a parliamentary content
    """
    @classmethod
    def makeLogFactory( klass, name ):
        factory = type( name, (klass,), {} )
        interface.classImplements(factory, interfaces.IChange) 
        return factory

class ItemVersions( Entity ):
    """a collection of the versions of a parliamentary content object
    """
    @classmethod
    def makeVersionFactory( klass, name ):
        factory = type( name, (klass,), {} )    
        interface.classImplements( factory, interfaces.IVersion, 
            interfaces.IBranchFileAttachments,  )
        return factory
            
    files = files.DirectoryDescriptor()
       
            
        
        
class ItemVotes( object ):
    """
    """
    
class ParliamentaryItem( Entity ):
    """
    """
    interface.implements( interfaces.IBungeniContent )
    sort_replace = {'owner_id': ['last_name', 'first_name']}  
       
    # votes

    # schedule

    # object log

    # versions



#ParliamentaryItemChange = ItemLog.makeLogFactory( "ParliamentaryItemChange")
#ParliamentaryItemVersions = ItemVersions.makeVersionFactory("ParliamentaryItemVersion")

class AgendaItem( ParliamentaryItem ):    
    """
    Generic Agenda Item that can be scheduled on a sitting
    """
    #interface.implements( interfaces.IAgendaItem )
    versions = one2many(
        "versions",
        "bungeni.models.domain.AgendaItemVersionContainer",
        "content_id")    
AgendaItemChange = ItemLog.makeLogFactory( "AgendaItemChange")
AgendaItemVersion = ItemVersions.makeVersionFactory("AgendaItemVersion")


class Question( ParliamentaryItem ):
    interface.implements( interfaces.IQuestion, interfaces.IHeadFileAttachments )
    responses = one2many("responses", "bungeni.models.domain.ResponseContainer", "response_id")
    supplementaryquestions = one2many("supplementaryquestions", "bungeni.models.domain.QuestionContainer", "supplement_parent_id")
    files = files.DirectoryDescriptor()
    versions = one2many(
        "versions",
        "bungeni.models.domain.QuestionVersionContainer",
        "content_id")
    sort_on = ['question_number','submission_date']
    sort_dir = 'desc'
    
    
    def getParentQuestion( self ):
        if self.supplement_parent_id:
            session = Session()
            parent = session.query(Question).get(self.supplement_parent_id)   
            return parent.subject

            
 

QuestionChange = ItemLog.makeLogFactory( "QuestionChange")
QuestionVersion = ItemVersions.makeVersionFactory("QuestionVersion")


class Response( ParliamentaryItem ):
    """
    Response to a Question
    """
    interface.implements( interfaces.IResponse, interfaces.IHeadFileAttachments )
    files = files.DirectoryDescriptor()
    versions = one2many(
        "versions",
        "bungeni.models.domain.ResponseVersionContainer",
        "content_id")
    
ResponseChange = ItemLog.makeLogFactory( "ResponseChange")
ResponseVersion = ItemVersions.makeVersionFactory("ResponseVersion")   

class Motion( ParliamentaryItem ):
    interface.implements( interfaces.IMotion, interfaces.IHeadFileAttachments )  
    files = files.DirectoryDescriptor()      
    motionamendment = one2many("motionamendment", "bungeni.models.domain.MotionAmendmentContainer", "motion_id")
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")

    versions = one2many(
        "versions",
        "bungeni.models.domain.MotionVersionContainer",
        "content_id")
      
    sort_on = ['motion_number','submission_date']
    sort_dir = 'desc'
    
MotionChange = ItemLog.makeLogFactory( "MotionChange")
MotionVersion = ItemVersions.makeVersionFactory("MotionVersion")

class MotionAmendment( Entity ):
    """
    Amendment to a Motion
    """
    @property
    def short_name( self ):
        return ( self.title )     

class BillType(object):
    """
    type of bill: public/ private, ....
    """

class Bill( ParliamentaryItem ):
    interface.implements( interfaces.IBill, interfaces.IHeadFileAttachments )
    files = files.DirectoryDescriptor()
    
    consignatory = one2many("consignatory", "bungeni.models.domain.ConsignatoryContainer", "item_id")
    event = one2many("event", "bungeni.models.domain.EventItemContainer", "item_id" )
    assigneditems = one2many("assigneditems", "bungeni.models.domain.GroupGroupItemAssignmentContainer", "object_id")               

    versions = one2many(
        "versions",
        "bungeni.models.domain.BillVersionContainer",
        "content_id")
    sort_on = ['submission_date']
    sort_dir = 'desc'
        
BillChange = ItemLog.makeLogFactory( "BillChange")
BillVersion = ItemVersions.makeVersionFactory("BillVersion")


class Consignatory( Entity ):
    """
    Consignatories for a Bill or Motion
    """



#############

class ParliamentSession( Entity ):
    """
    """
    sort_on = ['start_date',]
    sort_dir = 'desc'
    
    
class Rota( object ):
    """
    """

class Take( object ):
    """
    """

class TakeMedia( object ):
    """
    """

class Transcript( object ):
    """
    """    


class ObjectSubscriptions( object ):
    """
    """

# ###############

class Constituency( Entity ):
    """ a locality region, which elects an MP 
    """
    cdetail = one2many("cdetail", "bungeni.models.domain.ConstituencyDetailContainer", "constituency_id")
    sort_replace = {'province_id': ['province'], 'region_id': ['region']}      
    
ConstituencyChange = ItemLog.makeLogFactory( "ConstituencyChange")
ConstituencyVersion = ItemVersions.makeVersionFactory("ConstituencyVersion")

class Region( Entity ):
    """
    Region of the constituency
    """
    constituencies = one2many( "constituencies", "bungeni.models.domain.ConstituencyContainer", "region" ) 
    
class Province( Entity ):
    """
    Province of the Constituency
    """
    constituencies = one2many( "constituencies", "bungeni.models.domain.ConstituencyContainer", "province" )
    
class Country( object ):
    """
    Country of Birth
    """ 
    pass   
    
class ConstituencyDetail( object ):
    """
    Details of the Constituency like population and voters at a given time
    """
    pass       
    
    
# ##########

    
class MemberTitle( object ):
    """ Titles for members in groups"""
    pass
    
class Keyword( object ):
    """ Keywords for groups """
    
class MemberRoleTitle( Entity ):
    """
    The role title a member has in a specific context
    and official addresses for a official role
    """    
    addresses = one2many( "addresses", "bungeni.models.domain.UserAddressContainer", "role_title_id" )    
    


class MinistryInParliament( object ):
    """
    auxilliary class to get the parliament and government for a ministry
    """
    
class ItemSchedule(Entity):
    """
    for which sitting was a parliamentary item scheduled
    """ 

    discussions = one2many(
        "discussions",
        "bungeni.models.domain.ScheduledItemDiscussionContainer",
        "schedule_id")

    @property
    def getItem(self):
        session = Session()
        s_item = self.item
        s_item.__parent__ = self
        return s_item
        
    @property
    def getDiscussion(self):
        session = Session()
        s_discussion = self.discussion
        s_discussion.__parent__ = self
        return s_discussion

class ItemScheduleCategory(Entity):
    """ category of a scheduled item used to
    get the 'headings' when producing the agenda/ minutes
    for a sitting """
    

class ScheduledItemDiscussion(Entity):
    """A discussion on a scheduled item."""

class TabledDocument(ParliamentaryItem):
    """
    Tabled documents:
    a tabled document captures metadata about the document (owner, date, title, description) 
    and can have multiple physical documents attached.

        The tabled documents form should have the following :

    -Document title
    -Document link
    -Upload field (s)
    -Document source  / author agency (who is providing the document)
    (=> new table agencies)

    -Document submitter (who is submitting the document)
    (a person -> normally mp can be other user)

    It must be possible to schedule a tabled document for a sitting.
    """
    interface.implements( interfaces.ITabledDocument, interfaces.IFileAttachments )
    files = files.DirectoryDescriptor()     
    versions = one2many(
        "versions",
        "bungeni.models.domain.TabledDocumentVersionContainer",
        "content_id")        
    
TabledDocumentChange = ItemLog.makeLogFactory( "TabledDocumentChange")
TabledDocumentVersion = ItemVersions.makeVersionFactory("TabledDocumentVersion")
    
    
    
class DocumentSource( object ):
    """
    Document source for a tabled document
    """

class EventItem( ParliamentaryItem ):
    """
    Bill events with dates and possiblity to upload files.

    bill events have a title, description and may be related to a sitting (house, committee or other group sittings)
    via the sitting they acquire a date
    and an additional date for items that are not related to a sitting.

    Bill events:

       1. workflow related. e.g. submission, first reading etc. 
       (here we can use the same mechanism as in questions ... 
       a comment can be written when clicking (schedule for first reading) 
       then will appear in the calendar ... and cone schedule it will have a date
       2. not workflow related events ... we need for the following fieds:
              * date
              * body
              * attachments

    All these "events" they may be listed together, in that case the "workflow" once should be ... e.g. in bold.
    """    

class HoliDay( object ):
    """
    is this day a holiday?
    if a date in in the table it is otherwise not
    """

    
class Resource ( object ):
    """
    A Resource that can be assigned to a sitting
    """

class ResourceBooking ( object ):
    """
    assign a resource to a sitting
    """
class ResourceType(object):
    """ A Type of resource"""

class Venue( object ):
    """ A venue for a sitting """
            
           
    
