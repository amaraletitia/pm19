import numpy as np

class Classifier(object):
	def __init__(self):
		pass

	def rank_based_criterion(self, wafer_data, BOB_n = 10, WOW_n = 10):
		wafer_data_tmp = wafer_data.groupby('CASE_ID').agg([np.mean, np.std])
		mean = wafer_data_tmp['VALUE', 'mean']
		#print(mean)
		mean = mean.sort_values(ascending = False)
		if BOB_n ==0:
			BOB_criterion = float("inf")
		else:
			BOB_criterion = mean[BOB_n-1]
		if WOW_n == 0:
			WOW_criterion = -float("inf")
		else:
			WOW_criterion = mean[-(WOW_n)]
		print("produce rank_based_criterion")
		return BOB_criterion, WOW_criterion

	def relative_ratio_criterion(self, wafer_data, BOB_rela_criterion = 70, WOW_rela_criterion = 30):
		wafer_data_tmp = wafer_data.groupby('CASE_ID').agg([np.mean, np.std])
		mean = wafer_data_tmp['VALUE', 'mean']
		BOB_criterion = np.percentile(mean, BOB_rela_criterion)
		WOW_criterion = np.percentile(mean, WOW_rela_criterion)
		print("Execute relative_ratio_criterion")
		return BOB_criterion, WOW_criterion

	def absolute_value_criterion(self, wafer_data, BOB_abs_criterion = 8.0, WOW_abs_criterion = 7.0):
		BOB_criterion = BOB_abs_criterion
		WOW_criterion = WOW_abs_criterion
		print("Execute absolute_value_criterion")
		return BOB_criterion, WOW_criterion

	def produce_wafer_BOB_WOW_group(self,wafer_data, BOB_criterion, WOW_criterion):
		#확인
		"""
		criterion = [BOB_criterion, WOW_criterion]
		with open('../result/criterion.txt', 'w') as f:
			for c in criterion:
				f.write("%s\n" % c)
		"""
		#VALUE = wafer_data['VALUE'].astype(float)
		#wafer_data = wafer_data.copy()

		BOB_group = wafer_data.loc[wafer_data['VALUE'] >= BOB_criterion, 'CASE_ID']
		WOW_group = wafer_data.loc[wafer_data['VALUE'] <= WOW_criterion, 'CASE_ID']

		return list(set(BOB_group)), list(set(WOW_group))









