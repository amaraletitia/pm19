from Preprocessing import Preprocessing
import numpy as np
import pandas as pd

class Classifier(object):
	def __init__(self, preprocessed_data):
		print("CLASSIFIER class")
		
		self.data = preprocessed_data

	"""
	Specific Wafer level
	"""
	def create_lot_data(self, minimum_lot_counts = 20):

		self.lot_data = self.data[['ROOT_LOT_ID', 'STEP_SEQ', 'EQP_ID', 'VALUE']]
		self.lot_data['S_EQP_ID'] = self.lot_data['STEP_SEQ'] + '_' + self.lot_data['EQP_ID']
		self.lot_data.reset_index(inplace = True)
		del self.lot_data['index']
		grouped = self.lot_data.groupby('S_EQP_ID')
		eqp_count = grouped['ROOT_LOT_ID'].count()
		eqp_count[eqp_count >= minimum_lot_counts].index
		self.lot_data = self.lot_data[self.lot_data['S_EQP_ID'].isin(eqp_count[eqp_count >= minimum_lot_counts].index)]

	def relative_ratio_std_criterion(self, std_rela_criteiron = 70):
		self.lot_data_temp = self.lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.lot_data_temp['VALUE', 'std']
		user_defined_std_rela_criterion = std_rela_criteiron
		self.std_criterion = np.percentile(std, user_defined_std_rela_criterion)

	def absoulte_value_std_criterion(self, std_abs_criterion = 1):
		self.std_criterion = std_abs_criterion

	def rank_based_std_criterion(self, n = 10):
		self.lot_data_temp = self.lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.lot_data_temp['VALUE', 'std']
		std = std.sort_values(ascending = True)
		std_criterion = std[n-1]

		mean = self.lot_data_temp['VALUE', 'mean']
		mean = mean.sort_values(ascending = True)
		#mean_criterion
		mean_criterion = mean[n-1]

	def extract_deviated_lot(self):
		extracted_lots = self.lot_data_temp.loc[self.lot_data_temp.VALUE['std'] > self.std_criterion].index
		self.data = self.data.loc[self.data['ROOT_LOT_ID'].isin(extracted_lots)]
		print(self.data)

	"""
	wafer level
	"""
	def create_wafer_data(self, minimum_wafer_counts = 20):
		self.data['S_E_CHAMBER_ID'] = self.data['STEP_SEQ'] + '_' + self.data['EQP_ID'] + '_' + self.data['CHAMBER_ID']
		#print(self.data)
		wafer_data = self.data[['CASE_ID', 'STEP_SEQ', 'S_E_CHAMBER_ID', 'VALUE']]
		self.wafer_data = wafer_data
		self.wafer_data.reset_index(inplace = True)
		del self.wafer_data['index']
		grouped = wafer_data.groupby('S_E_CHAMBER_ID')
		chamber_count = grouped['CASE_ID'].count()
		chamber_count[chamber_count >= minimum_wafer_counts].index
		self.wafer_data = self.wafer_data[self.wafer_data['S_E_CHAMBER_ID'].isin(chamber_count[chamber_count >= minimum_wafer_counts].index)]

	#Rank-based
	"""
	def create_wafer_BOB_WOW_group(self, n):
		wafer_data_temp = wafer_data.copy()

		def value(x):
		    return x.values[0]

		wafer_data_temp = wafer_data_temp[['CASE_ID','VALUE']].groupby('CASE_ID').agg(value)
		wafer_data_temp.sort_values(by = 'VALUE', inplace = True, ascending = False)
		wafer_data_BOB_WOW_Group = wafer_data.copy()
		BOB_cases = wafer_data_temp.head(n).index
		WOW_cases = wafer_data_temp.tail(n).index
		wafer_data_BOB_WOW_Group['BOB'] = wafer_data_BOB_WOW_Group.CASE_ID.isin(BOB_cases)
		wafer_data_BOB_WOW_Group['WOW'] = wafer_data_BOB_WOW_Group.CASE_ID.isin(WOW_cases)
	"""

	#Relative Ratio
	def create_wafer_BOB_WOW_group(self, BOB_RELA=20, WOW_RELA=80):
		VALUE = self.wafer_data['VALUE'].astype(float)
		print(VALUE)
		user_defined_V_BOB_RELA = BOB_RELA
		user_defined_V_WOW_RELA = WOW_RELA
		BOB_VALUE = np.percentile(VALUE, user_defined_V_BOB_RELA)
		WOW_VALUE = np.percentile(VALUE, user_defined_V_WOW_RELA)
		wafer_BOB_WOW_Group = self.wafer_data.copy()
		wafer_BOB_WOW_Group['BOB'] = wafer_BOB_WOW_Group.VALUE > BOB_VALUE
		wafer_BOB_WOW_Group['WOW'] = wafer_BOB_WOW_Group.VALUE < WOW_VALUE
		#wafer_BOB_WOW_Group. ('/Users/i/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/imple/result/wafer_BOB_WOW_Group.csv', sep=',',index=False)
		self.wafer_BOB_WOW_Group = wafer_BOB_WOW_Group

	#Absoulte value
	"""
	def create_wafer_BOB_WOW_group(self, BOB_VALUE, WOW_VALUE):
		wafer_BOB_WOW_Group = self.wafer_data.copy()
		wafer_BOB_WOW_Group['BOB'] = wafer_BOB_WOW_Group.VALUE > BOB_VALUE
		wafer_BOB_WOW_Group['WOW'] = wafer_BOB_WOW_Group.VALUE < WOW_VALUE
		#wafer_BOB_WOW_Group.to_csv('/Users/i/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/imple/result/wafer_BOB_WOW_Group.csv', sep=',',index=False)
		self.wafer_BOB_WOW_Group = wafer_BOB_WOW_Group
	"""

	def create_chamber_perf(self):
		#user_defined_chamber_size = 30
		grouped = self.wafer_BOB_WOW_Group.groupby('S_E_CHAMBER_ID')
		chamber_perf = grouped.agg([np.count_nonzero, np.mean, np.std])

		BOB = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['BOB'] == True].groupby('S_E_CHAMBER_ID').VALUE.agg(['mean','std'])
		BOB.columns = pd.MultiIndex.from_product([['BOB_stat'], BOB.columns])

		WOW = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['WOW'] == True].groupby('S_E_CHAMBER_ID').VALUE.agg(['mean','std'])
		WOW.columns = pd.MultiIndex.from_product([['WOW_stat'], WOW.columns])


		chamber_perf = pd.merge(chamber_perf, BOB, left_index=True, right_index=True, how='left')
		chamber_perf = pd.merge(chamber_perf, WOW, left_index=True, right_index=True, how='left')
		#chamber_perf.to_csv('/Users/i/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/imple/result/chamber_perf.csv', sep=',')

		step_perf = self.wafer_data.groupby('STEP_SEQ').CASE_ID.count()

		#설비 BOB count/STEP 내 모든 웨이퍼 수
		chamber_perf['BOB/step'] = 0.0
		def BOB_step(chamber):
		    count = chamber_perf.loc[chamber]['BOB', 'count_nonzero']
		    step = chamber[:8]
		    return count/step_perf[step]

		def WOW_step(chamber):
		    count = chamber_perf.loc[chamber]['WOW', 'count_nonzero']
		    step = chamber[:8]
		    return count/step_perf[step]

		chamber_perf['BOB/step'] = chamber_perf.index.to_series().apply(BOB_step)
		chamber_perf['WOW/step'] = chamber_perf.index.to_series().apply(WOW_step)
		#chamber_perf = chamber_perf.loc[chamber_perf['VALUE', 'count_nonzero']>user_defined_chamber_size]
		self.chamber_perf = chamber_perf

	def show_data(self):
		print(self.wafer_data)

	def Get_data(self):
		return self.data

	"""
	LOT level
	""" 

if __name__ == '__main__':
	preprocessing = Preprocessing('../input/raw_data.txt')
	preprocessing.wafer_count(preprocessing.data, 23)
	print(len(preprocessing.data))
	preprocessing.chamber_variety(preprocessing.data, 20)
	print(len(preprocessing.data))
	preprocessing.period(preprocessing.data)
	print(len(preprocessing.data))
	preprocessing.main(preprocessing.data)
	print(len(preprocessing.data))
	preprocessed_data = preprocessing.data
	print("export preprocessed_data")
	preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)
	
	classifier = Classifier(preprocessed_data)
	classifier.create_lot_data()
	classifier.relative_ratio_std_criterion()
	classifier.extract_deviated_lot()
	classifier.create_wafer_data()
	print(classifier.wafer_data)
	print("created wafer_data.csv")
	print(len(classifier.wafer_data))
	classifier.wafer_data.to_csv('../result/wafer_data.csv', sep=',', index = False)
	classifier.create_wafer_BOB_WOW_group()
	print("created wafer_BOB_WOW_Group.csv")
	print(len(classifier.wafer_BOB_WOW_Group))
	classifier.wafer_BOB_WOW_Group.to_csv('../result/wafer_BOB_WOW_group.csv', sep=',')
	classifier.create_chamber_perf()
	print("created chamber_perf")
	print(len(classifier.chamber_perf))
	classifier.chamber_perf.to_csv('../result/chamber_perf.csv', sep=',')
	#classifier.show_data()


