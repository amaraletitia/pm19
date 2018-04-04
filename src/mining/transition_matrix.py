import sys
import os
#sys.path.append(os.path.abspath("../data"))
from PyProM.src.data.Eventlog import Eventlog
from PyProM.src.data.xes_reader import XesReader
from PyProM.src.data.sequence import Sequence
from PyProM.src.data.abs_set import Abs_set

import pandas as pd
import numpy as np
import collections
from copy import deepcopy

from multiprocessing import Process, Manager, Queue

#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile
from PyProM.src.utility.util_multiprocessing import Util_Multiprocessing

timefn = Util_Profile.timefn



class TransitionMatrix(object):
	"""docstring for TransitionMatrix"""
	def __init__(self):
		super(TransitionMatrix, self).__init__()

	def get_transition_matrix(self, eventlog, workers, type='sequence', horizon=1, target = 'ACTIVITY'):
		self.type = type
		self.horizon = horizon
		self.target = target

		output = eventlog.parallelize(self._produce_transition_matrix, workers, self.type, self.horizon, target)

		transition_matrix = Util_Multiprocessing.join_dict(output)
		return transition_matrix



	@timefn
	def _produce_transition_matrix(self, eventlog, x, type = 'sequence', horizon = 1, target='ACTIVITY'):
		print("produce transition matrix")
		transition_matrix = dict()
		transition_matrix['START'] = dict()

		event_trace = eventlog.get_event_trace(1, target)
		for trace in event_trace.values():
			if type == 'sequence':
				ai = Sequence(horizon)
			if type == 'set':
				ai = Abs_set(horizon)
			count = 0
			#add 'START'
			ai.append('START')
			for index, act in enumerate(trace):
				if count != 0:
					ai = deepcopy(aj)
				aj = deepcopy(ai)
				aj.append(act)
				ai_string = ai.to_string()
				aj_string = aj.to_string()
				if ai_string not in transition_matrix:
					transition_matrix[ai_string] = dict()
				if aj_string not in transition_matrix[ai_string]:
					transition_matrix[ai_string][aj_string] = collections.defaultdict(list)
					transition_matrix[ai_string][aj_string]['count'] = 0
				transition_matrix[ai_string][aj_string]['count'] += 1
				count = 1
				#add 'END'
				if index == len(trace) - 1:
					ai = deepcopy(aj)
					ai_string = ai.to_string()
					aj_string = 'END'
					if ai_string not in transition_matrix:
						transition_matrix[ai_string] = dict()
					if aj_string not in transition_matrix[ai_string]:
						transition_matrix[ai_string][aj_string] = collections.defaultdict(list)
						transition_matrix[ai_string][aj_string]['count'] = 0
					transition_matrix[ai_string][aj_string]['count'] += 1

		print("Finish")
		x.append(transition_matrix)

	def annotate_transition_matrix(self, eventlog, workers, transition_matrix, value = 'duration'):

		output = eventlog.parallelize(self._annotate_transition_matrix, workers, transition_matrix,value)

		transition_matrix = Util_Multiprocessing.join_dict(output)
		return transition_matrix

	@timefn
	def _annotate_transition_matrix(self, eventlog, x, transition_matrix, value='duration'):
		print("produce annotated transition matrix")

		#start node
		caseid = eventlog.get_first_caseid()
		count = 0

		for instance in eventlog.itertuples():
			index = instance.Index
			if index == eventlog.count_event() - 1:
				continue

			caseid = eventlog.get_caseid_by_index(index+1)

			if count == 0:
				if self.type == 'sequence':
					ai = Sequence(self.horizon)
				if self.type == 'set':
					ai = Abs_set(self.horizon)
				ai.append('START')
				aj = deepcopy(ai)
				if self.target == 'ACTIVITY':
					aj.append(eventlog.get_activity_by_index(index))
				elif self.target == 'RESOURCE':
					aj.append(eventlog.get_resource_by_index(index))
				count = 1

			if instance.CASE_ID == caseid:
				if index == eventlog.count_event() - 2:
					break
				ai = deepcopy(aj)
				if self.target == 'ACTIVITY':
					aj.append(eventlog.get_activity_by_index(index+1))
				elif self.target == 'RESOURCE':
					aj.append(eventlog.get_resource_by_index(index+1))
				ai_string = ai.to_string()
				aj_string = aj.to_string()
				if value == 'CASE_ID':
					if 'case' not in transition_matrix[ai_string][aj_string]:
						transition_matrix[ai_string][aj_string]['case'] = []

					if caseid not in transition_matrix[ai_string][aj_string]['case']:
						transition_matrix[ai_string][aj_string]['case'].append(caseid)
				if value == 'duration':
					next_caseid = eventlog.get_caseid_by_index(index+2)
					if caseid == next_caseid:
						ak = deepcopy(aj)
						if self.target == 'ACTIVITY':
							ak.append(eventlog.get_activity_by_index(index+2))
						elif self.target == 'RESOURCE':
							ak.append(eventlog.get_resource_by_index(index+2))
						ak_string = ak.to_string()
						if 'duration' not in transition_matrix[ai_string][aj_string]:
							transition_matrix[aj_string][ak_string]['duration'] = []
						duration = eventlog.get_timestamp_by_index(index+1) - eventlog.get_timestamp_by_index(index)
						duration = divmod(duration.days * 86400 + duration.seconds, 86400)
						duration = 24*duration[0] + duration[1]/3600
						transition_matrix[aj_string][ak_string]['duration'].append(duration)


			else:
				count = 0
				#add 'END'
				ai = deepcopy(aj)
				if self.type == 'sequence':
					aj = Sequence(self.horizon)
				if self.type == 'set':
					aj = Abs_set(self.horizon)
				aj.append('END')
				ai_string = ai.to_string()
				aj_string = aj.to_string()
				if value == 'CASE_ID':
					if 'case' not in transition_matrix[ai_string][aj_string]:
						transition_matrix[ai_string][aj_string]['case'] = []

					if caseid not in transition_matrix[ai_string][aj_string]['case']:
						transition_matrix[ai_string][aj_string]['case'].append(caseid)
		print("Finish")

		x.append(transition_matrix)








