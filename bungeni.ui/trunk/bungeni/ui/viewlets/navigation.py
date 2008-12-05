# encoding: utf-8

from zope.viewlet import viewlet
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.security import proxy

from ore.alchemist.interfaces import IAlchemistContainer, IAlchemistContent
from ore.alchemist.model import queryModelDescriptor
from alchemist.traversal.managed import ManagedContainerDescriptor
from bungeni.core.app import BungeniApp
from bungeni.ui.utils import getDisplayDate
import bungeni.core.globalsettings as prefs
import datetime
import urllib, simplejson

class SiteActionsViewlet( viewlet.ViewletBase ):
    """
    Siteactions copied 1 to 1 from plone 
    return the pure html template only
    """
    render = ViewPageTemplateFile( 'templates/siteactions.pt' )

class BreadCrumbsViewlet( viewlet.ViewletBase ):
    """
    render the Breadcrumbs to show a user his current context
    """
    def __init__( self,  context, request, view, manager ):        
        self.context = context
        self.request = request
        self.__parent__= view
        self.manager = manager
        self.path = []
        self.navigation_root_url ='/'

    def _get_path( self, context, url = '' ): 
        """
        Return the current path as a list
        """
        descriptor = None
        name = None 
        path = []
        context = proxy.removeSecurityProxy( context )
        if context.__parent__ is not None:            
            path = path + self._get_path(context.__parent__, '../' + url )
        #if context != self.context:           
        if  IAlchemistContent.providedBy(context):
            path.append( {'name' : getattr(context, 'short_name', None ), 'url' : url})
        if IAlchemistContainer.providedBy(context):                        
            domain_model = context._class 
            try:
                descriptor = queryModelDescriptor( domain_model )
            except:
                descriptor = None
                name = ""                
            if descriptor:
                name = getattr( descriptor, 'display_name', None)
            if not name:
                name = getattr( context, '__name__', None)  
            path.append({'name' : name, 'url' : url} )                         
        return path
        
    def getRootfolder(self):
        m_url = prefs.getPloneMenuUrl()
        return '/'.join(m_url.split('/')[:-1])    
        
    def update( self ):
        """
        prepare the data needed to render the viewlet.        
        """
        self.path = self._get_path(self.context)       
        
    render = ViewPageTemplateFile( 'templates/breadcrumbs.pt' )        
    
class NavigationTreeViewlet( viewlet.ViewletBase ):
    """
    render a navigation tree
    
    """ 
    template = ViewPageTemplateFile('templates/contained-constraint-navigation.pt')
        
    def __init__( self,  context, request, view, manager ):        
        self.context = context
        self.request = request
        self.__parent__= view
        self.manager = manager
        self.path = []
        self.name  =''
        self.tree = []
        

   
    def _get_object_path(self, context, url=''):
        """
        traverse up the tree 
        """
        path = []
        context = proxy.removeSecurityProxy( context )
        if context.__parent__ is not None:            
            path = path + self._get_object_path(context.__parent__, '../' + url )     
        else:            
            return []
        path.append({'obj':context, 'url':url})            
        return path
   
   
        
        
    def _append_child( self, path):
        """
        build the navigation tree
        """
        items = []
        if len(path) == 0:
            return items
        url = path[0]['url']
        if IAlchemistContent.providedBy(path[0]['obj']):                     
            item = {'name' : getattr(path[0]['obj'], 'short_name', None ), 'url' : url, 'current': 'navTreeItemInPath'}
            if len(path) > 1:
                item['node'] = self._append_child(path[1:])
            else: 
                # leaf => append actions
                item['current'] = 'navTreeCurrentItem'                                        
                context_class = path[0]['obj'].__class__
                context_class = proxy.removeSecurityProxy( context_class )    
                
                citems =[]
                for k, v in context_class.__dict__.items():
                    if isinstance( v, ManagedContainerDescriptor ):
                        domain_model = v.domain_container._class 
                        descriptor = queryModelDescriptor( domain_model )
                        if descriptor:
                            name = getattr( descriptor, 'display_name', None)
                        if not name:
                            name = domain_model.__name__                            
                        i = { 'name' : name,
                              'current' : '',
                              'url'  :  k, 
                              'node' : None,
                              'script': True }                                          
                        if domain_model == context_class: 
                            i['current'] = 'navTreeCurrentItem'                              
                        citems.append( i )
                item['node'] = citems
            items.append(item)
        if IAlchemistContainer.providedBy(path[0]['obj']):                        
            if (path[0]['obj'].__parent__ is None) or (path[0]['obj'].__parent__.__class__ == BungeniApp): 
                #Navigation Root               
                domain_model = path[0]['obj']._class 
                descriptor = queryModelDescriptor( domain_model )
                if descriptor:
                    name = getattr( descriptor, 'display_name', None)
                if not name:
                    name = getattr( domain_model, '__name__', None) 
                item = { 'name' : name,
                            'url'  : url ,
                            'current': 'navTreeItemInPath', 
                            'script': False,
                             } 
                if len(path) > 1:
                    item['node'] = self._append_child(path[1:])
                else:
                    item['node'] = None
                    item['current'] = 'navTreeCurrentItem'
                items.append(item)                     
                return items

                         
            context_class = path[0]['obj'].__parent__.__class__
            context_class = proxy.removeSecurityProxy( context_class )                
            for k, v in context_class.__dict__.items():
                if isinstance( v, ManagedContainerDescriptor ):
                    domain_model = v.domain_container._class 
                    descriptor = queryModelDescriptor( domain_model )                    
                    if len(path) == 1:
                        current = 'navTreeItemInPath'
                    else:
                        current = 'navTreeCurrentItem'
                    if descriptor:
                        name = getattr( descriptor, 'display_name', None)
                    if not name:
                        name = domain_model.__name__
                    if domain_model == path[0]['obj']._class:   
                        item = { 'name' : name,
                            'url'  : url + '../' + k,
                            'current': 'navTreeItemInPath', 
                            'script': False,
                             }
                        if len(path) > 1:
                            item['node'] = self._append_child(path[1:])
                        else:
                            item['node'] = None
                            item['current'] = 'navTreeCurrentItem' 
                    else:                            
                        item = { 'name' : name,
                              'current' : '',
                              'node' : None,
                              'url'  : url + '../' + k,
                              'script': False, }
                    items.append( item )  
        return items                                          

    def _appendSortFilter2URL(self, url):
        """
        get the filters from url and add them if applicable        
        """
        filter_by = ''
        displayDate = getDisplayDate(self.request)        
        if displayDate:
            filter_by='?date=' + datetime.date.strftime(displayDate,'%Y-%m-%d')
            return url + filter_by               
        else:
            return url                    

            
    def _tree2html(self, items, level = 0):
        #level = level +1
        if level >= 0:
            htmlstr = '<ul class="navTree navTreeLevel' + str(level) + '">'
        else:
            #if item['script']:
            #    htmlstr = '<noscript>'
            #else:                
            htmlstr = '' 
        for item in items:
            htmlstr = htmlstr + '<li class="navTreeItem ' + item['current'] +'" >'
            htmlstr = htmlstr + '<div><a href="' + self._appendSortFilter2URL(item['url']) + '"' + ' class="'  + item['current'] +'" >'
            htmlstr = htmlstr + str( item['name'] )   
            htmlstr = htmlstr + '</a></div>'           
            if item['node']:
                htmlstr = htmlstr + self._tree2html(item['node'], level + 1) 
            htmlstr = htmlstr +  '</li>'           
        if level >= 0:
            htmlstr = htmlstr +  '</ul>'
        return htmlstr
                    
    def _get_tree ( self, context, url = ''):
        items = []
        path = self._get_object_path(context)
        items = self._append_child( path)
        return self._tree2html(items)
        
       
    def getRootfolder(self):
        m_url = prefs.getPloneMenuUrl()
        return '/'.join(m_url.split('/')[:-1])          
        
    
    def update( self ):
        """
        prepare the data needed to render the viewlet.        
        """       
        self.tree = self._get_tree(self.context)  
    
    
    render = ViewPageTemplateFile( 'templates/bungeni-navigation-tree.pt' )

        

class PloneHorizontalNavigationViewlet( viewlet.ViewletBase ):
    """
    get the navigation menu from plone and display it
    """
    m_url = prefs.getPloneMenuUrl() 
    mf = None
    m_dict = {}
       
    def update(self):
        try:
            self.mf = urllib.urlopen(self.m_url)
            self.m_dict = simplejson.load(self.mf)
        except:
            pass            
         
    def append_li(self, menulist): 
        mstr = ''
        for mi in menulist:   
            #mstr = mstr + '<li id="' + mi['id'] + '" > <a href="' + mi['url'] + '">' + mi['title'] + '</a>'
            if mi.has_key('submenu'):
                mstr = mstr + '<li class="navTreeItem visualNoMarker" id="' + mi['id'] + '" > <a href="' + mi['url'] + '" class="hasDropDown">' + mi['title'] + '</a>'
                mstr = mstr + '<ul class="submenu">' + self.append_li(mi['submenu']) + '</ul>'
            else:
                mstr = mstr + '<li class="navTreeItem visualNoMarker" id="' + mi['id'] + '" > <a href="' + mi['url'] + '">' + mi['title'] + '</a>'
            mstr = mstr + '</li>' 
        return mstr   
           
    def dict2menu(self):
        try:
            mstr = '<div id="globalnav-wrapper">'
            mstr = mstr + '<ul id="portal-globalnav">'                
            #for mi in self.m_dict:
                    #mstr = mstr + '<li id="' + mi['id'] + '" > <a href="' + mi['url'] + '">' + mi['title'] + '</a> </li>'
            mstr = mstr + self.append_li(self.m_dict)
            mstr = mstr + '</ul> <div id="post-sections-clear" class="visualClear"></div> </div>'
            return mstr
        except:
            return ''
    
    def render(self):
        return self.dict2menu()
        

        
