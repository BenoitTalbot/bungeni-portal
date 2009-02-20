"""

support for xml defined workflows, and security manipulations by state

"""

import amara
import logging

import bungeni.core

from zope.dottedname.resolve import resolve
import zope.securitypolicy.interfaces
from zope.security.proxy import removeSecurityProxy

from zope import interface 


from ore.workflow.workflow import Workflow, WorkflowInfo, Transition, NullCondition, NullAction, MANUAL, CheckerPublic
from ore.workflow import interfaces
from zope.i18nmessageid import Message


trigger_value_map = {
    'manual':interfaces.MANUAL,
    'automatic':interfaces.AUTOMATIC,
    'system':interfaces.SYSTEM
    }

GRANT = 1
DENY  = 0

def load( uri ):
    #print uri
    doc = parse( uri )
    
    return _load( doc.workflow )

def parse( uri ):
    doc = amara.parse( uri )
    return doc

def _load( workflow ):
    transitions = []
    states = []
    domain = getattr( workflow, 'domain', None )

    for s in getattr( workflow, 'state', ()):
        permissions = []
        for g in getattr( s, 'grant', () ):
            permissions.append(
                ( GRANT, g.permission, g.role )
                )
        for d in getattr( s, 'deny', () ):
            permissions.append(
                (DENY, d.permission, d.role )
                )
        state_id  = s.id #=  resolve( s.id , 'bungeni.core.workflows' )       
        states.append( State( state_id, Message(s.title, domain), permissions ) )
    
    for t in workflow.transition:
        try:
            source = t.source and t.source or None
            if source:
                tsource = source #resolve( source , 'bungeni.core.workflows' )  
            else:
                tsource = None       
            tdestination = t.destination #resolve( t.destination , 'bungeni.core.workflows' )         
            args = ( t.id, Message( t.title, domain), tsource, tdestination )
            kw = {}
        except AttributeError:
            raise SyntaxError( t.toxml() )

        # optionals
        for i in ('trigger', 'order', 'permission'):
            val = getattr( t,i,None )
            if not val:
                continue
            kw[i] = val

        if 'trigger' in kw:
            k = kw['trigger']
            v = trigger_value_map[ k ]
            kw['trigger'] = v

        # optional python resolvables
        for i in('condition', 'action', 'event'):
            val = getattr( t,i,None)
            if not val:
                continue
            val = resolve( val , 'bungeni.core.workflows' ) # raises importerror/nameerror
            kw[i] = val
        transitions.append( StateTransition( *args, **kw ) )

    return StateWorkflow( transitions, states )

class State( object ):

    def __init__( self, id, title, permissions ):
        self.id = id
        self.title = title
        self.permissions = permissions

    def initialize( self, context ):
        """ initialize content now in this state """
        _context = removeSecurityProxy(context)
        rpm = zope.securitypolicy.interfaces.IRolePermissionMap( _context )
        for action, permission, role in self.permissions:
            if action == GRANT:
               rpm.grantPermissionToRole( permission, role )
            if action == DENY:
               rpm.denyPermissionToRole( permission, role ) 

class StateTransition( Transition ):
    """
    the xml file contains the transition events as well.        
    """
    def __init__(self, transition_id, title, source, destination,
                 condition=NullCondition,
                 action=NullAction,
                 trigger=MANUAL,
                 permission=CheckerPublic,
                 order=0,
                 event=None,
                 **user_data):    
            super( StateTransition, self).__init__( transition_id, title, source, destination,
                    condition,
                    action,
                    trigger,
                    permission,
                    order=0,
                    **user_data)   
            self.event = event                 

class StateWorkflow( Workflow ):

    def __init__( self, transitions, states):
        self.refresh( transitions, states )

    def refresh( self, transitions, states=None):
        super( StateWorkflow, self).refresh( transitions )
        self.states = {}
        state_names = set()
        for s in states:
            self.states[ s.id ] = s
            state_names.add( s.id )

        # find any states given that don't match a transition state            
        t_state_names = set( [ t.destination for t in transitions] )
        t_state_names.update(
            set( [ t.source for t in transitions ] )
            )
        unreachable_states = state_names - t_state_names
        if unreachable_states:
            raise SyntaxError("Workflow Contains Unreachable States %s"%(unreachable_states ) )

class StateWorkflowInfo( WorkflowInfo ):

    #interface.implements(interfaces.IWorkflowInfo)

    def _setState( self, state_id ):
        wf = self.workflow()        
        if not isinstance( wf.workflow, StateWorkflow):
            return
        state = wf.workflow.states.get( state_id )
        if state is None:
            return
        state.initialize( self.context )

if __name__ == '__main__':
    import sys
    workflow = load( sys.argv[1] )    
    try:
        print "Transitions"
        for t in workflow._id_transitions.values():
            print  t.transition_id, "|", t.source, "->", t.destination, t.permission, t.condition, t.event

        print
        print "States"
        for s in workflow.states.values():
            print s.id, "->",  s.title
            if s.permissions:
                print " permissions"
            for p in s.permissions:
                print "  ", p
    except:
       import pdb, traceback, sys
       traceback.print_exc()
       pdb.post_mortem(   sys.exc_info()[-1] ) 

