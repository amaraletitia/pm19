import sys
import os
sys.path.append(os.path.abspath("../data"))
from Eventlog import Eventlog
from xes_reader import XesReader

import pandas as pd
import numpy as np
import collections

from multiprocessing import Process, Manager, Queue

sys.path.append(os.path.abspath("../utility"))
from util_profile import Util_Profile
from util_multiprocessing import Util_Multiprocessing

timefn = Util_Profile.timefn



class TransitionMatrix(object):
	"""docstring for TransitionMatrix"""
	def __init__(self):
		super(TransitionMatrix, self).__init__()

	def get_transition_matrix(self, eventlog, workers):
		sublogs = eventlog.split_on_case(workers)

		output = Queue()
		manager = Manager()
		output = manager.list()

		# Setup a list of processes that we want to run
		processes = [Process(target=self._produce_transition_matrix, args=(sublogs[i], output)) for i in range(len(sublogs))]

		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
			p.join()


		transition_matrix = Util_Multiprocessing.join_dict(output)
		return transition_matrix



	@timefn
	def _produce_transition_matrix(self, eventlog, x):
		print("produce transition matrix")
		transition_matrix = dict()

		#start node
		transition_matrix['START'] = dict()
		caseid = eventlog.get_first_caseid()
		count = 0

		for instance in eventlog.itertuples():
			index = instance.Index
			if index == eventlog.count_event() - 1:
				continue
			#add 'START'
			caseid = eventlog.get_next_event_caseid_by_index(index)
			if count == 0:
				ai = 'START'
				aj = eventlog.get_activity_by_index(index)
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1
				count = 1

			if instance.CASE_ID == caseid:
				ai = eventlog.get_activity_by_index(index)
				aj = eventlog.get_next_event_activity_by_index(index)
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1

			else:
				count = 0
				#add 'END'
				ai = eventlog.get_activity_by_index(index)
				aj = 'END'
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0
				if caseid not in transition_matrix[ai][aj]['case']:
					transition_matrix[ai][aj]['case'].append(caseid)
				transition_matrix[ai][aj]['count'] += 1

		print("Finish")

		x.append(transition_matrix)

class AnnotatedTransitionMatrix(object):

	def __init__(self):
		super(AnnotatedTransitionMatrix, self).__init__()

	def get_annotated_transition_matrix(self, eventlog, workers):
		sublogs = eventlog.split_on_case(workers)

		output = Queue()
		manager = Manager()
		output = manager.list()

		# Setup a list of processes that we want to run
		processes = [Process(target=self._produce_annotated_transition_matrix, args=(sublogs[i], output)) for i in range(len(sublogs))]

		# Run processes
		for p in processes:
		    p.start()

		# Exit the completed processes
		for p in processes:
			p.join()


		transition_matrix = Util_Multiprocessing.join_dict(output)
		return transition_matrix

	@timefn
	def join_dict(self, output):
		for i, matrix in enumerate(output):
			if i == 0:
				result = matrix
			else:
				keys = result.keys()
				for ai in matrix.keys():
					if ai not in keys:
						result[ai] = matrix[ai]
					else:
						inner_keys = result[ai].keys()
						for aj in matrix[ai].keys():
							if aj not in inner_keys:
								result[ai][aj] = matrix[ai][aj]
							else:
								for ak in matrix[ai][aj].keys():
									result[ai][aj][ak] += matrix[ai][aj][ak]
		return result


	@timefn
	def _produce_annotated_transition_matrix(self, eventlog, x):
		print("produce annotated transition matrix")
		transition_matrix = dict()

		#start node
		transition_matrix['START'] = dict()
		caseid = eventlog.get_first_caseid()
		count = 0

		for instance in eventlog.itertuples():
			index = instance.Index
			if index == eventlog.count_event() - 1:
				continue
			#add 'START'
			caseid = eventlog.get_next_event_caseid_by_index(index)
			if count == 0:
				ai = 'START'
				aj = eventlog.get_resource_by_index(index)
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0

				transition_matrix[ai][aj]['count'] += 1
				count = 1

			if instance.CASE_ID == caseid:
				ai = eventlog.get_resource_by_index(index)
				aj = eventlog.get_next_event_resource_by_index(index)
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['case'] = [caseid]
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1

				if caseid not in transition_matrix[ai][aj]['case']:
					transition_matrix[ai][aj]['case'].append(caseid)
			else:
				count = 0
				#add 'END'
				ai = eventlog.get_resource_by_index(index)
				aj = 'END'
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['case'] = [caseid]
					transition_matrix[ai][aj]['count'] = 0
				if caseid not in transition_matrix[ai][aj]['case']:
					transition_matrix[ai][aj]['case'].append(caseid)
				transition_matrix[ai][aj]['count'] += 1

		print("Finish")

		x.append(transition_matrix)


	def get_transition_matrix(self):
		return self.transition_matrix








