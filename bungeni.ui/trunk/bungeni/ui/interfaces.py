
from zope.viewlet.interfaces import IViewletManager

from ploned.ui.interfaces import IPlonedSkin
from ore.yui.interfaces import IYUILayer

class IBungeniSkin(IPlonedSkin, IYUILayer):
    """Bungeni application skin."""

class IBungeniAuthenticatedSkin(IBungeniSkin):
    """Skin for authenticated users."""

class IWorkflowViewletManager( IViewletManager ):
    """
    Viewlet manager to display worflow history
    """
class IVersionViewletManager( IViewletManager ):
    """
    Viewletmanager to display the versions
    """

# class IParliamentMemberTaskMenu( interface.Interface ):
#     """ viewlet manager for member of parliament """
# 
# class IMinisterMemberTaskMenu( interface.Interface ):
#     """ viewlet manager for ministry """
