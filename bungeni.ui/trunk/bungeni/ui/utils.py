'''Various utilities for the UI

$Id$
'''

import datetime
from bungeni.ui.i18n import _
from types import StringTypes, ListType

from ore.workflow import interfaces

import os


# file system 

def pathjoin(basefilepath, filepath):
    return os.path.join(os.path.dirname(basefilepath), filepath)


# workflow 

def get_wf_state(context):
    # return human readable workflow title
    wf = interfaces.IWorkflow(context)
    wf_state = interfaces.IWorkflowState(context).getState()
    return wf.workflow.states[wf_state].title

    
# request 

def is_ajax_request(request):
    return request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


# url 

def urljoin(base, action):
    if action is None:
        return
    if action.startswith('http://') or action.startswith('https://'):
        return action
    if action.startswith('/'):
        raise NotImplementedError(action)

    return "/".join((base, action.lstrip('./')))

# XXX tmp hack -- business/whats-on -- because the "index" of the business 
# section is actually called "whats-on", we also check and remove that
# TODO rename business/whats-on to business/index
indexNames = ("index", "index.html", "@@index.html", "whats-on")

def absoluteURL(context, request):
    """
    For cleaner public URLs, we ensure to use an empty string instead of 'index'.
    
    Throughout bungeni and ploned packages, this function should ALWAYS be
    used instead of zope.traversing.browser.absoluteURL.
    """
    import logging; log = logging.getLogger('bungeni.ui.utils');
    from zope.traversing import browser
    url = browser.absoluteURL(context, request).split("/")
    while url[-1] in indexNames:
        log.warning(" POPPING: %s -> %s" % ('/'.join(url), url[-1]))
        url.pop()
    return '/'.join(url)

def same_path_names(base_path_name, path_name):
    """ (base_path_name, path_name) -> bool
    
    Checks if the two url path names are "equivalent" -- considering the case 
    for "" as base_path_name implying that we should be at an "index" URL node.
    """
    if base_path_name!=path_name:
        if base_path_name=="": # empty string -> index
            if path_name in indexNames:
                return True
    return base_path_name==path_name


# misc

def makeList(itemIds):
    if type(itemIds) == ListType:
        return itemIds            
    elif type(itemIds) in StringTypes:
        # only one item in this list
        return [itemIds,]
    else:
         raise TypeError( _("Form values must be of type string or list"))


# date

def get_date( date):
    if type(date) == datetime.datetime:
        return date.date()
    elif type(date) == datetime.date:
        return date
    else:
        raise TypeError (_("date must be of type datetime or date"))

def getDisplayDate(request):   
    """
    get the date for which to display the data.
    #SQL WHERE:
    # displayDate BETWEEN start_date and end_date
    # OR
    # displayDate > start_date and end_date IS NULL   
    """ 
    filter_by = ''
    DisplayDate = request.get('date', None)
    if not DisplayDate:
        if request.has_key('display_date'):
            DisplayDate = request['display_date']
#    else:
#        if request.has_key('display_date'):
#            if DisplayDate != request['display_date']:         
#                request.response.setCookie('display_date', DisplayDate, path='/')               
#        else:
#            request.response.setCookie('display_date', DisplayDate, path='/' )          
    displayDate = None
    if DisplayDate:
        try:
            y, m, d = (int(x) for x in DisplayDate.split('-'))
            displayDate = datetime.date(y,m,d)
        except:
            #displayDate = datetime.date.today()              
            displayDate = None
    else:
        #displayDate = datetime.date.today() 
        displayDate=None
    return displayDate

def getFilter(displayDate):                   
    if displayDate:
        filter_by = """
        ( ('%(displayDate)s' BETWEEN start_date AND end_date )
        OR
        ( '%(displayDate)s' > start_date AND end_date IS NULL) )
        """ % ({ 'displayDate' : displayDate})        
    else:
        filter_by = ""            
    return filter_by

#

