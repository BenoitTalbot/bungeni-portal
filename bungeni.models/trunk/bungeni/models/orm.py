
import sqlalchemy as rdb
from sqlalchemy.orm import mapper, relation, column_property, deferred

import schema
import domain

# Users
# general representation of a person
mapper( domain.User, schema.users,
          properties={
             'fullname' : column_property(
                 (schema.users.c.first_name + u" " + 
                  schema.users.c.middle_name + u" " + 
                  schema.users.c.last_name).label('fullname')
                 ),}, 
        polymorphic_on=schema.users.c.type,
        polymorphic_identity='user',
       )

mapper (domain.Keyword, schema.keywords)

# Groups
mapper( domain.Group, schema.groups,
        properties={
            'members': relation( domain.GroupMembership ),
            'group_principal_id': column_property(
                ("group." + schema.groups.c.type + "." + 
                rdb.cast(schema.groups.c.group_id, rdb.String)
                ).label('group_principal_id')),
             'contained_groups' : relation( domain.Group),                
#            'keywords': relation( domain.Keyword,  secondary=schema.groups_keywords,  )            
            },
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='group'
        
        )

# Keywords for groups
#mapper (domain.Keyword, schema.keywords,
#         properties = {
#                'groups': relation(domain.Group, secondary=schema.groups_keywords, backref='keywords'),
#                
#                   })

# delegate rights to act on behalf of a user
mapper (domain.UserDelegation, schema.user_delegations, 
        properties={
            'user': relation( domain.User,
                        primaryjoin=rdb.and_(
                            schema.user_delegations.c.user_id==
                            schema.users.c.user_id ),
                      uselist=False,
                      lazy=True ),  
            'delegation': relation( domain.User,
                        primaryjoin=rdb.and_(
                            schema.user_delegations.c.delegation_id==
                            schema.users.c.user_id,
                            schema.users.c.active_p=='A'
                             ),
                      uselist=False,
                      lazy=True ),                                                        
                }                      
        )
# group subclasses
mapper( domain.Government, schema.governments,
        inherits=domain.Group,                
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='government'
        )

mapper( domain.Parliament, schema.parliaments,
        inherits=domain.Group,                
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='parliament'
        )
        
mapper( domain.PoliticalParty, schema.political_parties,
        inherits=domain.Group,                        
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='political-party'
        )

mapper( domain.Ministry, schema.ministries,
        inherits=domain.Group,
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='ministry'
        )

mapper( domain.Committee, schema.committees,
        inherits=domain.Group,
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='committee'
        )    
        
mapper( domain.ExtensionGroup, schema.extension_groups,
        inherits=domain.Group,
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='extension'
        )                         


mapper( domain.Office, schema.offices,
        inherits=domain.Group,
        polymorphic_on=schema.groups.c.type,
        polymorphic_identity='office'
        )   

   

                

# Ministers and Committee members are defined by their group membership in a 
# ministry or committee (group)     

# we need to specify join clause for user explicitly because we have multiple fk
# to the user table.
mapper( domain.GroupMembership, schema.user_group_memberships,
        properties={
            'user': relation( domain.User,
                              primaryjoin=rdb.and_(schema.user_group_memberships.c.user_id==schema.users.c.user_id ),
                              uselist=False,
                              lazy=False ),
            'group': relation( domain.Group,
                               primaryjoin=schema.user_group_memberships.c.group_id==schema.groups.c.group_id,
                               uselist=False,
                               lazy=True ),                              
            'replaced': relation( domain.GroupMembership,
                                  primaryjoin=schema.user_group_memberships.c.replaced_id==schema.user_group_memberships.c.membership_id,
                                  uselist=False,
                                  lazy=True ),
            'sort_by_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.last_name + u" " + 
                             schema.users.c.first_name)],
                             schema.user_group_memberships.c.user_id==schema.users.c.user_id
                                    ).label('sort_by_name')
                                           ),  
            'short_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.first_name + u" " + 
                             schema.users.c.last_name)],
                             schema.user_group_memberships.c.user_id==schema.users.c.user_id
                                    ).label('short_name')
                                           ),

            },
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='member',            
        )



mapper ( domain.MemberOfParliament , 
        schema.parliament_memberships,
         inherits=domain.GroupMembership,
         primary_key=[schema.user_group_memberships.c.membership_id], 
          properties={
            'image' :  column_property( 
                             rdb.sql.select(
                             [(schema.users.c.image)],
                             schema.user_group_memberships.c.user_id==schema.users.c.user_id
                                    ).label('image')
                                           ),
            'constituency': relation( domain.Constituency,
                              primaryjoin=(schema.parliament_memberships.c.constituency_id==
                                    schema.constituencies.c.constituency_id),
                              uselist=False,
                              lazy=False ),
            'constituency_id':[schema.parliament_memberships.c.constituency_id], 
            'start_date' :  column_property(schema.user_group_memberships.c.start_date.label('start_date')), 
            'end_date' :  column_property(schema.user_group_memberships.c.end_date.label('end_date')),
               
          },      
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='parliamentmember'  
        )
        
   
mapper( domain.Minister, 
        inherits=domain.GroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='minister',        
        )        
 
mapper( domain.CommitteeMember, 
        inherits=domain.GroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='committeemember',
                
                )  

mapper( domain.ExtensionMember, 
        inherits=domain.GroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='extensionmember',        
        )                                

mapper( domain.PartyMember, 
        inherits=domain.GroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='partymember',        
        )  
                
mapper( domain.OfficeMember, 
        inherits=domain.GroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='officemember',        
        )  
        
#mapper( domain.MemberOfParty, 
#        inherits=domain.GroupMembership,
#        polymorphic_on=schema.user_group_memberships.c.membership_type,          
#        polymorphic_identity='partymember',        
#        )          

_ugm_party = rdb.alias(schema.user_group_memberships)
_ugm_parliament = rdb.alias(schema.user_group_memberships)

_pmp = rdb.join(schema.political_parties, schema.groups,
                schema.political_parties.c.party_id == schema.groups.c.group_id).join(
                   _ugm_party,
                  schema.groups.c.group_id == _ugm_party.c.group_id)
                 
_mpm = rdb.join(_ugm_parliament, _pmp,
                rdb.and_(_ugm_parliament.c.user_id == _ugm_party.c.user_id,
                     _ugm_parliament.c.group_id == schema.political_parties.c.parliament_id)
                     )
                     
mapper( domain.MemberOfParty, _mpm,
        primary_key=[schema.user_group_memberships.c.membership_id],
        properties={
           'membership_id' : column_property(_ugm_parliament.c.membership_id.label('membership_id')),
           'party_membership_id' : column_property(_ugm_party.c.membership_id.label('party_membership_id')),           
           'start_date' : column_property(_ugm_party.c.start_date.label('start_date')),
           'end_date' : column_property(_ugm_party.c.end_date.label('end_date')),
           'short_name' : column_property(schema.groups.c.short_name.label('short_name')),
           'user_id' : column_property(_ugm_party.c.user_id.label('user_id')),
           'user': relation( domain.User,
                  primaryjoin=(_ugm_party.c.user_id==schema.users.c.user_id ),
                  uselist=False, viewonly=True ),
           },
         include_properties=['membership_id', 'short_name', 'start_date', 'end_date', 'group_id'],                      
       )                                       
 
 
                
# staff assigned to a group (committee, ...)

mapper( domain.StaffGroupMembership, schema.user_group_memberships,
        properties={
            'short_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.first_name + u" " + 
                             #schema.users.c.middle_name + u" " +
                             schema.users.c.last_name)],
                             schema.user_group_memberships.c.user_id==schema.users.c.user_id
                                    ).label('short_name')
                                           ),
            'sort_by_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.last_name + u" " + 
                             schema.users.c.first_name)],
                             schema.user_group_memberships.c.user_id==schema.users.c.user_id
                                    ).label('sort_by_name')
                                           ),
                                           
          },
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='staff',
      )

mapper( domain.CommitteeStaff,
        inherits=domain.StaffGroupMembership,
        polymorphic_on=schema.user_group_memberships.c.membership_type,          
        polymorphic_identity='committeestaff',        
        )


# Reporters XXX
mapper( domain.HansardReporter, schema.reporters,
        inherits=domain.User,
        polymorphic_identity='reporter')
                


mapper( domain.ParliamentSession, schema.parliament_sessions )
mapper( domain.GroupSitting, schema.sittings,
        properties = {
            'sitting_type': relation(
                domain.SittingType, uselist=False),
            'group': relation( domain.Group,
                               primaryjoin=schema.sittings.c.group_id==schema.groups.c.group_id,
                               uselist=False,
                               lazy=True ),  
            'start_date' :  column_property(schema.sittings.c.start_date.label('start_date')), 
            'end_date' :  column_property(schema.sittings.c.end_date.label('end_date')),                                             
            })

mapper( domain.ResourceType, schema.resource_types )
mapper( domain.Resource, schema.resources )
mapper( domain.ResourceBooking, schema.resourcebookings)

mapper( domain.Venue, schema.venues )

##############################
# Parliamentary Items

mapper( domain.ParliamentaryItem, schema.parliamentary_items,
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='item', 
        properties = {          
                    'owner': relation( domain.User,
                              primaryjoin=rdb.and_(schema.parliamentary_items.c.owner_id==schema.users.c.user_id ),
                              uselist=False,
                              lazy=False ),
                }
         )


mapper( domain.Question, schema.questions,
        inherits=domain.ParliamentaryItem,
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='question',
        properties = {
             'changes':relation( domain.QuestionChange, backref='question'),  
             'response' : relation( domain.Response, backref='question' ),                                 
             }
        )
        
mapper( domain.QuestionChange, schema.question_changes )
mapper( domain.QuestionVersion, schema.question_versions,
        properties= {'change': relation( domain.QuestionChange, uselist=False),
                     'head': relation( domain.Question, uselist=False)}
        )




mapper( domain.Motion, schema.motions,
        inherits=domain.ParliamentaryItem,
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='motion',
        properties = {
             'changes':relation( domain.MotionChange, backref='motion'),
             }
        )
        
mapper( domain.MotionChange, schema.motion_changes )
mapper( domain.MotionVersion, schema.motion_versions,
        properties= {'change':relation( domain.MotionChange, uselist=False),
                     'head': relation( domain.Motion, uselist=False)}
        )

        
mapper( domain.Bill, schema.bills,
        inherits=domain.ParliamentaryItem,
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='bill',
        properties = {
             'changes':relation( domain.BillChange, backref='bill')
             }
        )
mapper( domain.BillChange, schema.bill_changes )
mapper( domain.BillVersion, schema.bill_versions, 
        properties= {'change':relation( domain.BillChange, uselist=False),
                     'head': relation( domain.Bill, uselist=False)}
        )


mapper( domain.EventItem, schema.event_items, 
        inherits=domain.ParliamentaryItem,
        inherit_condition=(
                    schema.event_items.c.event_item_id == 
                    schema.parliamentary_items.c.parliamentary_item_id),
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='event')

mapper( domain.AgendaItem, schema.agenda_items, 
        inherits=domain.ParliamentaryItem,
        polymorphic_on=schema.parliamentary_items.c.type,
        polymorphic_identity='agendaitem')


mapper( domain.ResponseChange, schema.response_changes )
mapper( domain.ResponseVersion, schema.response_versions,
        properties= {'change':relation( domain.ResponseChange, uselist=False),
                     'head': relation( domain.Response, uselist=False)}
        )

mapper( domain.Response, schema.responses,
        properties = {
             'changes':relation( domain.ResponseChange, backref='question')
             }
        )


#Items scheduled for a sitting expressed as a relation
# to their item schedule
        
mapper(domain.ItemSchedule, schema.items_schedule,
       properties = {
           'item': relation(
               domain.ParliamentaryItem,
               uselist=False),
           'discussion': relation(
               domain.ScheduledItemDiscussion,
               uselist=False,
               cascade='all, delete-orphan'),
           'category': relation( domain.ItemScheduleCategory, uselist=False),    
           'sitting' : relation( domain.GroupSitting, uselist=False),     
           }
       ) 

mapper(domain.ScheduledItemDiscussion, schema.item_discussion)

mapper( domain.ItemScheduleCategory , schema.item_schedule_category)

# items scheduled for a sitting
# expressed as a join between item and schedule


       
mapper( domain.Consignatory, schema.consignatories,
        properties= {'item': relation(domain.ParliamentaryItem, uselist=False),
                      'user': relation(domain.User, uselist=False)})
mapper( domain.Debate, schema.debates )

mapper( domain.MotionAmendment, schema.motion_amendments)

mapper( domain.BillType, schema.bill_types )        
#mapper( domain.DocumentSource, schema.document_sources )
#mapper( domain.TabledDocument, schema.tabled_documents )


mapper( domain.HoliDay, schema.holidays )
        
######################
#
    

mapper( domain.Constituency, schema.constituencies,
        properties={
        'province': relation( domain.Province,
                              uselist=False,
                              lazy=False ),
        'region': relation( domain.Region,
                              uselist=False,
                              lazy=False ),                              
        'details': relation( domain.ConstituencyDetail,
                              uselist=False,
                              lazy=True ),
        }
    )    
mapper( domain.Province, schema.provinces )    
mapper( domain.Region, schema.regions )
mapper( domain.Country, schema.countries )
mapper( domain.ConstituencyDetail, schema.constituency_details )
mapper( domain.CommitteeType, schema.committee_type )   
mapper( domain.SittingType, schema.sitting_type )     
mapper( domain.GroupSittingAttendance, schema.sitting_attendance,
        properties={
            'user': relation( domain.User,
                              uselist=False,
                              lazy=True ),
            'short_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.first_name + u", " + 
                             #schema.users.c.middle_name + u" " +
                             schema.users.c.last_name)],
                             schema.sitting_attendance.c.member_id==schema.users.c.user_id
                                    ).distinct().label('short_name')
                                           ),
            'sort_by_name' : column_property(
                             rdb.sql.select(
                             [(schema.users.c.last_name + u" " + 
                             schema.users.c.first_name)],
                             schema.sitting_attendance.c.member_id==schema.users.c.user_id
                                    ).distinct().label('sort_by_name')
                                           ),
                                           
                  }
         )
mapper( domain.AttendanceType, schema.attendance_type )
mapper( domain.MemberTitle, schema.user_role_types )
mapper( domain.MemberRoleTitle, schema.role_titles.join(schema.addresses))

mapper( domain.AddressType, schema.address_types )
mapper( domain.UserAddress, schema.addresses)

###########################
# Current Items

# get the current gov and parliament for a ministry
_ministry_gov_parliament = rdb.join ( schema.ministries, schema.governments,
     schema.ministries.c.government_id == schema.governments.c.government_id)
mapper(domain.MinistryInParliament, _ministry_gov_parliament)                                     
                                    


    
