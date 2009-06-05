#
# note that other events are handled in workflows
# audit and files!

import datetime

from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalRoleMap

from ore.alchemist import Session
from bungeni.core import audit
from bungeni.models import interfaces


def consignatory_added(ob, event): 
    session = Session()
    ob = removeSecurityProxy(ob)
    if ob.user:
        title=  "%s %s %s" % (ob.user.titles,
                ob.user.first_name,
                ob.user.last_name)
    else:                
        title = ""        
    event.cls =  ob.__class__.__name__
    event.description = u" %s: %s added" % (
            ob.__class__.__name__ , 
            title)
    if ob.item:                        
        audit.objectContained( ob.item, event)

    
def consignatory_modified(ob, event):
    session = Session()
    ob = removeSecurityProxy(ob)
    if ob.user:
        title=  "%s %s %s" % (ob.user.titles,
                ob.user.first_name,
                ob.user.last_name)
    else:                
        title = ""        
    event.cls =  ob.__class__.__name__
    event.description = u" %s: %s modified" % (
            ob.__class__.__name__ , 
            title)
    if ob.item:                        
        audit.objectContained( ob.item, event)


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

def group_added_or_modified(context, group, role):
    """ when a group is added we 
    give the users of this group the local role
    'role' when the group is closed we delete
    the role (unsetRoleForPrincipal as oposed to 
    removeRoleFromPrincipal)
    """
    if (not group.end_date) or (group.end_date >= datetime.date.today()):
        IPrincipalRoleMap(context).assignRoleToPrincipal(
            role, group.group_principal_id)
    else:            
        IPrincipalRoleMap(context).unsetRoleForPrincipal(
            role, group.group_principal_id)
        
def parliament_added_modified(ob,event):
    """when a parliament is added all members get the local role
    bungeni.MP
    """
    trusted = removeSecurityProxy(ob)
    group_added_or_modified(ob, trusted, 'bungeni.MP')
    
def ministry_added_modified(ob,event):  
    trusted = removeSecurityProxy(ob)
    group_added_or_modified(ob, trusted, 'bungeni.Minister')

def committee_added_modified(ob,event):
    trusted = removeSecurityProxy(ob)
    group_added_or_modified(ob, trusted, 'bungeni.CommitteeMember')


def office_added_modified(ob, event):
    """ when an office is added or modified we 
    add/edit the local role at parliament level """
    trusted = removeSecurityProxy(ob)
    parliament = get_parliament(trusted)
    if parliament:
        if trusted.office_type == "S":
            role = "bungeni.Speaker"
        elif trusted.office_type == "C":
            role = "bungeni.Clerk"
        else: 
            raise NotImplementedError            
        group_added_or_modified(parliament, trusted, role)                         
    else:
        raise NotImplementedError                        
        
