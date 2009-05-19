"""
$Id: $
"""
from zope import interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema import vocabulary
from zope.security.proxy import removeSecurityProxy
from ore.alchemist.vocabulary import DatabaseSource, ObjectSource, Session
from ore.alchemist.container import valueKey
#import ore.alchemist
from sqlalchemy.orm import mapper,  column_property 
import sqlalchemy as rdb
import sqlalchemy.sql.expression as sql
import schema, domain

from i18n import _

#ModelTypeSource = ObjectSource( model.DataModelType, 'short_name', 'id')
#SecurityLevelSource = DatabaseSource( model.SecurityLevel, 'short_name', 'id' )


ParliamentMembers = ObjectSource( domain.User, 'name', 'member_id' )
PoliticalParties  = ObjectSource( domain.PoliticalParty, 'full_name', "id")
ParliamentSessions = ObjectSource( domain.ParliamentSession, 'short_name', 'session_id')
QuestionType = vocabulary.SimpleVocabulary.fromItems( [(_(u"Ordinary"), "O"), (_(u"Private Notice"), "P")] )
ResponseType = vocabulary.SimpleVocabulary.fromItems( [(_("Oral"), "O"), (_(u"Written"), "W")] )
Gender = vocabulary.SimpleVocabulary.fromItems( [(_(u"Male"), "M"), (_(u"Female"), "F")] )
ElectedNominated = vocabulary.SimpleVocabulary.fromItems( [(_(u"elected"),'E'),(_(u"nominated") ,'N'), (_(u"ex officio"),'O')])
InActiveDead = vocabulary.SimpleVocabulary.fromItems([(_(u"active"),'A'),(_(u"inactive"), 'I'),(_(u"deceased"), 'D')])
ISResponse = vocabulary.SimpleVocabulary.fromItems([(_(u"initial"),'I'),(_(u"subsequent"), 'S'),])

Constituencies = ObjectSource( domain.Constituency, 'name', 'constituency_id')
Parliaments = ObjectSource(
    domain.Parliament, 'short_name', 'parliament_id',
    title_getter=lambda ob: "%s (%s-%s)" % (
        ob.full_name,
        ob.start_date and ob.start_date.strftime("%Y/%m/%d") or "?",
        ob.end_date and ob.end_date.strftime("%Y/%m/%d") or "?"))

ItemScheduleCategories = DatabaseSource(
    domain.ItemScheduleCategory, 'category_id', 'category_id', 'short_name')

SittingTypes = DatabaseSource(
    domain.SittingType, 'sitting_type', 'sitting_type_id',
    title_getter=lambda ob: "%s (%s-%s)" % (
        ob.sitting_type.capitalize(), ob.start_time, ob.end_time))

SittingTypeOnly = DatabaseSource(
    domain.SittingType, 
    title_field='sitting_type',
    token_field='sitting_type_id',
    value_field='sitting_type_id')

class mps_sitting( object ):
    """ returns the mps for a sitting """
    

_mp_sitting = rdb.join(
    schema.sittings, 
    schema.user_group_memberships,
    schema.sittings.c.group_id == schema.user_group_memberships.c.group_id).join(
    schema.users,
    schema.user_group_memberships.c.user_id == schema.users.c.user_id)

                                                                
mapper( mps_sitting, _mp_sitting,
          properties={
           'fullname' : column_property(
                             (schema.users.c.first_name + u" " + 
                             schema.users.c.middle_name + u" " + 
                             schema.users.c.last_name).label('fullname')
                                           )
                    },)
                    
class mp_ministers( object ):
    """ returns the MPs which are members of the parliament for a (given) ministry
    (potential ministers)
    """

_mp_ministers = rdb.join(schema.ministries, schema.governments,
                        schema.ministries.c.government_id == schema.governments.c.government_id).join(
                            schema.parliaments,
                            schema.governments.c.parliament_id == schema.parliaments.c.parliament_id).join(
                                schema.user_group_memberships,
                                schema.parliaments.c.parliament_id == schema.user_group_memberships.c.group_id).join(
                                    schema.users,
                                    schema.user_group_memberships.c.user_id == schema.users.c.user_id)
                    
mapper( mp_ministers, _mp_ministers,
        properties={
           'fullname' : column_property(
                             (schema.users.c.first_name + u" " + 
                             schema.users.c.middle_name + u" " + 
                             schema.users.c.last_name).label('fullname')
                                           )
                    },)     
                    
                    
class mp_committees( object ):
    """ Returns the MPs that are members of the parliament for a (given) committee
    (potential committee members)"""
    
_mp_comittee = rdb.join(schema.committees,  schema.parliaments,
                        schema.committees.c.parliament_id == schema.parliaments.c.parliament_id).join(
                                schema.user_group_memberships,
                                schema.parliaments.c.parliament_id == schema.user_group_memberships.c.group_id).join(
                                    schema.users,
                                    schema.user_group_memberships.c.user_id == schema.users.c.user_id)
mapper( mp_committees, _mp_comittee,
        properties={
           'fullname' : column_property(
                             (schema.users.c.first_name + u" " + 
                             schema.users.c.middle_name + u" " + 
                             schema.users.c.last_name).label('fullname')
                                           )
                    },)                                         

#class title_in_group( object ):
#     """ Titles for members in groups"""     
#_user_group_type = rdb.join(schema.groups, schema.user_role_type,
#                            schema.groups.c['type'] == schema.user_role_type.c.group_type)                            
#mapper( title_in_group, _user_group_type)

class substitution_member( object):
    """ replaced by this Member  """
    
_substitution_user = rdb.join( schema.user_group_memberships, schema.users,
                                schema.user_group_memberships.c.user_id == schema.users.c.user_id)

mapper (substitution_member, _substitution_user,
        properties={
           'fullname' : column_property(
                             (schema.users.c.first_name + u" " + 
                             schema.users.c.middle_name + u" " + 
                             schema.users.c.last_name).label('fullname')
                                           )
                    },          
        )                                    

class SpecializedSource( object ):
    interface.implements( IContextSourceBinder )
    def __init__( self, token_field, title_field, value_field ):
        self.token_field = token_field
        self.value_field = value_field
        self.title_field = title_field
            
    def constructQuery( self, context ):
        raise NotImplementedError("Must be implemented by subclass.")
        
    def __call__( self, context=None ):
        query = self.constructQuery( context )
        results = query.all()
        
        terms = []
        title_field = self.title_field or self.token_field
        for ob in results:
            terms.append( 
                vocabulary.SimpleTerm( 
                    value = getattr( ob, self.value_field), 
                    token = getattr( ob, self.token_field),
                    title = getattr( ob, title_field) ,
                    ))
                    
        return vocabulary.SimpleVocabulary( terms )

class MemberOfParliament( object ):
    """ Member of Parliament = user join group membership"""
    
member_of_parliament = rdb.join( schema.user_group_memberships, 
                    schema.users,
                    schema.user_group_memberships.c.user_id == 
                    schema.users.c.user_id)    

mapper(MemberOfParliament, member_of_parliament)
        

class MemberOfParliamentImmutableSource(SpecializedSource):
    
    def __init__(self, value_field):
        self.value_field = value_field
    
    def _get_parliament_id(self, context):
        parliament_id = getattr(context, 'parliament_id', None)
        if parliament_id is None:
            if context.__parent__ is None:
                return None
            else:    
                parliament_id = self._get_parliament_id(context.__parent__)            
        return parliament_id                
        
    def constructQuery(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        user_id = getattr(trusted, self.value_field, None)
        if user_id:
            query = session.query( domain.User 
                    ).filter(domain.User.user_id == 
                        user_id).order_by(domain.User.last_name,
                            domain.User.first_name,
                            domain.User.middle_name)                                                                                                                 
            return query
        else:
            parliament_id = self._get_parliament_id(trusted)
            if parliament_id:
                query = session.query(MemberOfParliament).filter(
                    sql.and_(MemberOfParliament.group_id ==
                            parliament_id,
                            MemberOfParliament.active_p ==
                            True)).order_by(MemberOfParliament.last_name,
                            MemberOfParliament.first_name,
                            MemberOfParliament.middle_name) 
            else:
                query = session.query(MemberOfParliament).order_by(MemberOfParliament.last_name,
                            MemberOfParliament.first_name,
                            MemberOfParliament.middle_name)                
        return query                                                                                                           

    def __call__( self, context=None ):
        query = self.constructQuery( context )
        results = query.all()        
        terms = []
        for ob in results:
            terms.append( 
                vocabulary.SimpleTerm( 
                    value = getattr( ob, 'user_id'), 
                    token = getattr( ob, 'user_id'),
                    title = "%s %s" % (getattr( ob, 'first_name') ,
                            getattr( ob, 'last_name'))
                    ))
        user_id = getattr(context, self.value_field, None) 
        if user_id:
            if len(query.filter(schema.users.c.user_id == user_id).all()) == 0:
                session = Session()            
                ob = session.query(domain.User).get(user_id)
                terms.append( 
                vocabulary.SimpleTerm( 
                    value = getattr( ob, 'user_id'), 
                    token = getattr( ob, 'user_id'),
                    title = "(%s %s)" % (getattr( ob, 'first_name') ,
                            getattr( ob, 'last_name'))
                    ))
        return vocabulary.SimpleVocabulary( terms )

class MemberOfParliamentSource(MemberOfParliamentImmutableSource):

    def constructQuery(self, context):
        session= Session()
        trusted=removeSecurityProxy(context)
        user_id = getattr(trusted, self.value_field, None)
        parliament_id = self._get_parliament_id(trusted)        
        if user_id:
            if parliament_id:
                query = session.query( MemberOfParliament
                        ).filter(
                        sql.or_(
                        sql.and_(MemberOfParliament.user_id == user_id,
                                MemberOfParliament.group_id ==
                                parliament_id),
                        sql.and_(MemberOfParliament.group_id ==
                                parliament_id,
                                MemberOfParliament.active_p ==
                                True)                     
                        )).order_by(
                            MemberOfParliament.last_name,
                            MemberOfParliament.first_name,
                            MemberOfParliament.middle_name).distinct()                                                                                                                       
                return query
            else:
                query = session.query(MemberOfParliament).order_by(
                            MemberOfParliament.last_name,
                            MemberOfParliament.first_name,
                            MemberOfParliament.middle_name)                 
        else:
            if parliament_id:
                query = session.query(MemberOfParliament).filter(                    
                    sql.and_(MemberOfParliament.group_id ==
                            parliament_id,
                            MemberOfParliament.active_p ==
                            True)).order_by(
                                MemberOfParliament.last_name,
                                MemberOfParliament.first_name,
                                MemberOfParliament.middle_name)
            else:
                query = session.query(MemberOfParliament).order_by(
                            MemberOfParliament.last_name,
                            MemberOfParliament.first_name,
                            MemberOfParliament.middle_name)                
        return query   




class QuerySource( object ):
    """ call a query with an additonal filter and ordering
    note that the domain_model *must* not have a where and order_by clause 
    (otherwise the parameters passed to this query will be ignored),
    the order_by and filter_field fields *must* be public attributes"""
    interface.implements( IContextSourceBinder )
    
    def getValueKey(self, context):
        """iterate through the parents until you get a valueKey """
        if context.__parent__ is None:
            return None
        else:            
            try:
                value_key = valueKey( context.__parent__.__name__ )[0]
            except:
                value_key = self.getValueKey( context.__parent__)
        return value_key         
        
        
    def __init__( self, domain_model, token_field, title_field, value_field, filter_field, filter_value=None, order_by_field=None,  ):
        self.domain_model = domain_model
        self.token_field = token_field
        self.value_field = value_field
        self.title_field = title_field
        self.filter_field = filter_field
        self.order_by_field = order_by_field
        self.filter_value = filter_value
        
    def constructQuery( self, context ):
        session = Session()
        trusted=removeSecurityProxy(context)
        #pdb.set_trace() 
        if self.filter_value:       
            query = session.query( self.domain_model ).filter(self.domain_model.c[self.filter_field] == trusted.__dict__[self.filter_value] )
        else:
            #pfk = valueKey( context.__parent__.__parent__.__name__ )[0]
            pfk = self.getValueKey(context)
            query = session.query( self.domain_model )
            #pdb.set_trace()
            query = query.filter(self.domain_model.c[self.filter_field] == pfk )
            
        query = query.distinct()
        if self.order_by_field:
            query = query.order_by(self.domain_model.c[self.order_by_field])
            
            
        return query
        
    def __call__( self, context=None ):
        query = self.constructQuery( context )
        results = query.all()
        
        terms = []
        title_field = self.title_field or self.token_field
        for ob in results:
            terms.append( 
                vocabulary.SimpleTerm( 
                    value = getattr( ob, self.value_field), 
                    token = getattr( ob, self.token_field),
                    title = getattr( ob, title_field) ,
                    ))
                    
        return vocabulary.SimpleVocabulary( terms )


    
    



                      
        
        
        
