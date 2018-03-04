from Preprocessing import Preprocessing
import numpy as np
import pandas as pd

class LOT_Classifier(object):
	def __init__(self, preprocessed_data):
		self.data = preprocessed_data
		print("LOT CLASSIFIER begins: {}".format(len(self.data)))
		#print(type(self.data))
		#self.data = self.create_lot_level_data()


	"""
	lot level
	"""
	def create_raw_lot_data(self, minimum_lot_counts = 20):
		self.raw_lot_data = self.data[['ROOT_LOT_ID', 'STEP_SEQ', 'EQP_ID', 'VALUE','TKIN_TIME']]
		self.raw_lot_data['S_EQP_ID'] = self.raw_lot_data['STEP_SEQ'] + '_' + self.raw_lot_data['EQP_ID']

		#maybe for generating step_graph
		self.raw_lot_data['TKIN_TIME'] =  pd.to_datetime(self.raw_lot_data['TKIN_TIME'], format='%Y-%m-%d %H:%M:%S')
		self.raw_lot_data.loc[:, 'TKIN_TIME'] =  self.raw_lot_data['TKIN_TIME'].map(lambda t: t.strftime('%Y-%m-%d %H'))

		self.raw_lot_data.sort_values(by=['ROOT_LOT_ID', 'STEP_SEQ'], inplace = True)
		self.raw_lot_data.reset_index(inplace = True)
		del self.raw_lot_data['index']

		grouped = self.raw_lot_data.groupby('S_EQP_ID')
		eqp_count = grouped['ROOT_LOT_ID'].count()
		eqp_count[eqp_count >= minimum_lot_counts].index
		self.raw_lot_data = self.raw_lot_data[self.raw_lot_data['S_EQP_ID'].isin(eqp_count[eqp_count >= minimum_lot_counts].index)]
		print("##Created raw_lot_data: {}".format(len(self.raw_lot_data)))

	def create_lot_data(self, horizon=1):
		#확인
		self.lot_data = self.raw_lot_data.groupby(['ROOT_LOT_ID', 'STEP_SEQ', 'S_EQP_ID']).VALUE.agg(np.mean)
		print(self.lot_data)
		print("len of lot_data: {}".format(len(self.lot_data)))
		self.lot_data = self.lot_data.reset_index()
		count = 0
		prev_count = 0
		index = 0
		lot_id = self.lot_data['ROOT_LOT_ID'][0]
		f = []
		t = []
		for row in self.lot_data.itertuples():
			if lot_id == row.ROOT_LOT_ID:
				if count == 0:
					f.append(['START'])
					t.append([row.S_EQP_ID])
				elif count < horizon:
					_from = []
					_to = []
					for n in range(count,0,-1):
                        #print(n)
						_from.append(self.lot_data['S_EQP_ID'][row.Index-n])
					for n in range(count,-1,-1):
						_to.append(self.lot_data['S_EQP_ID'][row.Index-n])
					t.append(_to)
					f.append(_from)
				else:
					_from = []
					_to = []
					for n in range(horizon,0,-1):
					#print(n)
						_from.append(self.lot_data['S_EQP_ID'][row.Index-n])
					for n in range(horizon-1,-1,-1):
						_to.append(self.lot_data['S_EQP_ID'][row.Index-n])
					t.append(_to)
					f.append(_from)
				count+=1
			else:
				count = 0
				lot_id = row.ROOT_LOT_ID
				if count == 0:
					f.append(['START'])
					t.append([row.S_EQP_ID])
				count+=1
		ff = []
		tt = []
		for __from in f:
			_from = "/".join(x for x in reversed(__from))
			ff.append(_from)

		for __to in t:
			_to = "/".join(x for x in reversed(__to))
			tt.append(_to)

		self.lot_data = self.lot_data.assign(FROM = ff, TO=tt)
		print("##Created lot_data: {}".format(len(self.lot_data)))

	#Rank-based
	def relative_ratio_std_criterion(self, std_rela_criteiron = 30):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.raw_lot_data_temp['VALUE', 'std']
		user_defined_std_rela_criterion = std_rela_criteiron
		self.std_criterion = np.percentile(std, user_defined_std_rela_criterion)
		print("Execute relative_ratio_std_criterion")

	def absoulte_value_std_criterion(self, std_abs_criterion = 1):
		self.std_criterion = std_abs_criterion
		print("Execute absoulte_value_std_criterion")

	def rank_based_std_criterion(self, n = 10):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		std = self.raw_lot_data_temp['VALUE', 'std']
		std = std.sort_values(ascending = True)
		self.std_criterion = std[n-1]

		mean = self.raw_lot_data_temp['VALUE', 'mean']
		mean = mean.sort_values(ascending = True)
		#mean_criterion
		mean_criterion = mean[n-1]
		print("Execute rank_based_std_criterion")

	def relative_ratio_mean_criterion(self, BOB_mean_rela_criterion = 70, WOW_mean_rela_criterion = 30):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		mean = self.raw_lot_data_temp['VALUE', 'mean']
		mean_BOB_RELA = BOB_mean_rela_criterion
		mean_WOW_RELA = WOW_mean_rela_criterion
		self.BOB_mean_criterion = np.percentile(mean, mean_BOB_RELA)
		self.WOW_mean_criterion = np.percentile(mean, mean_WOW_RELA)
		print("Execute relative_ratio_mean_criterion")

	def absoulte_value_mean_criterion(self, BOB_mean_abs_criterion = 8.0, WOW_mean_abs_criterion = 7.0):
		self.BOB_mean_criterion = BOB_mean_abs_criterion
		self.WOW_mean_criterion = WOW_mean_abs_criterion
		print("Execute absoulte_value_mean_criterion")

	def rank_based_mean_criterion(self, BOB_n = 10, WOW_n = 10):
		self.raw_lot_data_temp = self.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		mean = self.raw_lot_data_temp['VALUE', 'mean']
		mean = mean.sort_values(ascending = False)
		#mean_criterion
		if BOB_n ==0:
			self.BOB_mean_criterion = float("inf")
		else:
			self.BOB_mean_criterion = mean[BOB_n-1]
		if WOW_n == 0:
			self.WOW_mean_criterion = -float("inf")
		else:
			self.WOW_mean_criterion = mean[-(WOW_n)]
		print("Execute rank_based_mean_criterion")


	def create_lot_BOB_WOW_group(self):
		criterion = [self.BOB_mean_criterion, self.WOW_mean_criterion]
		with open('../result/criterion.txt', 'w') as f:
			for c in criterion:
				f.write("%s\n" % c)
		#self.raw_lot_data['VALUE'].astype(float)
		#self.raw_lot_data_temp['VALUE'].astype(float)
		BOB_lots = self.raw_lot_data_temp.loc[(self.raw_lot_data_temp.VALUE['std'] < self.std_criterion) & (self.raw_lot_data_temp.VALUE['mean'] > self.BOB_mean_criterion)].index
		WOW_lots = self.raw_lot_data_temp.loc[(self.raw_lot_data_temp.VALUE['std'] < self.std_criterion) & (self.raw_lot_data_temp.VALUE['mean'] < self.WOW_mean_criterion)].index
		self.lot_BOB_WOW_Group = self.lot_data.copy()
		self.lot_BOB_WOW_Group['BOB'] = self.lot_BOB_WOW_Group['ROOT_LOT_ID'].isin(BOB_lots)
		self.lot_BOB_WOW_Group['WOW'] = self.lot_BOB_WOW_Group['ROOT_LOT_ID'].isin(WOW_lots)
		self.lot_BOB_WOW_Group.to_csv('../result/lot_BOB_WOW_Group.csv', sep = ',')
		print("Created lot_BOB_WOW_Group: {}".format(len(self.lot_BOB_WOW_Group)))
		

	def create_eqp_perf(self):
		grouped = self.lot_BOB_WOW_Group.groupby('TO')
		self.eqp_perf = grouped.agg([np.count_nonzero, np.mean, np.std])

		BOB = self.lot_BOB_WOW_Group.loc[self.lot_BOB_WOW_Group['BOB'] == True].groupby('TO').VALUE.agg(['mean','std'])
		BOB.columns = pd.MultiIndex.from_product([['BOB_stat'], BOB.columns])

		WOW = self.lot_BOB_WOW_Group.loc[self.lot_BOB_WOW_Group['WOW'] == True].groupby('TO').VALUE.agg(['mean','std'])
		WOW.columns = pd.MultiIndex.from_product([['WOW_stat'], WOW.columns])


		self.eqp_perf = pd.merge(self.eqp_perf, BOB, left_index=True, right_index=True, how='left')
		self.eqp_perf = pd.merge(self.eqp_perf, WOW, left_index=True, right_index=True, how='left')

		BOB_step_perf = self.lot_BOB_WOW_Group.loc[self.lot_BOB_WOW_Group['BOB'] == True].groupby('STEP_SEQ').ROOT_LOT_ID.count()
		WOW_step_perf = self.lot_BOB_WOW_Group.loc[self.lot_BOB_WOW_Group['WOW'] == True].groupby('STEP_SEQ').ROOT_LOT_ID.count()

		self.eqp_perf['BOB/step'] = 0.0
		def BOB_step(eqp):
			try:
			    count = self.eqp_perf.loc[eqp]['BOB', 'count_nonzero']
			    step = eqp.split("_")[0].strip()
			    return count/BOB_step_perf[step]
			except KeyError:
				pass
		def WOW_step(eqp):
			try:
			    count = self.eqp_perf.loc[eqp]['WOW', 'count_nonzero']
			    step = eqp.split("_")[0].strip()
			    return count/WOW_step_perf[step]
			except KeyError:
				pass

		self.eqp_perf['BOB/step'] = self.eqp_perf.index.to_series().apply(BOB_step)
		self.eqp_perf['WOW/step'] = self.eqp_perf.index.to_series().apply(WOW_step)
		print("Created eqp_perf: {}".format(len(self.eqp_perf)))

	def show_data(self):
		print(self.raw_lot_data)

	def Get_data(self):
		return self.data

	"""
	LOT level
	""" 

if __name__ == '__main__':
	# 1. Input raw data
	preprocessing = Preprocessing('../input/raw_data.txt')

	# 2. Preprocess - 시작부터 종료까지의 전체 STEP이 기록되지 않은 LOT/Wafer 제외 
	preprocessing.Incomplete_wafer(preprocessing.data,)

	# 3. LOT 내 최소 Wafer 수 제한
	preprocessing.wafer_count(preprocessing.data, 23)

	# 4. 분석 시작/종료 STEP 기준 최적 기간 추천
	#print("recommended period")
	#print(preprocessing.recommend_period(preprocessing.data, start_step='STEP_001', end_step='STEP_075', inc_days = 14))

	# 5. 각 STEP의 기간 추출
	preprocessing.period(preprocessing.data)

	# 6. 분석 대상 STEP 추출
	preprocessing.main(preprocessing.data)

	preprocessing.diff_step_flow(preprocessing.data)
	#print(len(preprocessing.data))
	preprocessing.diff_eqp_flow(preprocessing.data)

	preprocessed_data = preprocessing.data
	print("export preprocessed_data")
	#preprocessed_data.to_sql("preprocessed_data", preprocessing.con, if_exists="replace", index = False)
	#preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)


	
	#preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)
	classifier = LOT_Classifier(preprocessed_data)
	classifier.create_raw_lot_data()
	classifier.create_lot_data()
	#classifier.raw_lot_data.to_csv('../result/raw_lot_data.csv', sep=',', index = False)
	classifier.relative_ratio_std_criterion()
	classifier.relative_ratio_mean_criterion()
	classifier.create_lot_BOB_WOW_group()
	#classifier.lot_BOB_WOW_Group.to_csv('../result/lot_BOB_WOW_group.csv', sep=',')
	classifier.create_eqp_perf()
	#classifier.eqp_perf.to_csv('../result/eqp_perf.csv', sep=',')
	#classifier.show_data()


