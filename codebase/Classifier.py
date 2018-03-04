from Preprocessing import Preprocessing
import numpy as np
import pandas as pd

class Classifier(object):
	def __init__(self, preprocessed_data):
		
		self.data = preprocessed_data
		print("CLASSIFIER begins: {}".format(len(self.data)))
	"""
	wafer level
	"""

	def create_raw_lot_data(self, minimum_lot_counts = 20):
		self.raw_lot_data = self.data[['ROOT_LOT_ID', 'STEP_SEQ', 'EQP_ID', 'VALUE','TKIN_TIME']]
		self.raw_lot_data['S_EQP_ID'] = self.raw_lot_data['STEP_SEQ'] + '_' + self.raw_lot_data['EQP_ID']

		#maybe for generating step_graph
		self.raw_lot_data.loc[:, 'TKIN_TIME'] =  self.raw_lot_data['TKIN_TIME'].map(lambda t: t.strftime('%Y-%m-%d %H'))

		self.raw_lot_data.sort_values(by=['ROOT_LOT_ID', 'STEP_SEQ'], inplace = True)
		self.raw_lot_data.reset_index(inplace = True)
		del self.raw_lot_data['index']

		grouped = self.raw_lot_data.groupby('S_EQP_ID')
		eqp_count = grouped['ROOT_LOT_ID'].count()
		eqp_count[eqp_count >= minimum_lot_counts].index
		self.raw_lot_data = self.raw_lot_data[self.raw_lot_data['S_EQP_ID'].isin(eqp_count[eqp_count >= minimum_lot_counts].index)]
		print("##Created raw_lot_data: {}".format(len(self.raw_lot_data)))

	def relative_ratio_std_criterion(self, std_rela_criteiron = 30):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.raw_lot_data_temp['VALUE', 'std']
		user_defined_std_rela_criterion = std_rela_criteiron
		self.std_criterion = np.percentile(std, user_defined_std_rela_criterion)
		print("Execute relative_ratio_std_criterion")

	def absolute_value_std_criterion(self, std_abs_criterion = 1):
		self.std_criterion = std_abs_criterion
		print("Execute absolute_value_std_criterion")

	def rank_based_std_criterion(self, n = 10):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.raw_lot_data_temp['VALUE', 'std']
		std = std.sort_values(ascending = True)
		std_criterion = std[n-1]

		mean = self.raw_lot_data_temp['VALUE', 'mean']
		mean = mean.sort_values(ascending = True)
		#mean_criterion
		mean_criterion = mean[n-1]
		print("Execute rank_based_std_criterion")

	def extract_deviated_lot(self):
		extracted_lots = self.raw_lot_data_temp.loc[self.raw_lot_data_temp.VALUE['std'] > self.std_criterion].index
		self.data = self.data.loc[self.data['ROOT_LOT_ID'].isin(extracted_lots)]
	# user_defined_ratio 설정할 수 있
	def create_wafer_data(self, user_defined_ratio=0.8, horizon=1):
		self.data.loc[:,'S_E_CHAMBER_ID'] = self.data['STEP_SEQ'] + '_' + self.data['EQP_ID'] + '_' + self.data['CHAMBER_ID']

		self.wafer_data = self.data[['CASE_ID', 'STEP_SEQ', 'S_E_CHAMBER_ID', 'VALUE', 'TKIN_TIME']]

		self.wafer_data['TKIN_TIME'] =  pd.to_datetime(self.wafer_data['TKIN_TIME'], format='%Y-%m-%d %H:%M:%S')
		#maybe for generating step_graph
		try:
			self.wafer_data.loc[:, 'TKIN_TIME'] =  self.wafer_data['TKIN_TIME'].map(lambda t: t.strftime('%Y-%m-%d %H'))
		except AttributeError:
			pass
		
		self.wafer_data.sort_values(by=['CASE_ID', 'STEP_SEQ'], inplace = True)
		self.wafer_data.reset_index(inplace = True)
		del self.wafer_data['index']

		count = 0
		prev_count = 0
		index = 0
		case_id = self.wafer_data['CASE_ID'][0]
		f = []
		t = []
		for row in self.wafer_data.itertuples():
			if case_id == row.CASE_ID:
				if count == 0:
					f.append(['START'])
					t.append([row.S_E_CHAMBER_ID])
				elif count < horizon:
					_from = []
					_to = []
					for n in range(count,0,-1):
                        #print(n)
						_from.append(self.wafer_data['S_E_CHAMBER_ID'][row.Index-n])
					for n in range(count,-1,-1):
						_to.append(self.wafer_data['S_E_CHAMBER_ID'][row.Index-n])
					t.append(_to)
					f.append(_from)
				else:
					_from = []
					_to = []
					for n in range(horizon,0,-1):
					#print(n)
						_from.append(self.wafer_data['S_E_CHAMBER_ID'][row.Index-n])
					for n in range(horizon-1,-1,-1):
						_to.append(self.wafer_data['S_E_CHAMBER_ID'][row.Index-n])
					t.append(_to)
					f.append(_from)
				count+=1
			else:
				count = 0
				case_id = row.CASE_ID
				if count == 0:
					f.append(['START'])
					t.append([row.S_E_CHAMBER_ID])
				count+=1
		ff = []
		tt = []
		for __from in f:
			_from = "/".join(x for x in reversed(__from))
			ff.append(_from)

		for __to in t:
			_to = "/".join(x for x in reversed(__to))
			tt.append(_to)

		self.wafer_data = self.wafer_data.assign(FROM = ff, TO=tt)
        

		step_perf = self.wafer_data.groupby('STEP_SEQ').CASE_ID.count()
		step_chamber_count = self.wafer_data.groupby('STEP_SEQ').TO.apply(list)

		def count_step_chambers(x):
		    return len(list(set(x)))

		step_criterion = step_perf / step_chamber_count.apply(count_step_chambers) * user_defined_ratio
		print(step_criterion)
		grouped = self.wafer_data.groupby('TO')
		chamber_count = grouped['CASE_ID'].count()
		mean = chamber_count.mean(axis=0)
		
		chamber_list = []

		def extract_chamber(x):
		    step = x.split("_")[0].strip()
		    minimum_criterion = step_criterion[step]
		    if chamber_count[x] >= minimum_criterion:
		        chamber_list.append(x)
		    elif chamber_count[x] > mean:
		        chamber_list.append(x)
		        
		chamber_count.index.to_series().apply(extract_chamber)

		#self.wafer_data = self.wafer_data[self.wafer_data['S_E_CHAMBER_ID'].isin(chamber_list)]

		self.wafer_data.loc[:,'TO_TEST'] = np.where(self.wafer_data['TO'].isin(chamber_list), True, False)

		self.wafer_data.loc[:,'FROM_TEST'] = np.where(self.wafer_data['FROM'].isin(chamber_list), True, False)
		self.wafer_data.loc[:,'TO'] = np.where(self.wafer_data['TO_TEST'] == True, self.wafer_data['TO'], self.wafer_data['TO'].apply(lambda x: x.split('_')[0] + '_DM'))
		self.wafer_data.loc[:,'FROM'] = np.where(self.wafer_data['FROM_TEST'] == True, self.wafer_data['FROM'], np.where(self.wafer_data['FROM'] != 'START', self.wafer_data['FROM'].apply(lambda x: x.split('_')[0] + '_DM'), 'START'))
		#self.wafer_data.loc[:,'FROM'] = np.where(self.wafer_data['FROM_TEST'] == True, self.wafer_data['FROM'], np.where(self.wafer_data['FROM'] != 'START', self.wafer_data['FROM'].str.slice(0,4,1)+'_DM', 'START'))
		del self.wafer_data['TO_TEST']
		del self.wafer_data['FROM_TEST']
		
		print("##Created wafer_data: {}".format(len(self.wafer_data)))
		self.wafer_data.to_csv('../result/wafer_data.csv', sep = ',')

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
	def rank_based_mean_criterion(self, BOB_n = 10, WOW_n = 10):
		self.wafer_data_temp = self.wafer_data.groupby('CASE_ID').agg([np.mean, np.std])
		mean = self.wafer_data_temp['VALUE', 'mean']
		#print(mean)
		mean = mean.sort_values(ascending = False)
		if BOB_n ==0:
			self.BOB_mean_criterion = float("inf")
		else:
			self.BOB_mean_criterion = mean[BOB_n-1]
		if WOW_n == 0:
			self.WOW_mean_criterion = -float("inf")
		else:
			self.WOW_mean_criterion = mean[-(WOW_n)]
		print("Execute rank_based_std_criterion")

	def relative_ratio_mean_criterion(self, BOB_mean_rela_criterion = 70, WOW_mean_rela_criterion = 30):
		self.wafer_data_temp = self.wafer_data.groupby('CASE_ID').agg([np.mean, np.std])
		mean = self.wafer_data_temp['VALUE', 'mean']
		self.BOB_mean_criterion = np.percentile(mean, BOB_mean_rela_criterion)
		self.WOW_mean_criterion = np.percentile(mean, WOW_mean_rela_criterion)
		print("Execute relative_ratio_mean_criterion")

	def absolute_value_mean_criterion(self, BOB_mean_abs_criterion = 8.0, WOW_mean_abs_criterion = 7.0):
		self.BOB_mean_criterion = BOB_mean_abs_criterion
		self.WOW_mean_criterion = WOW_mean_abs_criterion
		print("Execute absolute_value_mean_criterion")

	#Relative Ratio
	def create_wafer_BOB_WOW_group(self):
		#확인
		criterion = [self.BOB_mean_criterion, self.WOW_mean_criterion]
		with open('../result/criterion.txt', 'w') as f:
			for c in criterion:
				f.write("%s\n" % c)
		VALUE = self.wafer_data['VALUE'].astype(float)
		self.wafer_BOB_WOW_Group = self.wafer_data.copy()
		self.wafer_BOB_WOW_Group['BOB'] = self.wafer_BOB_WOW_Group.VALUE >= self.BOB_mean_criterion
		self.wafer_BOB_WOW_Group['WOW'] = self.wafer_BOB_WOW_Group.VALUE <= self.WOW_mean_criterion
		print("Created wafer_BOB_WOW_Group: {}".format(len(self.wafer_BOB_WOW_Group)))
		self.wafer_BOB_WOW_Group.to_csv('../result/wafer_BOB_WOW_Group.csv', sep = ',')

	#absolute value
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
		grouped = self.wafer_BOB_WOW_Group.groupby('TO')

		def count(x):
			return x.count()

		chamber_perf = grouped.VALUE.agg([count, np.mean, np.std])
		chamber_perf.columns = [('VALUE', 'count_nonzero'), ('VALUE', 'mean'), ('VALUE', 'std')]
		chamber_perf_temp = grouped.BOB.agg([np.count_nonzero, np.mean, np.std])
		chamber_perf_temp.columns = [('BOB', 'count_nonzero'), ('BOB', 'mean'), ('BOB', 'std')]
		chamber_perf_temp_2 = grouped.WOW.agg([np.count_nonzero, np.mean, np.std])
		chamber_perf_temp_2.columns = [('WOW', 'count_nonzero'), ('WOW', 'mean'), ('WOW', 'std')]

		chamber_perf = chamber_perf.join([chamber_perf_temp, chamber_perf_temp_2], how='left')
		print(chamber_perf)

		BOB = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['BOB'] == True].groupby('TO').VALUE.agg(['mean','std'])
		BOB.columns = pd.MultiIndex.from_product([['BOB_stat'], BOB.columns])

		WOW = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['WOW'] == True].groupby('TO').VALUE.agg(['mean','std'])
		WOW.columns = pd.MultiIndex.from_product([['WOW_stat'], WOW.columns])


		chamber_perf = pd.merge(chamber_perf, BOB, left_index=True, right_index=True, how='left')
		chamber_perf = pd.merge(chamber_perf, WOW, left_index=True, right_index=True, how='left')
		#chamber_perf.to_csv('/Users/i/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/imple/result/chamber_perf.csv', sep=',')

		#step_perf = self.wafer_data.groupby('STEP_SEQ').CASE_ID.count()
		BOB_step_perf = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['BOB'] == True].groupby('STEP_SEQ').CASE_ID.count()
		WOW_step_perf = self.wafer_BOB_WOW_Group.loc[self.wafer_BOB_WOW_Group['WOW'] == True].groupby('STEP_SEQ').CASE_ID.count()

		#설비 BOB count/STEP 내 모든 웨이퍼 수
		chamber_perf['BOB/step'] = 0.0
		def BOB_step(chamber):
			try:
				count = chamber_perf.loc[chamber]['BOB', 'count_nonzero']
				step = chamber.split("_")[0].strip()
				return count/BOB_step_perf[step]
			except KeyError:
				pass
		def WOW_step(chamber):
			try:
				count = chamber_perf.loc[chamber]['WOW', 'count_nonzero']
				step = chamber.split("_")[0].strip()
				return count/WOW_step_perf[step]
			except KeyError:
				pass

		chamber_perf['BOB/step'] = chamber_perf.index.to_series().apply(BOB_step)
		chamber_perf['WOW/step'] = chamber_perf.index.to_series().apply(WOW_step)
		#chamber_perf = chamber_perf.loc[chamber_perf['VALUE', 'count_nonzero']>user_defined_chamber_size]
		self.chamber_perf = chamber_perf

		print("Created chamber_perf: {}".format(len(self.chamber_perf)))

	def show_data(self):
		print(self.wafer_data)

	def Get_data(self):
		return self.data

	"""
	LOT level
	""" 

if __name__ == '__main__':
	preprocessing = Preprocessing('../input/raw_data.txt')
	preprocessing.Incomplete_wafer(preprocessing.data)
	preprocessing.wafer_count(preprocessing.data, 23)
	print(len(preprocessing.data))
	#preprocessing.chamber_variety(preprocessing.data, 20)
	#print(len(preprocessing.data))
	#preprocessing.period(preprocessing.data)
	#preprocessing.main(preprocessing.data)
	preprocessed_data = preprocessing.data
	print("export preprocessed_data")
	preprocessed_data.to_sql("preprocessed_data", preprocessing.con, if_exists="replace", index=False)
	preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)
	
	classifier = Classifier(preprocessed_data)
	classifier.create_wafer_data()
	print("created wafer_data.csv")
	print(len(classifier.wafer_data))
	classifier.wafer_data.to_sql("wafer_data", preprocessing.con, if_exists="replace", index = False)
	classifier.wafer_data.to_csv('../result/wafer_data.csv', sep=',', index = False)
	classifier.relative_ratio_mean_criterion(80,20)
	classifier.create_wafer_BOB_WOW_group()
	print("created wafer_BOB_WOW_Group.csv")
	print(len(classifier.wafer_BOB_WOW_Group))
	classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", preprocessing.con, if_exists="replace",index=False)
	classifier.wafer_BOB_WOW_Group.to_csv('../result/wafer_BOB_WOW_group.csv', sep=',', index = False)
	classifier.create_chamber_perf()
	print("created chamber_perf")
	print(len(classifier.chamber_perf))
	classifier.chamber_perf.to_sql("chamber_perf", preprocessing.con, if_exists="replace")
	classifier.chamber_perf.to_csv('../result/chamber_perf.csv', sep=',')
	#classifier.show_data()


