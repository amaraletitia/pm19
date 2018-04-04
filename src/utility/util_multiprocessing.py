from PyProM.src.utility.util_profile import Util_Profile

class Util_Multiprocessing(object):
	timefn = Util_Profile.timefn

	def __init__(self):
		super(Util_Multiprocessing, self).__init__()

	@property
	def _constructor(self):
		return Util_Multiprocessing


	@classmethod
	def join_dict(cls, output):
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