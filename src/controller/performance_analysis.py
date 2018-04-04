

import sys
import os
import signal
import pandas as pd
sys.path.append(os.path.abspath(("../../../")))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader

from PyProM.src.visualization.chart_visualization import ChartVisualizer

import multiprocessing



if __name__ == '__main__':
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Documents/example/repairExample.txt')
	eventlog = eventlog.assign_caseid('Case ID')
	eventlog = eventlog.assign_activity('Activity')
	eventlog = eventlog.assign_resource('Resource')
	eventlog = eventlog.assign_timestamp('Complete Timestamp')
	eventlog = eventlog.clear_columns()

	eventlog = eventlog.calculate_execution_time()
	result = eventlog.analyze_performance(value = 'execution_time',dim_1='RESOURCE', dim_2='ACTIVITY', metric = 'frequency_per_case')
	CV = ChartVisualizer()
	CV.produce_nested_bar(result)
