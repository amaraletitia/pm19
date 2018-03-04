import sys
import os
sys.path.append(os.path.abspath("../data"))
from Eventlog import Eventlog
from xes_reader import XesReader

import pandas as pd
import collections

import sys
import os
sys.path.append(os.path.abspath("../utility"))
from util_profile import Util_Profile

timefn = Util_Profile.timefn


class TransitionMatrix(object):
	"""docstring for TransitionMatrix"""
	def __init__(self):
		super(TransitionMatrix, self).__init__()
		self.transition_matrix = self._create_transition_matrix()
		#self.transition_matrix = to_transition_matrix(eventlog)
	@timefn
	def _create_transition_matrix(self, eventlog):
		print("produce transition matrix")
		transition_matrix = dict()
		caseid = eventlog['CASE_ID'][0]

		for index, instance in eventlog.iterrows():
			if index == len(eventlog) - 1:
				continue
			#caseid = instance['CASEID']
			if instance['CASE_ID'] == caseid:
				ai = eventlog['ACTIVITY'][index]
				aj = eventlog['ACTIVITY'][index+1]
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1
			caseid = instance['CASE_ID']
		"""
		for ai in sorted(transition_matrix.keys()):
			for aj in sorted(transition_matrix[ai].keys()):
				print("{}, ->, {}, :, {}".format(ai, aj, transition_matrix[ai][aj]['count']))
		"""
		print("Finish")
		return transition_matrix

	def get_transition_matrix(self):
		return self.transition_matrix

class AnnotatedTransitionMatrix(object):

	def __init__(self):
		super(AnnotatedTransitionMatrix, self).__init__()

	@timefn
	def _produce_annotated_transition_matrix(self, eventlog):
		print("produce annotated transition matrix")
		transition_matrix = dict()

		#start node
		transition_matrix['START'] = dict()
		#transition_matrix['START'] = dict()

		caseid = eventlog['CASE_ID'][0]
		#add 'START'
		count = 0
		for instance in eventlog.itertuples():
			index = instance.Index
			if index == len(eventlog) - 1:
				continue
			#add 'START'
			caseid = eventlog['CASE_ID'][index+1]
			if count == 0:
				ai = 'START'
				aj = eventlog['RESOURCE'][index]
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1
				count = 1

			if instance.CASE_ID == caseid:
				ai = eventlog['RESOURCE'][index]
				aj = eventlog['RESOURCE'][index+1]
				if ai not in transition_matrix:
					transition_matrix[ai] = dict()
				if aj not in transition_matrix[ai]:
					transition_matrix[ai][aj] = collections.defaultdict(list)
					transition_matrix[ai][aj]['case'] = [caseid]
					transition_matrix[ai][aj]['count'] = 0
				transition_matrix[ai][aj]['count'] += 1
				#count += 1

				if caseid not in transition_matrix[ai][aj]['case']:
					transition_matrix[ai][aj]['case'].append(caseid)
			else:
				#add 'START'
				count = 0

				#add 'END'
				ai = eventlog['RESOURCE'][index]
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

		#print(transition_matrix)
		print("Finish")
		return transition_matrix


	def get_transition_matrix(self):
		return self.transition_matrix








