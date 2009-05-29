
from StringIO import StringIO

import group, user

group_id = "bungeni_groups"
user_id  = "bungeni_users"

def install_pas_plugins( self ):
    pas = self.acl_users
    if not group_id in pas.objectIds():
        manager = group.GroupManager(group_id, "Bungeni Group Provider")
        pas._setObject( group_id, manager )
        group_provider = pas[ group_id ]
        group_provider.manage_activateInterfaces(
            ['IGroupsPlugin', 'IGroupEnumerationPlugin', 'IGroupIntrospection', 'IGroupManagement']
            )

    if not user_id in pas.objectIds():
        manager = user.UserManager(user_id, "Bungeni User Provider")
        pas._setObject( user_id, manager )
        user_provider = pas[ user_id ]
        
        user_provider.manage_activateInterfaces(
            ['IAuthenticationPlugin',
             'IUserEnumerationPlugin',
             'IUserManagement',
             'IUserAdderPlugin',
             'IRolesPlugin',
             'IRoleAssignerPlugin',
             'IRoleEnumerationPlugin']
            )        

def uninstall_pas_plugins( self ):
    pas = self.acl_users
    if group_id in pas.objectIds():
        pas[ group_id ].manage_activateInterfaces( [] )
        pas.manage_delObjects( [ group_id ] )

def uninstall( self ):
    out = StringIO()
    print >> out, "Removing PAS Plugin"
    uninstall_pas_plugins( self )
    return out.getvalue()    

def install( self ):
    out = StringIO()
    print >> out, "Installing and Activating PAS Property Plugin"
    install_pas_plugins( self )
    return out.getvalue()
