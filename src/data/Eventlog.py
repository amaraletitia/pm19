import pandas as pd
import numpy as np
import multiprocessing
from multiprocessing import Process, Manager, Queue
import math

from PyProM.src.data.importing import Import
from PyProM.src.data.xes_reader import XesReader

import sys
import os
from PyProM.src.utility.util_profile import Util_Profile
from PyProM.src.utility.util_multiprocessing import Util_Multiprocessing
import time
from functools import wraps

def timefn(fn):
	@wraps(fn)
	def measure_time(*args, **kwargs):
		t1 = time.time()
		result = fn(*args, **kwargs)
		t2 = time.time()
		print("@timefn: {} took {} seconds".format(fn.__name__, t2-t1))
		return result
	return measure_time


timefn = Util_Profile.timefn
class Eventlog(pd.DataFrame):
	"""docstring for Eventlog"""
	_columns = []
	def __init__(self, *args, **kwargs):
		super(Eventlog, self).__init__(*args, **kwargs)


	@property
	def _constructor(self):
		return Eventlog

	@classmethod
	def from_xes(cls, path):
		_import = Import(path, format='xes')
		dict_eventlog = _import.eventlog
		if isinstance(dict_eventlog, dict):
			print("import dict and produce eventlog")
			df =  Eventlog.from_dict(dict_eventlog)
			return df

	@classmethod
	def from_txt(cls, path):
		df = pd.read_csv(path, sep = '\t', index_col = False, dtype={'ROOT_LOT_ID':'str', 'WAFER_ID':'str', 'STEP_SEQ':'str', 'TKIN_TIME':'str', 'TKOUT_TIME':'str', 'EQP_ID':'str', 'EQP_MODEL_NAME':'str', 'PPID':'str', 'CHAMBER_ID':'str', 'UNIT_ID':'str', 'VALUE':'float'})
		return Eventlog(df)

	"""
	def __call__(self, path, format='xes'):
		if format == 'xes':
			_import = Import(path, format='xes')
			dict_eventlog = _import.eventlog
			return self.dict_to_dataframe(dict_eventlog)

		if format == 'txt':
			return self.csv_to_dataframe(path)
	"""
	@timefn
	def assign_caseid(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['CASE_ID'] = self[arg]
			else:
				self['CASE_ID'] += '_' + self[arg]
			#del self[arg]
			count +=1
		self._columns.append('CASE_ID')
		return self

	@timefn
	def assign_activity(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['ACTIVITY'] = self[arg]
			else:
				self['ACTIVITY'] += '_' + self[arg]
			#del self[arg]
			count +=1
		self._columns.append('ACTIVITY')
		return self

	@timefn
	def assign_resource(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['RESOURCE'] = self[arg]
			else:
				self['RESOURCE'] += '_' + self[arg]
			#del self[arg]
			count +=1
		self._columns.append('RESOURCE')
		return self

	@timefn
	def assign_timestamp(self, *args, format = '%Y/%m/%d %H:%M:%S'):
		if len(args) == 1:
			self['TIMESTAMP'] = pd.to_datetime(self[args[0]], format=format)
			self._columns.append('TIMESTAMP')
		if len(args) == 2:
			self['TIMESTAMP'] = pd.to_datetime(self[args[0]], format=format)
			self['TIMESTAMP_COMPLETE'] = pd.to_datetime(self[args[1]], format=format)
			self._columns.append('TIMESTAMP')
			self._columns.append('TIMESTAMP_COMPLETE')
		self = self.sort_values(by=['CASE_ID', 'TIMESTAMP'])

		return self

	def assign_cluster(self, *args):
		count = 0
		for arg in args:
			if count == 0:
				self['Cluster'] = self[arg].astype(str)
			else:
				self['Cluster'] += '_' + self[arg].astype(str)
			#del self[arg]
			count +=1
		self._columns.append('Cluster')
		return self

	def clear_columns(self, *args):

		return self[self._columns]



	def join_columns(self, col_name, *args):
		if len(args) < 2:
			print("join_columns requires at least 2 columns")
		count = 0
		tmp = self.copy(deep=True)
		for arg in args:
			if count == 0:
				self[col_name] = tmp[arg]
			else:
				self[col_name] += '/' + tmp[arg]
			#del self[arg]
			count +=1
		return self

	"""
	utility functions
	"""
	def get_event_trace(self, workers, value = 'ACTIVITY'):
		output = self.parallelize(self._get_event_trace, workers, value)
		event_trace = Util_Multiprocessing.join_dict(output)
		return event_trace

	def _get_event_trace(self, eventlog, x, value='ACTIVITY'):
		event_trace = dict()
		caseid = eventlog.get_first_caseid()
		count = 0
		for instance in eventlog.itertuples():
			index = instance.Index
			if value == 'ACTIVITY':
				ai = eventlog.get_activity_by_index(index)
			elif value == 'RESOURCE':
				ai = eventlog.get_resource_by_index(index)
			elif value == 'TIMESTAMP':
				ai = eventlog.get_timestamp_by_index(index)
			if index == 0:
				event_trace[instance.CASE_ID] = [ai]
				continue

			caseid = eventlog.get_caseid_by_index(index-1)

			if instance.CASE_ID == caseid:
				event_trace[instance.CASE_ID].append(ai)

			else:
				event_trace[instance.CASE_ID] = [ai]


		print("Finish")

		x.append(event_trace)

	def _get_trace_count(self, event_trace):
		trace_count = dict()
		traces = event_trace.values()
		for trace in traces:
			trace = tuple(trace)
			if trace not in trace_count:
				trace_count[trace] = 0
			trace_count[trace] += 1
		return trace_count




	def get_activities(self):
		unique_activities = self['ACTIVITY'].unique()
		return unique_activities

	def get_timestamps(self):
		unique_timestamps = self['TIMESTAMP'].unique()
		return unique_timestamps

	def get_caseids(self):
		unique_caseids = self['CASE_ID'].unique()
		return unique_caseids

	def get_first_caseid(self):
		return self['CASE_ID'][0]

	def get_caseid_by_index(self,index):
		return self['CASE_ID'][index]

	def get_resource_by_index(self, index):
		return self['RESOURCE'][index]

	def get_activity_by_index(self, index):
		return self['ACTIVITY'][index]

	def get_timestamp_by_index(self, index):
		return self['TIMESTAMP'][index]




	def filter(self, criterion, value):
		return self.loc[self[criterion] == value, :]


	def calculate_execution_time(self, unit='hour'):
		execution_times = []
		caseid = self.get_first_caseid()
		count = 0

		for instance in self.itertuples():
			index = instance.Index
			if index == 0:
				execution_times.append(float('nan'))
				continue
			previous_caseid = self.get_caseid_by_index(index-1)
			if instance.CASE_ID == previous_caseid:
				execution_time = self.get_timestamp_by_index(index) - self.get_timestamp_by_index(index-1)
				execution_time = divmod(execution_time.days * 86400 + execution_time.seconds, 86400)
				if unit == 'hour':
					execution_time = 24*execution_time[0] + execution_time[1]/(60*60)
				if unit == 'day':
					execution_time = execution_time[0] + execution_time[1]/(60*60*24)
				execution_times.append(execution_time)
				count = 1
			else:
				execution_times.append(float('nan'))
		self = self.assign(execution_time = execution_times)
		return self

	def calculate_relative_time(self, unit = 'day'):
		self.calculate_execution_time(unit)
		relative_times = []
		for instance in self.itertuples():
			index = instance.Index
			if math.isnan(instance.execution_time):
				relative_time = 0
			else:
				relative_time = relative_times[index-1] + instance.execution_time
			relative_times.append(relative_time)
		self = self.assign(relative_time = relative_times)
		return self

	def analyze_performance(self, value = 'execution_time', metric = 'mean', *args, **kwargs):
		if 'dim_1' in kwargs:
			dim_1 = kwargs['dim_1']
		if 'dim_2' in kwargs:
			dim_2 = kwargs['dim_2']
		if 'value' in kwargs:
			value = kwargs['value']
		if metric == 'mean':
			result = self.groupby([dim_1,dim_2])[value].mean()
		if metric == 'median':
			result = self.groupby([dim_1,dim_2])[value].median()
		if metric == 'min':
			result = self.groupby([dim_1,dim_2])[value].min()
		if metric == 'max':
			result = self.groupby([dim_1,dim_2])[value].max()
		if metric == 'std':
			result = self.groupby([dim_1,dim_2])[value].std()
		if metric == 'frequency':
			result = self.groupby([dim_1,dim_2])[value].count()
		if metric == 'frequency_per_case':
			result = self.groupby([dim_1,dim_2])[value].count()/len(self.get_caseids())

		return result

	def count_event(self):
		return len(self.index)

	def count_cluster(self):
		cluster_case = self.groupby('Cluster').CASE_ID.apply(list).apply(set)
		cluster_case_count = cluster_case.apply(len)
		cluster_case_count_mean = np.mean(cluster_case_count)
		cluster_case_count_std = np.std(cluster_case_count)
		print("CLUSTER count: {}".format(cluster_case_count))
		print("CLUSTER count mean: {}".format(cluster_case_count_mean))
		print("CLUSTER count std: {}".format(cluster_case_count_std))
		return cluster_case_count

	def count_case(self):
		return len(set(self['CASE_ID']))

	def describe(self):
		print("# events: {}".format(len(self)))
		print("# cases: {}".format(len(set(self['CASE_ID']))))
		print("# activities: {}".format(len(set(self['ACTIVITY']))))
		print("# resources: {}".format(len(set(self['RESOURCE']))))
		try:
			print("average yield: {}".format(np.mean(self['VALUE'])))
		except AttributeError:
			print("yield not exists")

	def split_on_case(self, split):
		caseid = self.get_caseids()
		sub_cases = []
		for d in np.array_split(caseid, split):
			sub_cases.append(d)
		sub_logs = []
		for i in range(len(sub_cases)):
			sub_log = self.loc[self['CASE_ID'].isin(sub_cases[i]), :]
			sub_log.reset_index(drop=True, inplace=True)
			sub_logs.append(sub_log)
		return sub_logs

	def parallelize(self, func, workers=multiprocessing.cpu_count(), *args):
		sublogs = self.split_on_case(workers)
		output = Queue()
		manager = Manager()
		output = manager.list()
		# Setup a list of processes that we want to run
		processes = [Process(target=func, args=(sublogs[i], output)+args) for i in range(len(sublogs))]
		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
			p.join()

		return output



if __name__ == '__main__':
	"""
	eventlog = Eventlog.from_xes('./example/running_example.xes')
	print(type(eventlog))
	"""
	eventlog = Eventlog.from_txt('/Users/GYUNAM/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/input/Sample_data.txt')

	eventlog = eventlog.assign_caseid('ROOT_LOT_ID', 'WAFER_ID')
	eventlog = eventlog.assign_timestamp('TKIN_TIME', 'TKOUT_TIME')
	print(eventlog)







