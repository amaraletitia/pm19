import abc

from core_test import Machine
from core_test import Transition
try:
    import pygraphviz as pgv
except ImportError:  # pragma: no cover
    pgv = None

import logging
from functools import partial
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Diagram(object):

    def __init__(self, machine):
        self.machine = machine

    @abc.abstractmethod
    def get_graph(self):
        raise Exception('Abstract base Diagram.get_graph called!')


class Graph(Machine):

    def __init__(self, states=None, transitions=None):
        super(Graph, self).__init__(states, transitions)

    machine_attributes = {
        'directed': True,
        'strict': False,
        'rankdir': 'LR',
        'ratio': '0.3',
        'ranksep': '7 equally'
    }

    style_attributes = {
        'node': {
            'default': {
                'shape': 'circle',
                'height': '2',
                'width' : '2',
                'style': 'filled',
                'fillcolor': 'white',
                #'color': 'black',
            },
            'DUMMY': {
                'color': 'gray',
                'fillcolor': 'gray'
            },
            'HIGH': {
                'fillcolor': 'lightblue',
                #'fillcolor': 'darksalmon',
                #'shape': 'doublecircle'
            },
            'LOW': {
                'fillcolor': 'lightpink'
                #'color': 'blue',
                #'fillcolor': 'azure2',
            },
            'BOB': {
                'color': 'navy'
            },
            'WOW': {
                'color': 'red4'
            },
            'B/W':{
                'color': 'lightgoldenrod'
            }
        },
        'edge': {
            'default': {
                'color': 'black',
                'penwidth': '7'
            },
            'previous': {
                'color': 'blue'
            }
        },
        'graph': {
            'default': {
                'color': 'black',
                'fillcolor': 'white'
            },
            'previous': {
                'color': 'blue',
                'fillcolor': 'azure2',
                'style': 'filled'
            },
            'active': {
                'color': 'red',
                'fillcolor': 'darksalmon',
                'style': 'filled'
            },
        }
    }

    

    def _add_nodes(self, states, container):
        for key, state in states.items():
            shape = self.style_attributes['node']['default']['shape']
            style = self.style_attributes['node']['default']['style']
            height = self.style_attributes['node']['default']['height']
            width = self.style_attributes['node']['default']['width']
            name = state.get_name()
            status = state.get_status()
            path = state.get_path()
            #container.add_node(name, shape=shape, color='black')
            if status == '0':
                #container.add_node(name, shape=shape, color='black')
                fillcolor = self.style_attributes['node']['DUMMY']['fillcolor']
            elif status == 'HIGH':
                fillcolor = self.style_attributes['node']['HIGH']['fillcolor']
                #container.add_node(name, shape=shape, color='blue')
            elif status == 'LOW':
                fillcolor = self.style_attributes['node']['LOW']['fillcolor']
                #container.add_node(name, shape=shape, color='red')

            if path == '0':
                color = self.style_attributes['node']['DUMMY']['color']
            elif path == 'BOB':
                color = self.style_attributes['node']['BOB']['color']
            elif path == 'WOW':
                color = self.style_attributes['node']['WOW']['color']
            elif path == 'B/W':
                color = self.style_attributes['node']['B/W']['color']
            #container.add_node(name, shape = shape, color = color, fillcolor = fillcolor, style = style, penwidth = 10, height = height, width = width, fixedsize = True)
            container.add_node(name, shape = shape, color = color, fillcolor = fillcolor, style = style)
                    
            

    def _add_edges(self, events, container):
        #count = 0

        for event in events:
            #count+=1
            #print(count)
            label = float(event.trigger)
            trans_attr = str(event.attr)
            #실제 구현 시에는 slider로 조절.
            if label >0:
                label = str(label)
                edge_attr = {}
                src_node = container.get_node(event.source)
                dst_node = container.get_node(event.dest)
                edge_attr['color'] = 'gray'
                if trans_attr == 'BOB':
                    edge_attr['color'] = 'navy'
                elif trans_attr == 'WOW':
                    edge_attr['color'] = 'red4'
                edge_attr['label'] = label
                container.add_edge(event.source, event.dest, **edge_attr)
                """
                if self._omit_auto_transitions(event, label):
                    continue

                for transitions in event.transitions.items():
                    print(transitions)
                    src = transitions[0]
                    edge_attr = {}
                    src_node = container.get_node(src)
                    for t in transitions[1]:
                        dst = t.dest
                        dst_node = container.get_node(dst)
                        edge_attr['color'] = 'gray'
                        if trans_attr == 'BOB':
                            edge_attr['color'] = 'navy'
                        elif trans_attr == 'WOW':
                            print(transitions)
                            edge_attr['color'] = 'red4'
                        
                        edge_attr['label'] = label
                        #print(type(label))
                        if container.has_edge(src, dst):
                            edge = container.get_edge(src, dst)
                            edge.attr['label'] = edge.attr['label'] + ' | ' + edge_attr['label']
                        else:
                            container.add_edge(src, dst, **edge_attr)
                """
                #print(transitions)

    def _omit_auto_transitions(self, event, label):
        return self._is_auto_transition(event, label) and not self.machine.show_auto_transitions

    # auto transition events commonly a) start with the 'to_' prefix, followed by b) the state name
    # and c) contain a transition from each state to the target state (including the target)
    def _is_auto_transition(self, event, label):
        if label.startswith('to_') and len(event.transitions) == len(self.machine.states):
            state_name = label[len('to_'):]
            if state_name in self.machine.states:
                return True
        return False

    def rep(self, f):
        return f.__name__ if callable(f) else f

    def _transition_label(self, edge_label, tran):
        if self.machine.show_conditions and tran.conditions:
            return '{edge_label} [{conditions}]'.format(
                edge_label=edge_label,
                conditions=' & '.join(
                    self.rep(c.func) if c.target else '!' + self.rep(c.func)
                    for c in tran.conditions
                ),
            )
        return edge_label

    def get_graph(self, title=None):
        print("NOW PRINT")
        """ Generate a DOT graph with pygraphviz, returns an AGraph object
        Args:
            title (string): Optional title for the graph.
        """
        if not pgv:  # pragma: no cover
            raise Exception('AGraph diagram requires pygraphviz')

        if title is False:
            title = ''

        fsm_graph = pgv.AGraph(label=title, compound=True, **self.machine_attributes)
        print("AGRAPH")
        fsm_graph.node_attr.update(self.style_attributes['node']['default'])
        print("NODE attr UPDATE")
        fsm_graph.edge_attr.update(self.style_attributes['edge']['default'])
        print("EDGE attr UPDATE")

        # For each state, draw a circle
        self._add_nodes(self.states, fsm_graph)
        print("NODE UPDATE")
        self._add_edges(self.trans.copy(), fsm_graph)
        print("EDGE UPDATE")
        setattr(fsm_graph, 'style_attributes', self.style_attributes)
        print("style update")
        #print(self.machine_attributes)
        return fsm_graph


class GraphMachine(Machine):
    _pickle_blacklist = ['graph']

    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if k not in self._pickle_blacklist}

    def __setstate__(self, state):
        self.__dict__.update(state)
        for model in self.models:
            graph = self._get_graph(model, title=self.title)
            self.set_node_style(graph, model.state, 'active')

    def __init__(self, *args, **kwargs):
        # remove graph config from keywords
        self.title = kwargs.pop('title', 'State Machine')
        self.show_conditions = kwargs.pop('show_conditions', False)
        self.show_auto_transitions = kwargs.pop('show_auto_transitions', False)

        super(GraphMachine, self).__init__(*args, **kwargs)

        # Create graph at beginning
        for model in self.models:
            if hasattr(model, 'get_graph'):
                raise AttributeError('Model already has a get_graph attribute. Graph retrieval cannot be bound.')
            setattr(model, 'get_graph', partial(self._get_graph, model))
            model.get_graph()
            #self.set_node_state(model.graph, self.initial, 'active')

        # for backwards compatibility assign get_combined_graph to get_graph
        # if model is not the machine
        if not hasattr(self, 'get_graph'):
            setattr(self, 'get_graph', self.get_combined_graph)


    def _get_graph(self, model, title=None, force_new=False, show_roi=False):
        if title is None:
            title = self.title
        if not hasattr(model, 'graph') or force_new:
            
            model.graph = Graph(self).get_graph(title)
            #self.set_node_state(model.graph, model.state, state='active')

        return model.graph if not show_roi else self._graph_roi(model)

    def get_combined_graph(self, title=None, force_new=False, show_roi=False):
        logger.info('Returning graph of the first model. In future releases, this ' +
                    'method will return a combined graph of all models.')
        return self._get_graph(self.models[0], title, force_new, show_roi)

    def set_edge_state(self, graph, edge_from, edge_to, state='default', label=None):
        """ Mark a node as active by changing the attributes """
        if not self.show_auto_transitions and not graph.has_edge(edge_from, edge_to):
            graph.add_edge(edge_from, edge_to, label)
        edge = graph.get_edge(edge_from, edge_to)
        self.set_edge_style(graph, edge, state)

    def add_states(self, *args, **kwargs):
        super(GraphMachine, self).add_states(*args, **kwargs)
        for model in self.models:
            model.get_graph(force_new=True)

    def add_transition(self, *args, **kwargs):
        super(GraphMachine, self).add_transition(*args, **kwargs)
        for model in self.models:
            model.get_graph(force_new=True)

    def reset_graph(self, graph):
        # Reset all the edges
        for e in graph.edges_iter():
            self.set_edge_style(graph, e, 'default')
        for n in graph.nodes_iter():
            if 'point' not in n.attr['shape']:
                self.set_node_style(graph, n, 'default')
        for g in graph.subgraphs_iter():
            self.set_graph_style(graph, g, 'default')

    def set_node_state(self, graph, node_name, state='default'):
        if graph.has_node(node_name):
            node = graph.get_node(node_name)
            func = self.set_node_style
        else:
            node = graph
            node = _get_subgraph(node, 'cluster_' + node_name)
            func = self.set_graph_style
        func(graph, node, state)

    @staticmethod
    def _graph_roi(model):
        g = model.graph
        filtered = g.copy()

        kept_nodes = set()
        active_state = model.state if g.has_node(model.state) else model.state + '_anchor'
        kept_nodes.add(active_state)

        # remove all edges that have no connection to the currently active state
        for e in filtered.edges():
            if active_state not in e:
                filtered.delete_edge(e)

        # find the ingoing edge by color; remove the rest
        for e in filtered.in_edges(active_state):
            if e.attr['color'] == g.style_attributes['edge']['previous']['color']:
                kept_nodes.add(e[0])
            else:
                filtered.delete_edge(e)

        # remove outgoing edges from children
        for e in filtered.out_edges_iter(active_state):
            kept_nodes.add(e[1])

        for n in filtered.nodes():
            if n not in kept_nodes:
                filtered.delete_node(n)

        return filtered

    @staticmethod
    def set_node_style(graph, node_name, style='default'):
        node = graph.get_node(node_name)
        style_attr = graph.style_attributes.get('node', {}).get(style)
        node.attr.update(style_attr)

    @staticmethod
    def set_edge_style(graph, edge, style='default'):
        style_attr = graph.style_attributes.get('edge', {}).get(style)
        edge.attr.update(style_attr)

    @staticmethod
    def set_graph_style(graph, item, style='default'):
        style_attr = graph.style_attributes.get('graph', {}).get(style)
        item.graph_attr.update(style_attr)

    @staticmethod
    def _create_transition(*args, **kwargs):
        return TransitionGraphSupport(*args, **kwargs)


class TransitionGraphSupport(Transition):

    def _change_state(self, event_data):
        machine = event_data.machine
        model = event_data.model
        dest = machine.get_state(self.dest)

        # Mark the active node
        machine.reset_graph(model.graph)

        # Mark the previous node and path used
        if self.source is not None:
            source = machine.get_state(self.source)
            machine.set_node_state(model.graph, source.name,
                                   state='previous')
            machine.set_node_state(model.graph, dest.name, state='active')

            if hasattr(source, 'children') and len(source.children) > 0:
                source = source.name + '_anchor'
            else:
                source = source.name
            if hasattr(dest, 'children') and len(dest.children) > 0:
                dest = dest.name + '_anchor'
            else:
                dest = dest.name
            machine.set_edge_state(model.graph, source, dest,
                                   state='previous', label=event_data.event.name)

        super(TransitionGraphSupport, self)._change_state(event_data)


def _get_subgraph(g, name):
    sg = g.get_subgraph(name)
    if sg:
        return sg
    for sub in g.subgraphs_iter():
        sg = _get_subgraph(sub, name)
        if sg:
            return sg
    return None
