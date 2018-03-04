

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
from transition_matrix import AnnotatedTransitionMatrix

sys.path.append(os.path.abspath(("../model")))
from fsm import FSM

sys.path.append(os.path.abspath(("../visualization")))
from svg_widget import Visualization

from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import multiprocessing



if __name__ == '__main__':
	#eventlog = Eventlog.from_txt('/Volumes/GoogleDrive/내 드라이브/framework/src/data/example/Sample_data.txt')

	eventlog = Eventlog.from_txt('/Volumes/GoogleDrive/내 드라이브/framework/src/data/example/raw_data.txt')
	eventlog = eventlog.assign_caseid('ROOT_LOT_ID', 'WAFER_ID')
	eventlog = eventlog.assign_activity('STEP_SEQ')
	eventlog = eventlog.assign_resource('EQP_ID', 'CHAMBER_ID')
	eventlog = eventlog.join_columns('RESOURCE', 'ACTIVITY', 'RESOURCE')
	eventlog = eventlog.assign_timestamp('TKIN_TIME', 'TKOUT_TIME')
	#print(eventlog)

	filtering = Filtering()
	#steps = ['STEP_001', 'STEP_002', 'STEP_003', 'STEP_004', 'STEP_005', 'STEP_006', 'STEP_007', 'STEP_008', 'STEP_009', 'STEP_010', 'STEP_011', 'STEP_012', 'STEP_013', 'STEP_014', 'STEP_015', 'STEP_016', 'STEP_017', 'STEP_018', 'STEP_019', 'STEP_020', 'STEP_021', 'STEP_022', 'STEP_023', 'STEP_024', 'STEP_025', 'STEP_026', 'STEP_027', 'STEP_028', 'STEP_029', 'STEP_030', 'STEP_031', 'STEP_032', 'STEP_033', 'STEP_034', 'STEP_035', 'STEP_036']
	steps = []
	for i in range(76):
		if i == 41 or i == 0:
			continue
		if i < 10:
			steps.append("STEP_00{}".format(i))
		if i >= 10:
			steps.append("STEP_0{}".format(i))
		#steps.append("STEP_{}".format())
	#print(steps)
	eventlog = filtering.filter_activity(eventlog, steps)
	eventlog = filtering.filter_eqp(eventlog, 20)
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
	eventlog = remover.remove_incomplete_wafer(eventlog, 'STEP_001', 'STEP_075')
	#eventlog = remover.remove_incomplete_lot(eventlog,20)
	print("Length of steps: {}".format(len(steps)))
	eventlog = remover.remove_incomplete_flow(eventlog, len(steps))
	eventlog = remover.remove_diff_flow(eventlog)



	transformer = Transformer()
	wafer_data = transformer.produce_wafer_data(eventlog)
	sorted_wafer_data = wafer_data.sort_values(by=['CASE_ID', 'ACTIVITY'])
	sorted_wafer_data.to_csv('../result/wafer_data.csv', sep = ',')
	sorted_wafer_data.describe()

	classifier = Classifier()
	BOB_criterion, WOW_criterion = classifier.relative_ratio_criterion(wafer_data, 70, 30)
	BG, WG = classifier.produce_wafer_BOB_WOW_group(wafer_data, BOB_criterion, WOW_criterion)



	"""
	stat_analyzer = StatAnalyzer(wafer_data)
	result = stat_analyzer.produce_KS_test()
	result = stat_analyzer.produce_ANOVA_test()
	result = stat_analyzer.produce_stat_analysis(0.05, 0.05)
	result.to_csv('../result/sample_analysis_result.csv', sep = ',')
	"""


	#transition_matrix = TransitionMatrix(eventlog).get_transition_matrix()
	analysis_result = pd.read_csv('../result/analysis_result.csv')

	annotated_transition_matrix = AnnotatedTransitionMatrix().get_annotated_transition_matrix(wafer_data, multiprocessing.cpu_count())
	#annotated_transition_matrix = AnnotatedTransitionMatrix().produce_annotated_transition_matrix(wafer_data)
	simplified_annotated_transition_matrix = Simplification().by_inout(annotated_transition_matrix, analysis_result)
	fsm = FSM(simplified_annotated_transition_matrix, analysis_result, BG, WG)
	fsm_graph = fsm.get_fsm()
	fsm.get_graph_info()
	dot = fsm.get_dot()

	app = QtWidgets.QApplication(sys.argv)


	window = Visualization()
	window.show()

	#for path in app.arguments()[1:]:
	window.load('../result/state_svg.svg');

	sys.exit(app.exec_())
