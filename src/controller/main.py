
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
from fsm import FSM_Miner

sys.path.append(os.path.abspath(("../visualization")))
from svg_widget import Visualization
from chart_visualization import ChartVisualizer

from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import multiprocessing



if __name__ == '__main__':
	#eventlog = Eventlog.from_txt('/Volumes/GoogleDrive/내 드라이브/framework/src/data/example/Sample_data.txt')

	eventlog = Eventlog.from_txt("/Users/GYUNAM/Documents/example/Sample_data.txt")
	eventlog = eventlog.assign_caseid('ROOT_LOT_ID', 'WAFER_ID')
	eventlog = eventlog.assign_activity('STEP_SEQ')
	eventlog = eventlog.assign_resource('EQP_ID', 'CHAMBER_ID')
	eventlog = eventlog.join_columns('RESOURCE', 'ACTIVITY', 'RESOURCE')
	eventlog = eventlog.assign_timestamp('TKIN_TIME', 'TKOUT_TIME')
	#print(eventlog)

	filtering = Filtering()

	def _count(x):
		x = list(set(x))
		return len(x)
	steps = eventlog.groupby('ACTIVITY').RESOURCE.apply(list).apply(_count)
	steps = [step for step in steps.index if 50 < steps[step] < 130]
	print(steps)
	eventlog = filtering.filter_activity(eventlog, steps)
	#eventlog = filtering.filter_eqp(eventlog, 20)
	#chamber filtering 후에 RESOURCE 재생성
	eventlog = eventlog.assign_resource('EQP_ID', 'CHAMBER_ID')
	eventlog = eventlog.join_columns('RESOURCE', 'ACTIVITY', 'RESOURCE')

	remover = Remover()
	#remover = remove()
	eventlog = remover.remove_duplicate(eventlog)
	eventlog = remover.remove_duplicates_except_one(eventlog)
	eventlog = remover.remove_duplicate_chambers(eventlog)
	eventlog = remover.remove_multiple_value(eventlog,'VALUE')
	#eventlog = remover.remove_incomplete_wafer(eventlog, 'STEP_001', 'STEP_118', 'STEP_SEQ')
	#eventlog = remover.remove_incomplete_wafer(eventlog, 'STEP_001', 'STEP_075')
	#eventlog = remover.remove_incomplete_lot(eventlog,20)
	print("Length of steps: {}".format(len(steps)))
	#eventlog = remover.remove_incomplete_flow(eventlog, len(steps))
	#eventlog = remover.remove_diff_flow(eventlog)



	transformer = Transformer()
	wafer_data = transformer.produce_wafer_data(eventlog)
	sorted_wafer_data = wafer_data.sort_values(by=['CASE_ID', 'ACTIVITY'])
	sorted_wafer_data.to_csv('../result/wafer_data.csv', sep = ',')
	sorted_wafer_data.describe()

	#Transition Matrix
	TM = TransitionMatrix()
	transition_matrix = TM.get_transition_matrix(sorted_wafer_data, 4, type='sequence', horizon=1, target = 'RESOURCE')
	#simplified_annotated_transition_matrix = Simplification().by_inout(transition_matrix, analysis_result)
	fsm = FSM_Miner()
	fsm_graph = fsm._create_graph(transition_matrix)
	fsm.get_graph_info(fsm_graph)
	dot = fsm.get_dot(fsm_graph)

	app = QtWidgets.QApplication(sys.argv)


	window = Visualization()
	window.show()

	#for path in app.arguments()[1:]:
	window.load('../result/state_svg.svg');

	sys.exit(app.exec_())
