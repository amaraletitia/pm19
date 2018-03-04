import abc
import numpy as np
from core import Machine
from core import Transition
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

    def __init__(self, num_wafer_chamber_step, dummy_threshold = 50, BOB_threshold=30, WOW_threshold=30, states=None, transitions=None):
        super(Graph, self).__init__(states, transitions)
        self.num_wafer_chamber_step = num_wafer_chamber_step
        self.dummy_threshold = dummy_threshold
        self.BOB_threshold = BOB_threshold
        self.WOW_threshold = WOW_threshold

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
                'height': '4',
                'width' : '4',
                'style': 'filled',
                'fillcolor': 'white',
                'fontsize': 60
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
                'penwidth': '15'
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
            #height = self.style_attributes['node']['default']['height']
            #width = self.style_attributes['node']['default']['width']
            fontsize = self.style_attributes['node']['default']['fontsize']
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
            container.add_node(name, shape = shape, color = color, fillcolor = fillcolor, style = style, penwidth = 10, fontsize = fontsize)
                    
            

    def _add_edges(self, events, container, num_wafer_chamber_step, Dummy_threshold=0, BOB_threshold=30, WOW_threshold=30):
        #상대적 비율에 따라 edge 자르고 가면 될듯
        
        diffs = []
        labels = []
        for event in events:
            BOB_ratio = event.BOB_count/event.count
            WOW_ratio = event.WOW_count/event.count
            diffs.append(BOB_ratio - WOW_ratio)
            labels.append(float(event.trigger))
        min_label = min(labels)
        max_label = max(labels)
        #diff.sort()
        BOB_percentile = np.percentile(diffs, 100 - BOB_threshold)
        WOW_percentile = np.percentile(diffs, WOW_threshold)

        for event in events:
            edge_threshold = num_wafer_chamber_step[event.step]
            label = float(event.trigger)
            trans_attr = str(event.attr)
            if label >=edge_threshold:
                label = str(label)
                edge_attr = {}
                try:
                    src_node = container.get_node(event.source)
                    dst_node = container.get_node(event.dest)
                except KeyError:
                    continue
                print("event count: {}, BOB_count: {}, WOW_count: {}".format(event.count, event.BOB_count, event.WOW_count))
                event.count = int(event.count)
                event.BOB_count = int(event.BOB_count)
                event.WOW_count = int(event.WOW_count)
                print("event count: {}, BOB_count: {}, WOW_count: {}".format(event.count, event.BOB_count, event.WOW_count))
                dummy_count = event.count - event.BOB_count - event.WOW_count
                dummy_ratio = dummy_count/event.count
                print("dummy ratio: {}, dummy_threshold: {}".format(dummy_ratio, Dummy_threshold))
                weight = 200
                initial_dummy = 10
                initial_BW = 10
                BW_value = initial_BW + float(label) / (max_label - min_label) * weight
                dummy_value = initial_dummy + float(label) / (max_label - min_label) * weight
                try:
                    if (event.source.split('_')[1] == 'DM' and event.dest.split('_')[1] == 'DM') | (event.source == 'START' and event.dest.split('_')[1] == 'DM') | (event.source.split('_')[1] == 'DM' and event.dest == 'END'):
                        edge_attr['color'] = 'gray'
                        edge_attr['penwidth'] = initial_dummy
                    else:
                    				
                        if dummy_ratio > Dummy_threshold*0.01:
                            edge_attr['color'] = 'gray'
                            edge_attr['penwidth'] = max(50, dummy_value)
                        else:
                            diff = event.BOB_count/event.count - event.WOW_count/event.count
                            #(해당 값 - min) / (max - min) * 30

                            if diff >= BOB_percentile:
                                edge_attr['color'] = 'navy'
                                edge_attr['penwidth'] = max(50, BW_value)
                            elif diff <= WOW_percentile:
                                edge_attr['color'] = 'red4'
                                edge_attr['penwidth'] = max(50, BW_value)
                            else:
                                edge_attr['color'] = 'gray'
                                edge_attr['penwidth'] = max(50, dummy_value)
                except IndexError:
                    if dummy_ratio > Dummy_threshold*0.01:
                        edge_attr['color'] = 'gray'
                        edge_attr['penwidth'] = max(50, dummy_value)
                    else:
                        diff = event.BOB_count/event.count - event.WOW_count/event.count
											    #(해당 값 - min) / (max - min) * 30
                        if diff >= BOB_percentile:
                            edge_attr['color'] = 'navy'
                            edge_attr['penwidth'] = max(50, BW_value)
                        elif diff <= WOW_percentile:
                            edge_attr['color'] = 'red4'
                            edge_attr['penwidth'] = max(50, BW_value)
                        else:
                            edge_attr['color'] = 'gray'
                            edge_attr['penwidth'] = max(50, dummy_value)
	                
	                 
                """
                if trans_attr == 'BOB':
                    edge_attr['color'] = 'gray'
                elif trans_attr == 'WOW':
                    edge_attr['color'] = 'gray'
                """
                #path(edge) 조건 설정 부분
                #주의:
                #elif event.WOW_count/event.BOB_count > 2:
                #ZeroDivisionError: division by zero
                """
                if event.BOB_count/event.WOW_count > 2:
                    edge_attr['color'] = 'navy'
                elif event.WOW_count/event.BOB_count > 2:
                    edge_attr['color'] = 'red4'
                """
                edge_attr['label'] = label
                #print(event.source)
                #print(event.dest)
                #print(label)
                container.add_edge(event.source, event.dest, **edge_attr)
            #else:

                #edge_attr = {}
                #edge_attr['color'] = 'white'
                #edge_attr['label'] = ''
                #edge_attr['style'] = 'invis'
                #src_node = container.get_node(event.source)
                #dst_node = container.get_node(event.dest)
                #container.add_edge(event.source, event.dest, **edge_attr)

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
        #fsm_graph.edge_attr.update(self.style_attributes['edge']['default'])
        print("EDGE attr UPDATE")

        # For each state, draw a circle
        self._add_nodes(self.states, fsm_graph)
        print("NODE UPDATE")
        self._add_edges(self.trans.copy(), fsm_graph, self.num_wafer_chamber_step, self.dummy_threshold, self.BOB_threshold, self.WOW_threshold)
        print("EDGE UPDATE")
        setattr(fsm_graph, 'style_attributes', self.style_attributes)
        print("style update")
        
        total_nodes = fsm_graph.nodes()
        print("total nodes: {}".format(total_nodes))
        outdeg = fsm_graph.out_degree()
        #print(outdeg)
        indeg = fsm_graph.in_degree()
        #print(indeg)
        zero_deg = [n for n in range(len(outdeg)) if (outdeg[n] == 0 or indeg[n] == 0)]
        print("Remove nodes: {}".format(zero_deg))
        for x in zero_deg:
            if total_nodes[x] not in ['START\n', 'END\n']:
                fsm_graph.remove_node(total_nodes[x])
        return fsm_graph

class Single_path_Graph(Machine):

    def __init__(self, num_wafer_chamber_step, states=None, transitions=None):
        super(Single_path_Graph, self).__init__(states, transitions)
        self.num_wafer_chamber_step = num_wafer_chamber_step
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
                'fontsize': 11
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
                'penwidth': '15'
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
            #height = self.style_attributes['node']['default']['height']
            #width = self.style_attributes['node']['default']['width']
            fontsize = self.style_attributes['node']['default']['fontsize']
            name = state.get_name()
            """
            step = name.split("_")[0].strip()
            step_len = len(step)
            chamber = name[step_len:]
            name = step + "\n" + chamber + "!"
            """

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
            container.add_node(name, shape = shape, color = color, fillcolor = fillcolor, style = style, penwidth = 10, fontsize = fontsize)
                    
            

    def _add_edges(self, events, container,num_wafer_chamber_step):
        #count = 0

        for event in events:
            edge_threshold = num_wafer_chamber_step[event.dest.split("_")[0].strip()]
            label = float(event.trigger)
            trans_attr = str(event.attr)
            if label >edge_threshold:
                label = str(label)
                edge_attr = {}
                try:
                    src_node = container.get_node(event.source)
                    dst_node = container.get_node(event.dest)
                except KeyError:
                    continue
                edge_attr['color'] = 'gray'
                if trans_attr == 'BOB':
                    edge_attr['color'] = 'navy'
                    edge_attr['penwidth'] = 30
                elif trans_attr == 'WOW':
                    edge_attr['color'] = 'red4'
                    edge_attr['penwidth'] = 30
                edge_attr['label'] = label
                #print(event.source)
                #print(event.dest)
                #print(label)
                #print(edge_attr)
                container.add_edge(event.source, event.dest, **edge_attr)
            else:
                edge_attr = {}
                #edge_attr['color'] = 'white'
                edge_attr['label'] = ''
                #edge_attr['style'] = 'invis'
                src_node = container.get_node(event.source)
                dst_node = container.get_node(event.dest)
                if event.status == 'valid':
                    if trans_attr == 'BOB':
                        edge_attr['color'] = 'navy'
                        edge_attr['penwidth'] = 30
                    elif trans_attr == 'WOW':
                        edge_attr['color'] = 'red4'
                        edge_attr['penwidth'] = 30
                    container.add_edge(event.source, event.dest, **edge_attr)
                
                #container.add_edge(event.source, event.dest, **edge_attr)
                

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
        self._add_edges(self.trans.copy(), fsm_graph, self.num_wafer_chamber_step)
        print("EDGE UPDATE")
        setattr(fsm_graph, 'style_attributes', self.style_attributes)
        print("style update")
        total_nodes = fsm_graph.nodes()
        print("total nodes: {}".format(total_nodes))
        outdeg = fsm_graph.out_degree()
        #print(outdeg)
        indeg = fsm_graph.in_degree()
        #print(indeg)
        zero_deg = [n for n in range(len(outdeg)) if (outdeg[n] == 0 or indeg[n] == 0)]
        print("Remove nodes: {}".format(zero_deg))
        for x in zero_deg:
            if total_nodes[x] not in ['START\n', 'END\n']:
                fsm_graph.remove_node(total_nodes[x])
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

