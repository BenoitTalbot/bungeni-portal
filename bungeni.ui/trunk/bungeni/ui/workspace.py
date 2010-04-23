# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Workspace Views

$Id$
"""
log = __import__("logging").getLogger("bungeni.ui.workspace")

import sys

from zope import component
from zope import interface
from zope.app.publication.traversers import SimpleComponentTraverser
from zope.location.interfaces import ILocation
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IHTTPRequest
from zope.security.proxy import ProxyFactory
from zope.security.proxy import removeSecurityProxy

from sqlalchemy import sql

from ore.alchemist import Session

from bungeni.core.i18n import _
from bungeni.core.content import Section, QueryContent
from bungeni.core.proxy import LocationProxy
from bungeni.core.interfaces import ISchedulingContext
from bungeni.core.schedule import format_date

from bungeni.models import interfaces as model_interfaces
from bungeni.models import domain
from bungeni.models.utils import container_getter
from bungeni.models.utils import get_db_user_id
from bungeni.models.utils import get_roles
from bungeni.models.utils import get_group_ids_for_user_in_parliament 
from bungeni.models.utils import get_ministries_for_user_in_government
from bungeni.models.utils import get_current_parliament
from bungeni.models.utils import get_current_parliament_governments

from bungeni.ui.utils import url, misc, debug
from bungeni.ui import interfaces

from ploned.ui.interfaces import IViewView


class BungeniBrowserView(BrowserView):
    interface.implements(IViewView)
    
    page_title = u" :BungeniBrowserView.page_title: "
    provider_name = None # str, to be set by subclass, to specify the 
    # ViewletManager.name for the viewlet manager that is providing the 
    # viewlets for this view
    
    def provide(self):
        """ () -> str
        
        To give view templates the ability to call on a view-defined provider, 
        without having to hard-wire the provider name in the template itself
        i.e. this is to be able to replace template calls such as:
            <div tal:replace="structure provider:HARD_WIRED_PROVIDER_NAME" />
        with:
            <div tal:replace="structure python:view.provide() />
        The provider_name attribute is factored out so that it is trivial 
        for view subclasses to specify a provider name.
        
        Also to decouple a zope-specific feature (the provider ZPT keyword) 
        out of the templates by making it (for the templates) a generic python 
        call.
        """
        from zope.viewlet.interfaces import IViewletManager
        provider = component.getMultiAdapter(
                            (self.context, self.request, self),
                            IViewletManager,
                            name=self.provider_name)
        provider.update()
        return provider.render()



def prepare_user_workspaces(event):
    """Determine the current principal's workspaces, depending on roles and
    group memberships. 
    
    "bungeni.Clerk", "bungeni.Speaker", "bungeni.MP"
        these roles get a parliament-level workspace
    
    "bungeni.Minister"
        "implied" role (by being a member of a ministry group) 
        gets a ministry-level workspace (for each ministry)
    
    "zope.Manager", "bungeni.Admin", "bungeni.Owner", "bungeni.Everybody", 
    "bungeni.Anybody"
        not relevant for user workspaces, no workspaces
        !+ should these get an owner-level (user) workspace?
    
    """
    destination_url_path = url.get_destination_url_path(event.request)
    def need_to_prepare_workspaces(obj, req):
        return (
            # need only to do it when traversing "/", 
            # obj should be the BungeniApplication
            model_interfaces.IBungeniApplication.providedBy(obj)
            and
            # user is logged in
            interfaces.IBungeniAuthenticatedSkin.providedBy(req)
            and (
                # the request should be for a view within /workspace
                # note: IWorkspaceSectionLayer is applied to the request by 
                # publication.apply_request_layers_by_url() that therefore must 
                # have already been called
                interfaces.IWorkspaceSectionLayer.providedBy(req)
                or
                # the request is for "/" (we need to know the user 
                # workspaces to be able to redirect appropriately
                destination_url_path=="/"
                # !+ IHomeLayer
            )
        )
    if not need_to_prepare_workspaces(event.object, event.request):
        return
    
    request = event.request
    application = event.object # is bungeni.core.app.BungeniApp
    
    # initialize a layer data object, for the views in the layer
    LD = request._layer_data = misc.bunch(
        workspaces=[], # workspace containers !+ unique?
        # !+ role-based workspaces: (role|group, workspace_container)
        # these are needed by the views, as we need them also here, we just
        # remember them to not need to calculate them again
        user_id=None,
        user_group_ids=None,
        government_id=None,
        ministry_ids=None,
    )
    # !+ from zope.annotation.interfaces import IAnnotations
    #    LD = IAnnotations(request)["layer_data"] = ...
    
    LD.user_id = get_db_user_id()
    try:
        parliament = get_current_parliament(None)
        assert parliament is not None # force exception
        # we do get_roles under the current parliament as context, but we 
        # must ensure that the BungeniApp is along the __parent__ stack:
        parliament.__parent__ = application
        roles = get_roles(parliament)
        # "bungeni.Clerk", "bungeni.Speaker", "bungeni.MP"
        for role_id in roles:
            if role_id in ("bungeni.Clerk", "bungeni.Speaker", "bungeni.MP"):
                log.debug("adding parliament workspace %s (for role %s)" % (
                                                        parliament, role_id))
                LD.workspaces.append(parliament)
    
        # "bungeni.Minister"
        # need to check for ministry groups to which the principal belongs, and 
        # for each such ministry assign a ministry workspace
        LD.user_group_ids = get_group_ids_for_user_in_parliament(
                                    LD.user_id, parliament.group_id)
        LD.government_id = get_current_parliament_governments(
                                    parliament)[0].group_id # IndexError
        ministries = get_ministries_for_user_in_government(
                                            LD.user_id, LD.government_id)
        log.debug(""" [prepare_user_workspaces]
            user_id:%s
            parliament:(%s, %s) 
            government_id:%s
            ministries:%s""" % (
                LD.user_id, 
                parliament.full_name, parliament.group_id, 
                LD.government_id, 
                [(m.full_name, m.group_id) for m in ministries] ))
        for ministry in ministries:
            log.debug("adding ministry workspace %s" % ministry)
            LD.workspaces.append(ministry)
    except (Exception,):
        debug.log_exc_info(sys.exc_info(), log_handler=log.info)
    
    # ensure unique workspaces, preserving order, retaining same list obj ref
    LD.workspaces[:] = [ workspace for i,workspace in enumerate(LD.workspaces) 
                         if LD.workspaces.index(workspace)==i ]
    
    # mark each workspace container with IWorkspaceContainer
    for workspace in LD.workspaces:
        interface.alsoProvides(workspace, interfaces.IWorkspaceContainer)
        log.debug(debug.interfaces(workspace))
    
    log.debug(" [prepare_user_workspaces] %s" % debug.interfaces(request))
    log.info(""" [prepare_user_workspaces] DONE:
        for: [request=%s][path=%s]
        request._layer_data: %s""" % (id(request), destination_url_path,
            getattr(request, "_layer_data", None)))

# traversers

def workspace_resolver(context, request, name):
    """Get the workspace domain object identified by name.
    
    Raise zope.publisher.interfaces.NotFound if no container found.
    This is a callback for the "/workspace" Section (the context here), 
    to resolve which domain object is needed for a workspace.
    """
    if name.startswith("obj-"):
        obj_id = int(name[4:])
        for workspace in request._layer_data.workspaces:
            if obj_id==workspace.group_id:
                log.debug("[workspace_resolver] name=%s workspace=%s context=%s" % (
                                        name, workspace, context))
                assert interfaces.IWorkspaceContainer.providedBy(workspace)
                assert ILocation.providedBy(workspace)
                # update location for workspace
                workspace.__parent__ = context
                workspace.__name__ = name
                return workspace
    raise NotFound(context, name, request)


class WorkspaceContainerTraverser(SimpleComponentTraverser):
    """Custom Workspace (domain IBungeniGroup object) container traverser.
    This object is the "root" of each user's workspace.
    """
    interface.implementsOnly(IPublishTraverse)
    component.adapts(interfaces.IWorkspaceContainer, IHTTPRequest)
    
    def __init__(self, context, request):
        assert interfaces.IWorkspaceContainer.providedBy(context)
        self.context = context # workspace domain object
        self.request = request
        log.debug(" __init__ %s context=%s url=%s" % (
                        self, self.context, request.getURL()))
    
    def publishTraverse(self, request, name):        
        workspace = self.context
        _meth_id = "%s.publishTraverse" % self.__class__.__name__
        log.debug("%s: name=%s context=%s " % (_meth_id, name, workspace))
        if name=="pi":
            return getWorkSpacePISection(workspace)
        elif name=="archive":
            return getWorkSpaceArchiveSection(workspace)
        elif name=="calendar":
            #return ISchedulingContext(workspace)
            view = component.queryMultiAdapter(
                        (self.context, request), name="workspace-calendar")
            if view is None:
                raise NotFound(self.context, name)
            return view
        
        return super(WorkspaceContainerTraverser, 
                        self).publishTraverse(request, name)


# contexts

ARCHIVED = ("debated", "withdrawn", "response_complete", "elapsed")

# Note: for all the following QueryContent "sections", we want to keep 
# title=None so that no menu item for the entry will be displayed

def getWorkSpacePISection(workspace):
    """ /workspace/obj-id/pi -> non-ARCHIVED parliamentary items
    """
    s = Section(title=_(u"Parliamentary items"),
            description=_(u"Current parliamentary activity"),
            default_name="workspace-pi")
    interface.alsoProvides(s, interfaces.IWorkspacePIContext)
    s.__parent__ = workspace
    s.__name__ = "pi"
    s["questions"] = QueryContent(
            container_getter(workspace, 'questions',
            query_modifier=sql.not_(domain.Question.status.in_(ARCHIVED))),
            #title=_(u"Questions"),
            description=_(u"Questions"))
    s["motions"] = QueryContent(
            container_getter(workspace, 'motions',
                query_modifier=sql.not_(domain.Motion.status.in_(ARCHIVED))),
            #title=_(u"Motions"),
            description=_(u"Motions"))
    s["tableddocuments"] = QueryContent(
            container_getter(workspace, 'tableddocuments',
                query_modifier=sql.not_(domain.TabledDocument.status.in_(ARCHIVED))),
            #title=_(u"Tabled documents"),
            description=_(u"Tabled documents"))
    s["bills"] = QueryContent(
            container_getter(workspace, 'bills',
                query_modifier=sql.not_(domain.Bill.status.in_(ARCHIVED))),
            #title=_(u"Bills"),
            description=_(u"Bills"))
    s["agendaitems"] = QueryContent(
            container_getter(workspace, 'agendaitems',
                query_modifier=sql.not_(domain.AgendaItem.status.in_(ARCHIVED))),
            #title=_(u"Agenda items"),
            description=_(u" items"))
    s["committees"] = QueryContent(
            container_getter(workspace, 'committees'),
            #title=_(u"Committees"), # title=None to not show up in menu
            description=_(u"Committees"))
    log.debug("WorkspacePISection %s" % debug.interfaces(s))
    return s

def getWorkSpaceArchiveSection(workspace):
    """ /workspace/obj-id/my-archive/ -> ARCHIVED parliamentary items 
    """
    s = Section(title=_(u"My archive"),
            description=_(u"My archive personal items"),
            default_name="workspace-archive")
    interface.alsoProvides(s, interfaces.IWorkspaceArchiveContext)
    s.__parent__ = workspace
    s.__name__ = "archive"
    s["questions"] = QueryContent(
            container_getter(workspace, 'questions',
                query_modifier=domain.Question.status.in_(ARCHIVED)),
            #title=_(u"Questions"),
            description=_(u"Questions"))
    s["motions"] = QueryContent(
            container_getter(workspace, 'motions',
                query_modifier=domain.Motion.status.in_(ARCHIVED)),
            #title=_(u"Motions"),
            description=_(u"Motions"))
    s["tableddocuments"] = QueryContent(
            container_getter(workspace, 'tableddocuments',
                query_modifier=domain.TabledDocument.status.in_(ARCHIVED)),
            #title=_(u"Tabled documents"),
            description=_(u"Tabled documents"))
    s["bills"] = QueryContent(
            container_getter(workspace, 'bills',
                query_modifier=domain.Bill.status.in_(ARCHIVED)),
            #title=_(u"Bills"),
            description=_(u"Bills"))
    s["agendaitems"] = QueryContent(
            container_getter(workspace, 'agendaitems',
                query_modifier=domain.AgendaItem.status.in_(ARCHIVED)),
            #title=_(u"Agenda items"),
            description=_(u" items"))
    log.debug("getWorkSpaceArchiveSection %s" % debug.interfaces(s))
    return s


''' !+ workspace section contexts:
the more logical approach -- that did not work -- for the PI and Archive 
workspace sections: the idea is to have WorkspaceContainerTraverser return 
an interfaces.IWorkspacePIContext(workspace_container), that would then be
defined something like:

<adapter factory=".workspace.WorkspacePIContext" 
    for=".interfaces.IWorkspaceContainer" 
    provides=".interfaces.IWorkspacePIContext"
    permission="zope.Public" trusted="true" />

class WorkspacePIContext(Section):
    component.adapts(interfaces.IWorkspaceContainer, IHTTPRequest)
    interface.implements(interfaces.IWorkspacePIContext) 
    # interfaces.IWorkspaceSectionContext
    
    def __init__(self, context):
        # Section: title=None, description=None, default_name=None, 
        # marker=None, publishTraverseResolver=None
        super(WorkspacePIContext, self).__init__(
            title=_(u"Parliamentary items"),
            description=_(u"Current parliamentary activity"),
            default_name="workspace-pi")
        log.debug(" __init__ %s (context:%s)" % (self, context))
        self.context = context
        self.__parent__ = context
        self.__name__ = ""
        log.debug("WorkspacePIContext %s" % debug.interfaces(self))
        log.debug("WorkspacePIContext %s" % debug.location_stack(self))
        
        self["questions"] = self.get_questions()
    
    def get_questions(self):
        return QueryContent(
                container_getter(self.context, 'questions',
                query_modifier=sql.not_(domain.Question.status.in_(ARCHIVED))),
                #title=_(u"Questions"),
                description=_(u"Questions"))

# !+ also try using:
from zope.app.container.sample import SampleContainer
'''

class WorkspaceSchedulingContext(object):
    component.adapts(interfaces.IWorkspaceContainer)
    interface.implements(ISchedulingContext)
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.group_id = workspace.group_id
        interface.alsoProvides(self, interfaces.IWorkspaceSchedulingContext)
        self.__parent__ = workspace
        self.__name__ = ""
        log.debug("WorkspaceSchedulingContext %s" % debug.location_stack(self))
        
    @property
    def label(self):
        group = self.get_group()
        if group is not None:
            return u"%s (%s)" % (group.short_name, group.full_name)
        return _(u"Unknown principal group")
    
    def get_group(self, name="group"):

        if self.group_id is None:
            return
        try:
            session = Session()
            group = session.query(domain.Group).filter_by(group_id=self.group_id)[0]
        except IndexError:
            raise RuntimeError("Group not found (%d)." % self.group_id)
        return group
    
    def get_sittings(self, start_date=None, end_date=None):
        try: 
            sittings = self.get_group().sittings
        except (AttributeError,):
            # e.g. ministry has no sittings attribute
            return {} # !+ should be a bungeni.models.domain.ManagedContainer
            # !+ could add sittings to a ministry
            #    could not have calendar appear for ministries
        if start_date is None and end_date is None:
            return sittings
        assert start_date and end_date
        unproxied = removeSecurityProxy(sittings)
        unproxied.subset_query = sql.and_(
            unproxied.subset_query,
            domain.GroupSitting.start_date.between(
                format_date(start_date),
                format_date(end_date))
            )
        unproxied.__parent__ = ProxyFactory(LocationProxy(
            unproxied.__parent__, container=self, name="group"))
        return sittings


# views

class WorkspaceSectionView(BungeniBrowserView):
    
    # set on request._layer_data
    user_id = None
    user_group_ids = None
    government_id = None
    ministry_ids = None
    
    role_interface_mapping = {
        u'bungeni.Admin': interfaces.IAdministratorWorkspace,
        u'bungeni.Minister': interfaces.IMinisterWorkspace,
        u'bungeni.MP': interfaces.IMPWorkspace,
        u'bungeni.Speaker': interfaces.ISpeakerWorkspace,
        u'bungeni.Clerk': interfaces.IClerkWorkspace
    }

    def __init__(self, context, request):
        """self:zope.app.pagetemplate.simpleviewclass.SimpleViewClass -> 
                    templates/workspace-index.pt
           context:bungeni.core.content.Section
        """
        assert interfaces.IWorkspaceSectionLayer.providedBy(request)
        assert request._layer_data.get("workspaces") is not None        
        super(WorkspaceSectionView, self).__init__(context, request)
        log.debug(" __init__ %s context=%s url=%s" % (
                                        self, self.context, request.getURL()))
        LD = request._layer_data
        
        # transfer layer data items, for the view/template
        self.user_id = LD.user_id
        self.user_group_ids = LD.user_group_ids
        self.government_id = LD.government_id # may be None
        self.ministry_ids = LD.ministry_ids # may be None
        if self.ministry_ids:
            interface.alsoProvides(self, interfaces.IMinisterWorkspace)
        
        # roles are function of the context, so always recalculate
        roles = get_roles(self.context)
        for role_id in roles:
            iface = self.role_interface_mapping.get(role_id)
            if iface is not None:
                interface.alsoProvides(self, iface)

class WorkspacePIView(WorkspaceSectionView):
    page_title = u"Bungeni Workspace"
    provider_name = "bungeni.workspace"
    def __init__(self, context, request):
        super(WorkspacePIView, self).__init__(
                interfaces.IWorkspacePIContext(context), request)
        interface.alsoProvides(self.context, ILocation) # !+ needs it (again!)
        log.debug("WorkspacePIView %s" % debug.interfaces(self))
        log.debug("WorkspacePIView %s" % debug.location_stack(self))

class WorkspaceArchiveView(WorkspaceSectionView):
    provider_name = "bungeni.workspace-archive"
    page_title = u"Bungeni Workspace Archive"
    def __init__(self, context, request):
        super(WorkspaceArchiveView, self).__init__(
                interfaces.IWorkspaceArchiveContext(context), request)
        interface.alsoProvides(self.context, ILocation) # !+ needs it (again!)
        log.debug("WorkspaceArchiveView %s" % debug.interfaces(self))
        log.debug("WorkspaceArchiveView %s" % debug.location_stack(self))
    

