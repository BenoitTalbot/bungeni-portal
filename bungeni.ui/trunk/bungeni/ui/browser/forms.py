
# encoding: utf-8

from ore.alchemist.vocabulary import DatabaseSource

from alchemist.ui.content import ContentAddForm
from alchemist.ui.viewlet import EditFormViewlet

from zope.formlib import form
from zope import schema, interface
from zope.formlib.namedtemplate import NamedTemplate


import bungeni.core.vocabulary as vocabulary
import bungeni.core.domain as domain
from bungeni.core.i18n import _
from bungeni.core.interfaces import IGroupSitting, IParliamentSession, IMemberOfParliament, \
    ICommittee, ICommitteeMember, IGovernment, IMinistry, IExtensionGroup, IMinister, \
    IExtensionMember, IParliament, IGroupSittingAttendance


from bungeni.ui.datetimewidget import  SelectDateTimeWidget, SelectDateWidget

import validations





#############
## ADD 

#####################
# Generic Custom Add Form

class CustomAddForm( ContentAddForm ):
    """
    Override the autogenerated Add form for custom behaviour
    """
    Adapts = {} 
    CustomValidation = None


    def finishConstruction( self, ob ):
        """
        adapt the custom fields to the object
        """
        self.adapters = { self.Adapts : ob }
               
             
    def validate(self, action, data):    
        """
        validation that require context must be called here,
        invariants may be defined in the descriptor
        """                                       
        return (form.getWidgetsData(self.widgets, self.prefix, data) +
                 form.checkInvariants(self.form_fields, data) +
                 self.CustomValidation( self.context, data ) )  
    
        
class ParliamentAdd( CustomAddForm ):
    """
    custom Add form for parliaments
    """
    form_fields = form.Fields( IParliament )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget  
    form_fields["election_date"].custom_widget = SelectDateWidget  
    Adapts = IParliament
    CustomValidation = validations.CheckParliamentDatesAdd  
    





# ministries
class MinistryAdd( CustomAddForm ):
    """
    custom Add form for ministries
    """
    form_fields = form.Fields( IMinistry )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget
    Adapts = IMinistry
    CustomValidation =  validations.CheckMinistryDatesInsideGovernmentDatesAdd     
                      

                 
#ministers


sql_addMinister = """
                SELECT DISTINCT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as fullname, 
                        "users"."user_id", "users"."last_name" 
                FROM "public"."ministries", "public"."government", "public"."parliaments", 
                    "public"."user_group_memberships", "public"."users" 
                WHERE ( "ministries"."government_id" = "government"."government_id" 
                    AND "government"."parliament_id" = "parliaments"."parliament_id" 
                    AND "user_group_memberships"."group_id" = "parliaments"."parliament_id" 
                    AND "user_group_memberships"."user_id" = "users"."user_id" ) 
                    AND ( "user_group_memberships"."active_p" = True AND "ministries"."ministry_id" = %(primary_key)s )
                    AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    ) 
                UNION
                SELECT DISTINCT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as fullname, 
                        "users"."user_id", "users"."last_name" 
                FROM "public"."ministries", "public"."government", "public"."groups", 
                    "public"."extension_groups", "public"."user_group_memberships", "public"."users" 
                WHERE ( "ministries"."government_id" = "government"."government_id" 
                    AND "ministries"."ministry_id" = "groups"."group_id" 
                    AND "extension_groups"."group_type" = "groups"."type" 
                    AND "extension_groups"."extension_type_id" = "user_group_memberships"."group_id" 
                    AND "user_group_memberships"."user_id" = "users"."user_id" 
                    AND "extension_groups"."parliament_id" = "government"."parliament_id" ) 
                    AND ( "user_group_memberships"."active_p" = True AND "ministries"."ministry_id" = %(primary_key)s )
                    AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    )                                     
                ORDER BY "last_name"
                """

qryAddMinisterVocab = vocabulary.SQLQuerySource(sql_addMinister, 'fullname', 'user_id')

class IMinisterAdd( IMinister ):
    """
    override some fields with custom schema
    """
    user_id = schema.Choice(title=_(u"Minister"),  
                                source=qryAddMinisterVocab, 
                                required=True,
                                )
    
    
class MinistersAdd( CustomAddForm ):
    """
    custom Add form for ministries
    """
    form_fields = form.Fields( IMinisterAdd ).omit( "replaced_id", "substitution_type" )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget
    Adapts = IMinisterAdd
    CustomValidation =   validations.CheckMinisterDatesInsideMinistryDatesAdd    
                       
    
# government

class GovernmentAdd ( CustomAddForm ):
    """
    custom Add form for government
    """
    form_fields = form.Fields( IGovernment )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget 
    Adapts = IGovernment
    CustomValidation =  validations.CheckGovernmentsDateInsideParliamentsDatesAdd    
                      
   

# Extension groups

class ExtensionGroupAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IExtensionGroup )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget 
    Adapts = IExtensionGroup
    CustomValidation =   validations.CheckExtensionGroupDatesInsideParentDatesAdd   
 



#XXX currently filters by "type" = 'memberofparliament' -> has to be replaced with all electable usertypes
sql_addExtensionMember = """
                        SELECT DISTINCT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as fullname, 
                        "users"."user_id", "users"."last_name" 
                        FROM "public"."users" 
                        WHERE ( ( "active_p" = 'A' AND "type" = 'memberofparliament' )
                                AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    )
                                AND ( "users"."user_id" NOT IN (SELECT "user_group_memberships"."user_id" 
                                                                FROM "public"."user_group_memberships", "public"."extension_groups" 
                                                                WHERE ( "user_group_memberships"."group_id" = "extension_groups"."parliament_id" ) 
                                                                AND ( "extension_groups"."extension_type_id" = %(primary_key)s  
                                                                        AND "active_p" = True) 
                                                                )
                                    )         
                               )                    
                        ORDER BY "last_name"
                        """
qryAddExtensionMemberVocab = vocabulary.SQLQuerySource(sql_addExtensionMember, 'fullname', 'user_id')

class IExtensionMemberAdd( IExtensionMember ):
    """
    override some fields for extension group members
    """
    user_id = schema.Choice(title=_(u"Person"),  
                                source=qryAddExtensionMemberVocab, 
                                required=True,
                                )
                                
                                
# Members of extension Groups
class ExtensionMemberAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IExtensionMemberAdd ).omit( "replaced_id", "substitution_type" )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget 
    Adapts = IExtensionMemberAdd
    CustomValidation =  validations.CheckExtensionMemberDatesInsideParentDatesAdd    
                      

# CommitteeMemberAdd



sql_AddCommitteeMember = """
                        SELECT DISTINCT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as fullname, 
                        "users"."user_id", "users"."last_name" 
                        FROM "public"."user_group_memberships", "public"."users", 
                             "public"."extension_groups", "public"."groups", 
                             "public"."committees", "public"."parliaments" 
                        WHERE ( "user_group_memberships"."user_id" = "users"."user_id" 
                                AND "extension_groups"."extension_type_id" = "user_group_memberships"."group_id" 
                                AND "extension_groups"."group_type" = "groups"."type" 
                                AND "committees"."committee_id" = "groups"."group_id" 
                                AND "committees"."parliament_id" = "parliaments"."parliament_id" 
                                AND "extension_groups"."parliament_id" = "parliaments"."parliament_id" ) 
                                AND ( "committees"."committee_id" = %(primary_key)s  AND "user_group_memberships"."active_p" = True )
                                AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    ) 
                        UNION
                        SELECT DISTINCT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as fullname,  
                        "users"."user_id", "users"."last_name" 
                        FROM "public"."committees", "public"."parliaments", "public"."groups", 
                            "public"."user_group_memberships", "public"."users" 
                        WHERE ( "committees"."parliament_id" = "parliaments"."parliament_id" 
                                AND "parliaments"."parliament_id" = "groups"."group_id" 
                                AND "user_group_memberships"."group_id" = "groups"."group_id" 
                                AND "user_group_memberships"."user_id" = "users"."user_id" ) 
                                AND ( "user_group_memberships"."active_p" = True AND "committees"."committee_id" = %(primary_key)s )
                                AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    )
                        ORDER BY "last_name"
                        """

qryAddCommitteeMemberVocab = vocabulary.SQLQuerySource(sql_AddCommitteeMember, 'fullname', 'user_id')

class ICommitteeMemberAdd ( ICommitteeMember ):
    """
    override some fields with custom schema
    """
    user_id = schema.Choice(title=_(u"Member of Parliament"),  
                                source=qryAddCommitteeMemberVocab, 
                                required=True,
                                )
class CommitteeMemberAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( ICommitteeMemberAdd ).omit( "replaced_id", "substitution_type" )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget
    Adapts = ICommitteeMemberAdd
    CustomValidation =  validations.CheckCommitteeMembersDatesInsideParentDatesAdd     
                      

# Committees


class CommitteeAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( ICommittee )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget    
    form_fields["dissolution_date"].custom_widget = SelectDateWidget
    form_fields["reinstatement_date"].custom_widget = SelectDateWidget 
    Adapts = ICommittee
    CustomValidation = validations.CheckCommitteesDatesInsideParentDatesAdd     
                      

# Members of Parliament



sql_AddMemberOfParliament = """
                            SELECT "titles" ||' ' || "first_name" || ' ' || "middle_name" || ' ' || "last_name" as fullname, "user_id" 
                            FROM "public"."users" 
                            WHERE ( ( "active_p" = 'A' ) 
                                AND ( "users"."user_id" NOT IN ( SELECT "user_id" 
                                                                FROM "public"."user_group_memberships" 
                                                                WHERE ( "group_id"  = %(primary_key)s 
                                                                        AND "active_p" = True) 
                                                                )                                           
                                    )
                                )
                            ORDER BY "users"."last_name"  
                            """
qryAddMemberOfParliamentVocab = vocabulary.SQLQuerySource(sql_AddMemberOfParliament, 'fullname', 'user_id')  

class IMemberOfParliamentAdd ( IMemberOfParliament ):
    """ Custom schema to override some autogenerated fields"""
    user_id = schema.Choice(title=_(u"Member of Parliament"),  
                                source=qryAddMemberOfParliamentVocab, 
                                required=True,
                                )


class MemberOfParliamentAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IMemberOfParliamentAdd ).omit( "replaced_id", "substitution_type" )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget 
    Adapts = IMemberOfParliamentAdd
    CustomValidation = validations.CheckMPsDatesInsideParentDatesAdd  
    
    

# Sessions

    
class SessionAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IParliamentSession )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget 
    Adapts = IParliamentSession
    CustomValidation =  validations.CheckSessionDatesInsideParentDatesAdd    
                      
 

# Sittings



class GroupSittingAdd( CustomAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IGroupSitting )
    form_fields["start_date"].custom_widget = SelectDateTimeWidget
    form_fields["end_date"].custom_widget = SelectDateTimeWidget
    Adapts = IGroupSitting
    CustomValidation =  validations.CheckSittingDatesInsideParentDatesAdd 
                      
        
     

sql_add_members ='''SELECT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as user_name, 
                    "users"."user_id", "group_sittings"."sitting_id" 
                    FROM "public"."group_sittings", "public"."sessions", 
                    "public"."user_group_memberships", "public"."users" 
                    WHERE ( "group_sittings"."session_id" = "sessions"."session_id" 
                        AND "user_group_memberships"."group_id" = "sessions"."parliament_id" 
                        AND "user_group_memberships"."user_id" = "users"."user_id" )
                        AND ( "user_group_memberships"."active_p" = True )
                        AND ("group_sittings"."sitting_id" = %(primary_key)s)
                        AND ( "users"."user_id" NOT IN (SELECT member_id 
                                                        FROM sitting_attendance 
                                                        WHERE sitting_id = %(primary_key)s )                                           
                            )
                    ORDER BY "users"."last_name"                    
                    '''
membersAddVocab = vocabulary.SQLQuerySource(sql_add_members, 'user_name', 'user_id')      
attendanceVocab = DatabaseSource(domain.AttendanceType, 'attendance_type', 'attendance_id' )

# Sitting Attendance

class IGroupSittingAttendanceAdd( interface.Interface ):
    """ """
    member_id = schema.Choice(title=_(u"Member of Parliament"),  
                                source=membersAddVocab, 
                                required=True,
                                )
    attendance_id = schema.Choice( title=_(u"Attendance"),  
                                    source=attendanceVocab, 
                                    required=True,
                                    )  



class GroupSittingAttendanceAdd( ContentAddForm ):
    """
    override the AddForm for GroupSittingAttendance
    """
    form_fields = form.Fields( IGroupSittingAttendanceAdd )
                      
    def update(self):
        """
        Called by formlib after __init__ for every page update. This is
        the method you can use to update form fields from your class
        """        
        self.status = self.request.get('portal_status_message','')        
        form.AddForm.update( self )
        set_widget_errors(self.widgets, self.errors)
         
    def finishConstruction( self, ob ):
        """
        adapt the custom fields to the object
        """
        self.adapters = { IGroupSittingAttendanceAdd : ob }
          
     


        
##############
# Edit forms      
##############

##############
#Generic Custom Edit form   

####
# Display invariant errors /  custom validation errors in the context of the field
# that raised the error.

def set_widget_errors(widgets, errors):
    for widget in widgets:
        name = widget.context.getName()
        for error in errors:
            if isinstance(error, interface.Invalid) and name in error.args[1:]:
                if widget._error is None:
                    widget._error = error




def flag_changed_widgets( widgets, context, data):
    for widget in widgets:
        name = widget.context.getName()
        # If the field is not in the data, then go on to the next one
        if name not in data:
            widget.changed = False
            continue
        if data[name] == getattr(context, name):
            widget.changed = False
        else:
            widget.changed = True  
    return []                  

class CustomEditForm ( EditFormViewlet ):
    """
    Override the autogenerated Edit form for specific behaviour
    """  
    Adapts = None
    CustomValidations = None
    template = NamedTemplate('alchemist.subform')       
    
          
    def update( self ):
        """
        adapt the custom fields to our object
        """
        self.adapters = {self.Adapts  : self.context }    
        super( CustomEditForm, self).update()        
        set_widget_errors(self.widgets, self.errors)    
        
    def validate(self, action, data):    
        """
        validation that require context must be called here,
        invariants may be defined in the descriptor
        """       
                                   
        return (form.getWidgetsData(self.widgets, self.prefix, data) +
                 form.checkInvariants(self.form_fields, data) +
                 flag_changed_widgets( self.widgets, self.context, data) +     
                 self.CustomValidations( self.context, data) )  

    def invariantErrors( self ):        
        """ All invariant errors should be handled by the fields that raised them """
        return []    
                                 
                  
#################
# return only current member
# Members should not be editable (exchanged) once they were added

sql_edit_members = '''SELECT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as user_name, 
                      "users"."user_id" 
                       FROM  "public"."users" 
                       WHERE  "users"."user_id" = %(member_id)s                                                                  
                    '''            
membersEditVocab = vocabulary.SQLQuerySource(sql_edit_members, 'user_name', 'user_id', {'member_id':'$member_id'} )      
  
# Parliament
class ParliamentEdit( CustomEditForm ):
    """
    Edit a parliament
    """
    form_fields = form.Fields( IParliament )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget  
    form_fields["election_date"].custom_widget = SelectDateWidget     
    Adapts = IParliament
    CustomValidations = validations.CheckParliamentDatesEdit
   
       

                              

class GovernmentEdit( CustomEditForm ): 
    """
    Edit a government
    """
    form_fields = form.Fields( IGovernment )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget      
    Adapts = IGovernment
    CustomValidations = validations.CheckGovernmentsDateInsideParliamentsDatesEdit
    
# Sitting Attendance
             
  

class IGroupSittingAttendanceEdit( interface.Interface ):
    """ """
    member_id = schema.Choice(title=_(u"Member of Parliament"),  
                                source=membersEditVocab, 
                                required=True,
                                )
    attendance_id = schema.Choice( title=_(u"Attendance"),  
                                    source=attendanceVocab, 
                                    required=True,
                                    )  
   
class GroupSittingAttendanceEdit( EditFormViewlet ):
    """
    override the Edit Form for GroupSittingAttendance
    """
    form_fields = form.Fields( IGroupSittingAttendanceEdit )
    template = NamedTemplate('alchemist.subform')   
    def update( self ):
        """
        adapt the custom fields to our object
        """
        self.adapters = { IGroupSittingAttendance : self.context }        
        super( GroupSittingAttendanceEdit, self).update()
        set_widget_errors(self.widgets, self.errors)

# Sittings                    


class GroupSittingEdit( CustomEditForm ):
    """
    override the Edit Form for GroupSitting
    """
    form_fields = form.Fields( IGroupSitting )
    form_fields["start_date"].custom_widget = SelectDateTimeWidget
    form_fields["end_date"].custom_widget = SelectDateTimeWidget
    Adapts = IGroupSitting
    CustomValidations = validations.CheckSittingDatesInsideParentDatesEdit 

                 

class SessionsEdit ( CustomEditForm ):
    form_fields = form.Fields( IParliamentSession )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget      
    Adapts = IParliamentSession
    CustomValidations = validations.CheckSessionDatesEdit    

membersEditVocab = vocabulary.SQLQuerySource(sql_edit_members, 'user_name', 'user_id', {'member_id':'$user_id'} )  

sql_editSubstitution = """
                        SELECT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as user_name,        
                                "users"."user_id" , "users"."last_name"
                        FROM "public"."user_group_memberships", "public"."users" 
                        WHERE ( "user_group_memberships"."user_id" = "users"."user_id" ) 
                            AND ( ( "user_group_memberships"."group_id" = %(group_id)s 
                                AND "user_group_memberships"."user_id" != %(user_id)s 
                                AND "user_group_memberships"."active_p" = True ) ) 
                        UNION
                        SELECT "users"."titles" || ' ' || "users"."first_name" || ' ' || "users"."middle_name" || ' ' || "users"."last_name" as user_name,        
                                "users"."user_id" , "users"."last_name"
                        FROM  "public"."user_group_memberships", "public"."users"
                        WHERE (( "user_group_memberships"."replaced_id" = "users"."user_id" ) 
                            AND "user_group_memberships"."user_id" = %(user_id)s )                             
                        ORDER BY "last_name" ASC
                        """

substitutionsEditVocab = vocabulary.SQLQuerySource(sql_editSubstitution, 'user_name', 'user_id', 
                                                    {'user_id':'$user_id', 'group_id' : '$group_id'} )  
    
class IMemberOfParliamentEdit( IMemberOfParliament ):
    """ Custom schema to override some autogenerated fields"""
    user_id = schema.Choice(title=_(u"Member of Parliament"),  
                                source=membersEditVocab, 
                                required=True,
                                )
    replaced_id = schema.Choice(title=_(u"substituted by"),  
                                source=substitutionsEditVocab, 
                                required=False,
                                )
    
class MemberOfParliamenEdit( CustomEditForm ):     
    Adapts = IMemberOfParliamentEdit          
    form_fields = form.Fields( IMemberOfParliamentEdit )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.CheckMemberDatesEdit         

class CommitteeEdit ( CustomEditForm ):
    Adapts = ICommittee          
    form_fields = form.Fields( ICommittee )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget     
    form_fields["dissolution_date"].custom_widget = SelectDateWidget
    form_fields["reinstatement_date"].custom_widget = SelectDateWidget             
    CustomValidations = validations.CheckCommitteeDatesEdit 

class ICommitteeMemberEdit( ICommitteeMember ):
    """ Custom schema to override some autogenerated fields"""
    user_id = schema.Choice(title=_(u"Comittee Member"),  
                                source=membersEditVocab, 
                                required=True,
                                )
    replaced_id = schema.Choice(title=_(u"substituted by"),  
                                source=substitutionsEditVocab, 
                                required=False,
                                )
    
        
class CommitteeMemberEdit( CustomEditForm ):
    Adapts = ICommitteeMemberEdit          
    form_fields = form.Fields( ICommitteeMemberEdit )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.CommitteeMemberDatesEdit
   
class MinistryEdit( CustomEditForm ):
    Adapts = IMinistry   
    form_fields = form.Fields( IMinistry )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.MinistryDatesEdit

class IMinisterEdit( IMinister ):
    """ Custom schema to override some autogenerated fields"""
    user_id = schema.Choice(title=_(u"Minister"),  
                                source=membersEditVocab, 
                                required=True,
                                )
    replaced_id = schema.Choice(title=_(u"substituted by"),  
                                source=substitutionsEditVocab, 
                                required=False,
                                )

class MinisterEdit( CustomEditForm ):
    Adapts = IMinisterEdit   
    form_fields = form.Fields( IMinisterEdit )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.MinisterDatesEdit
    
class ExtensionGroupEdit( CustomEditForm ):
    Adapts = IExtensionGroup   
    form_fields = form.Fields( IExtensionGroup )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.ExtensionGroupDatesEdit    
        
class IExtensionMemberEdit( IExtensionMember ):
    """ Custom schema to override some autogenerated fields"""
    user_id = schema.Choice(title=_(u"Member"),  
                                source=membersEditVocab, 
                                required=True,
                                )
    replaced_id = schema.Choice(title=_(u"substituted by"),  
                                source=substitutionsEditVocab, 
                                required=False,
                                )
       
class ExtensionMemberEdit( CustomEditForm ):
    Adapts = IExtensionMemberEdit   
    form_fields = form.Fields( IExtensionMemberEdit )
    form_fields["start_date"].custom_widget = SelectDateWidget
    form_fields["end_date"].custom_widget = SelectDateWidget         
    CustomValidations = validations.ExtensionMemberDatesEdit    
            
