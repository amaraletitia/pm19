import networkx as nx
from networkx.drawing.nx_agraph import write_dot, read_dot, graphviz_layout, pygraphviz_layout

import sys
import os
import signal
import pandas as pd
sys.path.append(os.path.abspath("../data"))
from Eventlog import Eventlog
from xes_reader import XesReader

sys.path.append(os.path.abspath("../preprocessing"))
from preprocess import Remover
from preprocess import Transformer
from preprocess import Filtering

sys.path.append(os.path.abspath("../analysis"))
from classifier import Classifier
from stat_analysis import StatAnalyzer
from simplification import Simplification

sys.path.append(os.path.abspath("../mining"))
from transition_matrix import TransitionMatrix
from dependency_graph import DependencyGraph
from heuristic_miner import HeuristicMiner

sys.path.append(os.path.abspath(("../model")))
from bokeh_fsm import FSM_Miner

import multiprocessing



if __name__ == '__main__':
	#eventlog
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	#preprocessing
	filtering = Filtering()
	remover = Remover()
	eventlog = remover.remove_duplicate(eventlog)

	#Transition Matrix
	TM = TransitionMatrix()
	transition_matrix = TM.get_transition_matrix(eventlog, 4, type='sequence', horizon=2)
	transition_matrix = TM.annotate_transition_matrix(eventlog, 4, transition_matrix)

	#FSM model
	fsm = FSM_Miner()
	fsm_graph = fsm._create_graph(transition_matrix)
	fsm.get_graph_info(fsm_graph)
	write_dot(fsm_graph,'test.dot')
	fsm_graph = read_dot('test.dot')
	from networkx.readwrite import json_graph
	print(json_graph.node_link_data(fsm_graph))
	#layout =graphviz_layout(fsm_graph, prog='dot')
	#print(layout)
	from bokeh.models import ColumnDataSource, LabelSet

	nodes, nodes_coordinates = zip(*sorted(layout.items()))
	nodes_xs, nodes_ys = list(zip(*nodes_coordinates))
	nodes_source = ColumnDataSource(dict(x=nodes_xs, y=nodes_ys, name=nodes))

	from bokeh.plotting import show, figure
	from bokeh.models import HoverTool

	hover = HoverTool(tooltips=[('name', '@name'), ('id', '$index')])
	plot = figure(sizing_mode='stretch_both',
	              tools=['tap', hover, 'box_zoom', 'reset', 'wheel_zoom'])
	r_circles = plot.circle('x', 'y', source=nodes_source, size=20,color='blue', level = 'overlay', alpha = 0.8)
	labels = LabelSet(x='x', y='y', text='name', level='glyph', x_offset=5, y_offset=5, source=nodes_source,render_mode='canvas', text_font_size="5pt")

	def get_edges_specs(_network, _layout):
	    d = dict(xs=[], ys=[])
	    #weights = [d['weight'] for u, v, d in _network.edges(data=True)]
	    #max_weight = max(weights)
	    #calc_alpha = lambda h: 0.1 + 0.6 * (h / max_weight)

	    # example: { ..., ('user47', 'da_bjoerni', {'weight': 3}), ... }
	    for u, v, data in _network.edges(data=True):
	        d['xs'].append([_layout[u][0], _layout[v][0]])
	        d['ys'].append([_layout[u][1], _layout[v][1]])
	        #d['alphas'].append(calc_alpha(data['weight']))
	    return d

	edges = get_edges_specs(fsm_graph, layout)
	lines_source = ColumnDataSource(edges)
	print(edges)
	from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead

	for i in range(len(edges['ys'])):
		plot.add_layout(Arrow(end=VeeHead(size=5), x_start=edges['xs'][i][0], y_start=edges['ys'][i][0], x_end=edges['xs'][i][1], y_end = edges['ys'][i][1]))
	#r_lines = plot.multi_line('xs', 'ys', line_width=1.5, color='navy', source=lines_source)
	plot.add_layout(labels)
	show(plot)

