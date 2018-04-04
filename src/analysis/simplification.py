import sys
import os
#sys.path.append(os.path.abspath("../utility"))
from PyProM.src.utility.util_profile import Util_Profile

timefn = Util_Profile.timefn

class Simplification(object):

	def __init__(self):
		super(Simplification, self).__init__()
		#self.by_inout(transition_matrix, analysis_result)

	def dummy(self, x):
 		return x.split("/")[0].strip() + '/dummy'

	@timefn
	def by_inout(self, transition_matrix, analysis_result):

		dummies = analysis_result.loc[analysis_result['LCresult'] == 'DUMMY','RESOURCE']
		dummies = dummies.values
		#print("dummies: {}".format(dummies))
		for ai in list(transition_matrix):

			for aj in list(transition_matrix[ai]):

				if aj in dummies:
					new_key = self.dummy(aj)
					if self.dummy(aj) not in transition_matrix[ai]:
						transition_matrix[ai][new_key] = transition_matrix[ai].pop(aj)
					else:
						for key in transition_matrix[ai][aj].keys():
							transition_matrix[ai][new_key][key] += transition_matrix[ai][aj][key]
						del transition_matrix[ai][aj]


					#transition_matrix[ai][new_key] = transition_matrix[ai].pop(aj)
					#del transition_matrix[ai][aj]

			if ai in dummies:
				new_key = self.dummy(ai)
				transition_matrix[new_key] = transition_matrix.pop(ai)


		#print("simplification completed: {}".format(transition_matrix))
		#print("Simplified {}".format(transition_matrix.keys()))
		return transition_matrix

	#def __call__(self)


