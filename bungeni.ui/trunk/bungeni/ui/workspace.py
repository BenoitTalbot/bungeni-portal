from zope import interface
from zope import component
from zope.publisher.browser import BrowserView
from zope.securitypolicy.interfaces import IRole
from ploned.ui.interfaces import IViewView
from bungeni.core.globalsettings import getCurrentParliamentId
from ore.alchemist import Session
from bungeni.models import domain


import interfaces



def getRoles(context=None):
    return [role_id for role_id, role in \
            component.getUtilitiesFor(IRole, context)]

role_interface_mapping = {
    u'bungeni.Admin': interfaces.IAdministratorWorkspace,
    u'bungeni.Minister': interfaces.IMinisterWorkspace,
    u'bungeni.MP': interfaces.IMPWorkspace,
    u'bungeni.Speaker': interfaces.ISpeakerWorkspace,
    u'bungeni.Clerk': interfaces.IClerkWorkspace
    }

class WorkspaceView(BrowserView):
    interface.implements(IViewView)
    
    def __init__(self, context, request):
        super(WorkspaceView, self).__init__(context, request)
        parliament_id = getCurrentParliamentId()
        if parliament_id:
            session = Session()
            parliament = session.query(domain.Parliament).get(parliament_id)
            self.context= parliament
            self.context.__parent__ = context
            self.context.__name__ = ""
            
        for role_id in getRoles():
            iface = role_interface_mapping.get(role_id)
            if iface is not None:
                interface.alsoProvides(self, iface)
