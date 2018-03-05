

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
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	filtering = Filtering()

	remover = Remover()
	eventlog = remover.remove_duplicate(eventlog)

	eventlog = eventlog.calculate_execution_time()
	eventlog = eventlog.calculate_relative_time()

	CV = ChartVisualizer()
	CV.produce_dotted_chart(eventlog, _type = 'RESOURCE', _time = 'relative')
