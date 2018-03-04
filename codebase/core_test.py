
try:
    from builtins import object
except ImportError:
    # python2
    pass
import inspect
import itertools
import logging

from collections import OrderedDict
from collections import defaultdict
from collections import deque
from functools import partial
from six import string_types

import warnings
warnings.simplefilter('default')

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
class State(object):

    def __init__(self, name):
        """
        Args:
            name (string): The name of the state
        """
        self.name = name[0]
        self.status = name[1]
        self.path = name[2]

    def get_status(self):
        return self.status

    def get_name(self):
        return self.name

    def get_path(self):
        return self.path

    def __repr__(self):
        return "<%s('%s', '%s')@%s>" % (type(self).__name__, self.name, self.status, id(self))


class Transition(object):

    def __init__(self, source, dest):
        """
        Args:
            source (string): The name of the source State.
            dest (string): The name of the destination State.
        """
        self.source = source
        self.dest = dest

class Transitions(object):

    def __init__(self, source, dest, attr, trigger):
        """
        Args:
            source (string): The name of the source State.
            dest (string): The name of the destination State.
        """
        self.source = source
        self.dest = dest
        self.attr = attr
        self.trigger = trigger

def listify(obj):
    if obj is None:
        return []
    else:
        return obj if isinstance(obj, (list, tuple, type(None))) else [obj]


class Event(object):

    def __init__(self, attr, name, machine):
        """
        Args:
            name (string): The name of the event, which is also the name of the
                triggering callable (e.g., 'advance' implies an advance()
                method).
            machine (Machine): The current Machine instance.
        """
        self.attr = attr
        self.name = name
        self.machine = machine
        self.transitions = defaultdict(list)

    def add_transition(self, transition):
        """ Add a transition to the list of potential transitions.
        Args:
            transition (Transition): The Transition instance to add to the
                list.
        """
        #print(transition)
        self.transitions[transition.source].append(transition)

    

    
    def __repr__(self):
        return "<%s('%s')@%s>" % (type(self).__name__, self.name, id(self))

    

class Machine(object):

    # Callback naming parameters

    callbacks = ['before', 'after', 'prepare', 'on_enter', 'on_exit']
    separator = '_'
    wildcard_all = '*'
    wildcard_same = '='  
    """
    Args:
        model (object): The object(s) whose states we want to manage. If 'self',
            the current Machine instance will be used the model (i.e., all
            triggering events will be attached to the Machine itself).
        states (list): A list of valid states. Each element can be either a
            string or a State instance. If string, a new generic State
            instance will be created that has the same name as the string.
        transitions (list): An optional list of transitions. Each element
            is a dictionary of named arguments to be passed onto the
            Transition initializer.

        **kwargs additional arguments passed to next class in MRO. This can be ignored in most cases.
    """
    def __init__(self, states=None, transitions=None):
        #부모 클래스 한번만 호출
        
        super(Machine, self).__init__()

        self.states = OrderedDict()
        self.trans = []
        self.events = {}
        self.id = ""

        self.models = []


        if states is not None:
            self.add_states(states)

        if transitions is not None:
            transitions = listify(transitions)
            for t in transitions:
                #transitions as input: dictionary or list
                if isinstance(t, list):
                    self.add_transition(*t)
                else:
                    self.add_transition(**t)



    def get_states(self):
        return self.states

    @staticmethod
    def _create_transition(*args, **kwargs):
        return Transition(*args, **kwargs)

    @staticmethod
    def _create_event(*args, **kwargs):
        return Event(*args, **kwargs)

    @staticmethod
    def _create_state(*args, **kwargs):
        return State(*args, **kwargs)

    def get_state(self, state):
        """ Return the State instance with the passed name. """
        if state not in self.states:
            raise ValueError("State '%s' is not a registered state." % state)
        return self.states[state]

    def add_state(self, *args, **kwargs):
        """ Alias for add_states. """
        self.add_states(*args, **kwargs)

    def add_states(self, states):
        """ Add new state(s).
        Args:
            state (list, string, dict, or State): a list, a State instance, the
                name of a new state, or a dict with keywords to pass on to the
                State initializer. If a list, each element can be of any of the
                latter three types.
        """
        states = listify(states)
        for instance in states:
            
            state = self._create_state(instance)
            self.states[instance[0]] = state

            
    def add_transition(self, attr, trigger, source, dest, **kwargs):
        """ Create a new Transition instance and add it to the internal list.
        Args:
            trigger (string): The name of the method that will trigger the
                transition. This will be attached to the currently specified
                model (e.g., passing trigger='advance' will create a new
                advance() method in the model that triggers the transition.)
            source(string): The name of the source state--i.e., the state we
                are transitioning away from. This can be a single state, a
                list of states or an asterisk for all states.
            dest (string): The name of the destination State--i.e., the state
                we are transitioning into. This can be a single state or an
                equal sign to specify that the transition should be reflexive
                so that the destination will be the same as the source for
                every given source.
            **kwargs: Additional arguments which can be passed to the created transition.
                This is useful if you plan to extend Machine.Transition and require more parameters.
        """
        self.trans.append(Transitions(source, dest, attr, trigger))
        if trigger not in self.events:
            self.events[trigger] = self._create_event(attr, trigger, self)

        if isinstance(source, string_types):
            source = list(self.states.keys()) if source == self.wildcard_all else [source]
        else:
            source = [s.name if self._has_state(s) else s for s in listify(source)]

        for s in source:
            d = s if dest == self.wildcard_same else dest
            if self._has_state(d):
                d = d.name
            t = self._create_transition(s, d, **kwargs)
            #self.events[trigger].add_transition(t)

        

    def _has_state(self, s):
        if isinstance(s, State):
            if s in self.states.values():
                return True
            else:
                raise ValueError('State %s has not been added to the machine' % s.name)
        else:
            return False


    def __getattr__(self, name):
        # Machine.__dict__ does not contain double underscore variables.
        # Class variables will be mangled.
        if name.startswith('__'):
            raise AttributeError("'{}' does not exist on <Machine@{}>"
                                 .format(name, id(self)))
        # Nothing matched
        raise AttributeError("'{}' does not exist on <Machine@{}>".format(name, id(self)))

class MachineError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
