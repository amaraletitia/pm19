import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from scipy import stats
#import matplotlib.pyplot as plt
import datetime
import os
import sqlite3
import time
class Data(object):
	def __init__(self, data_source):
		self.data = self.Setup_input(data_source)
		print("processing begins: {}".format(len(self.data)))
		self.Remove_duplicates(self.data)
		self.Remove_duplicates_chamber(self.data)
		self.Multiple_VALUE(self.data)
		self.chamber_variety(self.data)
		#self.data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)

	

	def Setup_input(self, data_source):
		def short_step(x):
			#count = 0
			for i in range(len(x)):
				if x[i].isdigit():
					return 'S' + x[i:]
				#count+=1

			#return 'S' + x[5:]

		def short_eqp(x):
			return 'E' + x[4:7]

		raw_data = pd.read_csv(data_source, sep = '\t', index_col = False, dtype={'ROOT_LOT_ID':'str', 'WAFER_ID':'str', 'STEP_SEQ':'str', 'TKIN_TIME':'str', 'TKOUT_TIME':'str', 'EQP_ID':'str', 'EQP_MODEL_NAME':'str', 'PPID':'str', 'CHAMBER_ID':'str', 'UNIT_ID':'str', 'VALUE':'float'})
		#raw_data = raw_data[:10000]
		#raw_data = pd.read_csv(data_source, index_col = False)
		#raw_data['STEP_SEQ'] = "AB" + "0000" + raw_data['STEP_SEQ'].str.slice(5,8,1)
		#print(raw_data['STEP_SEQ'])
		#raw_data['STEP_SEQ'] = raw_data['STEP_SEQ'].apply(short_step)
		#print(raw_data['STEP_SEQ'])
		#raw_data['EQP_ID'] = raw_data['EQP_ID'].apply(short_eqp)
		print("Before deleting test wafer: {}".format(len(raw_data)))
		#raw_data = raw_data.loc[raw_data['LOT_ID'].apply(lambda x: x.split('.')[1]).str.isdigit()]
		print("After deleting test wafer: {}".format(len(raw_data)))
		raw_data['CASE_ID'] = raw_data['ROOT_LOT_ID'] + '_' + raw_data['WAFER_ID'].astype(str)
		raw_data['TKIN_TIME'] =  pd.to_datetime(raw_data['TKIN_TIME'], format='%Y-%m-%d %H:%M:%S')
		raw_data['TKOUT_TIME'] =  pd.to_datetime(raw_data['TKOUT_TIME'], format='%Y-%m-%d %H:%M:%S')

		return raw_data

	def Remove_duplicates(self, raw_data):
		print("##Execute Remove_duplicates")
		Preprocessed_data_1 = raw_data.drop_duplicates()
		Preprocessed_data_1 = Preprocessed_data_1.reset_index(drop=True)
		self.data = Preprocessed_data_1
		print("##Finish Remove_duplicates: {}".format(len(self.data)))

	def Remove_duplicates_chamber(self, Preprocessed_data_1):
		print("##Execute Remove_duplicates_chamber")
		Preprocessed_data_2 = Preprocessed_data_1.copy()
		columns = list(Preprocessed_data_2.columns)
		columns_not_chamber_id = [x for x in columns if x != 'CHAMBER_ID']
		#print(columns_not_chamber_id)
		dp = Preprocessed_data_2.loc[Preprocessed_data_2.duplicated(columns_not_chamber_id, keep=False)]
		#dp = Preprocessed_data_2.loc[Preprocessed_data_2.duplicated(['ROOT_LOT_ID', 'WAFER_ID', 'CASE_ID', 'STEP_SEQ', 'TKIN_TIME', 'TKOUT_TIME', 'EQP_ID', 'EQP_MODEL_NAME', 'PPID', 'UNIT_ID', 'VALUE'], keep=False)]
		#print(dp)

		#CHAMEBER_ID & UNIT_ID가 같은 경우 하나로 합쳐주는 작업
		columns_not_chamber_unit_id = [x for x in columns if x !='CHAMBER_ID' and x != 'UNIT_ID']
		#print(columns_not_chamber_unit_id)
		try:
			duplicate_list = dp.groupby(columns_not_chamber_unit_id).apply(lambda x: list(x.index)).tolist()
			print("len of chamber_unit_id_duplicates: {}".format(len(duplicate_list)))
			idx = []
			del_idx = []
			value = []
			for pair in duplicate_list:
				chamber_id = Preprocessed_data_2['CHAMBER_ID'][pair[0]] + '-' + Preprocessed_data_2['CHAMBER_ID'][pair[1]]
				idx.append(pair[0])
				value.append(chamber_id)
				del_idx.append(pair[1])
				#value.append(chamber_id)
			#print(len(Preprocessed_data_2))
			Preprocessed_data_2.drop(Preprocessed_data_2.index[del_idx], inplace = True)
			Preprocessed_data_2.loc[idx, 'CHAMBER_ID'] = value
			Preprocessed_data_2 = Preprocessed_data_2.reset_index(drop=True)
		except AttributeError:
			pass
		#print(duplicate_list)
		#print(len(Preprocessed_data_2))
		self.data = Preprocessed_data_2
		print("##Finish Remove_duplicates_chamber: {}".format(len(self.data)))

	def Multiple_VALUE(self, Preprocessed_data_2):
		print("##Execute Multiple_VALUE")
		VALUE_CNT = Preprocessed_data_2.groupby('CASE_ID').VALUE.nunique()
		Preprocessed_data_3 = Preprocessed_data_2[Preprocessed_data_2.CASE_ID.isin(VALUE_CNT[VALUE_CNT == 1].index)]
		Preprocessed_data_3 = Preprocessed_data_3.reset_index(drop=True)
		self.data = Preprocessed_data_3
		print("##Finish Multiple_VALUE: {}".format(len(self.data)))

	def chamber_variety(self, Preprocessed_data_5, chamber_variety_count=20):
		print("##Execute chamber_variety, count: {}".format(chamber_variety_count))
		#설비의 CHAMBER 종류가 20개 이상인 경우 CHAMBER는 NULL 처리
		user_defined_chamber_count = chamber_variety_count
		distinct_chamber_count = Preprocessed_data_5.groupby('EQP_ID').CHAMBER_ID.nunique()
		Preprocessed_data_6 = Preprocessed_data_5.copy()

		Preprocessed_data_6.loc[Preprocessed_data_6['EQP_ID'].isin(distinct_chamber_count[distinct_chamber_count >= user_defined_chamber_count].index), 'CHAMBER_ID']='NULL'     
		
		Preprocessed_data_6.sort_values(by=['CASE_ID','STEP_SEQ'])
		self.data = Preprocessed_data_6
		print("##Finish chamber_variety: {}".format(len(self.data)))

	def Get_data(self):
		return self.data




class Preprocessing(object):
	def __init__(self, data_source):
		self.makeDir()
		print(self.TARGET_FILE_FULL_PATH)
		self.con = sqlite3.connect(self.TARGET_FILE_FULL_PATH)
		self.data = Data(data_source)
		self.data = self.data.Get_data()
		"""		
		self.wafer_count(self.data, 23)
		self.chamber_variety(self.data, 20)
		self.period(self.data)
		self.main(self.data)
		"""

	def makeDir(self):
		self.BASE_DIR   =  os.path.abspath('.')
		self.TARGET_DIR =  os.path.join(self.BASE_DIR, "DB")
		#self.TARGET_FILE = '{}.db'.format('DB_' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
		self.db_name = str(time.time())
		self.TARGET_FILE = '{}.db'.format('DB_' + self.db_name)
		with open('../result/db_name.txt', 'w') as f:
			f.write("%s\n" %self.db_name)
		self.TARGET_FILE_FULL_PATH = os.path.join(self.TARGET_DIR, self.TARGET_FILE)
		if not os.path.isdir( self.TARGET_DIR ):
			os.makedirs( self.TARGET_DIR )

	def Incomplete_wafer(self, Preprocessed_data_3, start, end):
		print("##Execute Incomplete_wafer, Start_step: {}, End_step: {}".format(start,end))
		user_defined_start = start
		user_defined_end = end

		START_STEP = Preprocessed_data_3.loc[(Preprocessed_data_3['STEP_SEQ'] == user_defined_start)].CASE_ID
		START_STEP = START_STEP.reset_index(drop=True)
		END_STEP = Preprocessed_data_3.loc[(Preprocessed_data_3['STEP_SEQ'] == user_defined_end)].CASE_ID
		END_STEP = END_STEP.reset_index(drop=True)

		Preprocessed_data_4 = Preprocessed_data_3[Preprocessed_data_3.CASE_ID.isin(list(set(START_STEP) & set(END_STEP)))]
		self.data = Preprocessed_data_4
		print("##Finish Incomplete_wafer: {}".format(len(self.data)))

	def wafer_count(self, Preprocessed_data_4, wafer_count=20):
		print("##Execute wafer_count, count: {}".format(wafer_count))
		#LOT 내 Wafer 수가 23개 미만인 LOT 제외
		user_defined_wafer_count = wafer_count
		distinct_wafer_count = Preprocessed_data_4.groupby('ROOT_LOT_ID').CASE_ID.nunique()
		#distinct_wafer_count[distinct_count < 23].index
		Preprocessed_data_5 = Preprocessed_data_4[Preprocessed_data_4['ROOT_LOT_ID'].isin(distinct_wafer_count[distinct_wafer_count >= user_defined_wafer_count].index)]
		self.data = Preprocessed_data_5
		print("##Finish wafer_count: {}".format(len(self.data)))




	

	def diff_step_flow(self, Preprocessed_data_6):
		print("##Execute diff_step_flow")
		def checkEqual1(iterator):
		    iterator = iter(iterator)
		    try:
		        first = next(iterator)
		    except StopIteration:
		        return True
		    return all(first == rest for rest in iterator)

		distinct_case_step_6 = Preprocessed_data_6.groupby(['ROOT_LOT_ID','CASE_ID']).STEP_SEQ.apply(list)
		
		Preprocessed_data_7 = Preprocessed_data_6.copy()
		count=0
		l_count =0
		list_lot = []
		for lot, wafer_steps in distinct_case_step_6.groupby(level=0):
		    count+=1
		    if all(x==wafer_steps[0] for x in wafer_steps):
		        continue
		        
		    else:
		        mask = Preprocessed_data_7['ROOT_LOT_ID']== lot
		        Preprocessed_data_7.drop(Preprocessed_data_7[Preprocessed_data_7['ROOT_LOT_ID']== lot].index, inplace=True)
		Preprocessed_data_7 = Preprocessed_data_7.reset_index(drop=True)
		self.data = Preprocessed_data_7
		print("##Finish diff_step_flow: {}".format(len(self.data)))

	def diff_eqp_flow(self, Preprocessed_data_7):
		print("##Execute diff_eqp_flow")
		def checkEqual1(iterator):
		    iterator = iter(iterator)
		    try:
		        first = next(iterator)
		    except StopIteration:
		        return True
		    return all(first == rest for rest in iterator)
		Preprocessed_data_8_STQP = Preprocessed_data_7[['ROOT_LOT_ID', 'CASE_ID','STEP_SEQ', 'EQP_ID']]
		Preprocessed_data_8_STQP['STQP'] = Preprocessed_data_8_STQP['STEP_SEQ'] + '_' + Preprocessed_data_8_STQP['EQP_ID']
		Preprocessed_data_8_STQP

		 
		distinct_case_eqp_8 = Preprocessed_data_8_STQP.groupby(['ROOT_LOT_ID','CASE_ID']).STQP.apply(list)
		freq_eqp_case_ids = []
		for lot, wafer_eqps in distinct_case_eqp_8.groupby(level=0):
		    eqps = []
		    eqps_count = []
		    for wafer_eqp in wafer_eqps:
		        if wafer_eqp in eqps:
		            eqps_index = eqps.index(wafer_eqp)
		            eqps_count[eqps_index] += 1
		        else:
		            eqps.append(wafer_eqp)
		            eqps_count.append(1)
		        
		    freq_eqps_index = eqps_count.index(max(eqps_count))
		    #print(freq_eqps_index)
		    #print(eqps_count)
		    freq_eqps = eqps[freq_eqps_index]
		    #print(freq_eqps)
		    #print(wafer_eqps)
		    #hashed = np.array([hash(s) for s in eg])
		    #[x+1 if x >= 45 else x+5 for x in l]
		    case_ids = wafer_eqps[[True if eqp== freq_eqps else False for eqp in wafer_eqps]].index.droplevel(0).tolist()
		    freq_eqp_case_ids += case_ids
		Preprocessed_data_8 = Preprocessed_data_7.copy()
		Preprocessed_data_8 = Preprocessed_data_8.loc[Preprocessed_data_8['CASE_ID'].isin(freq_eqp_case_ids)]
		self.data = Preprocessed_data_8
		print("##Finish diff_eqp_flow: {}".format(len(self.data)))

	def recommend_period(self, Preprocessed_data_6, start_step, end_step, inc_days = 14):
		print("##Execute recommend_period, Start_step: {}, End_step: {}".format(start_step, end_step))
		Preprocessed_data_Period_B = Preprocessed_data_6.copy()
		Preprocessed_data_Period_B['TKIN_TIME'] = pd.DatetimeIndex(Preprocessed_data_Period_B.TKIN_TIME).normalize()
		Preprocessed_data_Period_B['TKOUT_TIME'] = pd.DatetimeIndex(Preprocessed_data_Period_B.TKIN_TIME).normalize()
		step_001_tkin = Preprocessed_data_Period_B.loc[Preprocessed_data_Period_B['STEP_SEQ'] == start_step,'TKIN_TIME']
		start_begin = min(step_001_tkin)
		start_finish = max(step_001_tkin)

		step_075_tkin = Preprocessed_data_Period_B.loc[Preprocessed_data_Period_B['STEP_SEQ'] == end_step, 'TKOUT_TIME']
		end_begin = min(step_075_tkin)
		end_finish = max(step_075_tkin)

		#inc_days = 14
		start = start_begin
		max_start = start_begin
		start_max_wafer_count = 0
		chosen = Preprocessed_data_Period_B['CASE_ID']
		while start < start_finish:
		    to = start + datetime.timedelta(days=inc_days)
		    trial = Preprocessed_data_Period_B.loc[(Preprocessed_data_Period_B['STEP_SEQ'] == start_step) & (Preprocessed_data_Period_B['TKIN_TIME'] >= start) &  (Preprocessed_data_Period_B['TKIN_TIME'] < to), 'CASE_ID']
		    
		    interval_wafer_count = len(Preprocessed_data_Period_B.loc[Preprocessed_data_Period_B['CASE_ID'].isin(trial), 'CASE_ID'])
		    if to > start_finish:
		        break
		    if interval_wafer_count > start_max_wafer_count:
		        max_start = start
		        start_max_wafer_count = interval_wafer_count
		        chosen = trial
		    start += datetime.timedelta(days=1)

		end = end_begin
		max_end = end_begin
		end_max_wafer_count = 0
		Preprocessed_data_Period_B = Preprocessed_data_Period_B.loc[Preprocessed_data_Period_B['CASE_ID'].isin(chosen)]
		while end < end_finish:
		    to = end + datetime.timedelta(days=inc_days)
		    interval_wafer_count = len(Preprocessed_data_Period_B.loc[Preprocessed_data_Period_B['CASE_ID'].isin(Preprocessed_data_Period_B.loc[(Preprocessed_data_Period_B['STEP_SEQ'] == end_step) & (Preprocessed_data_Period_B['TKOUT_TIME'] >= end) &  (Preprocessed_data_Period_B['TKIN_TIME'] < to), 'CASE_ID'])])
		    if to > end_finish:
		        break
		    if interval_wafer_count > end_max_wafer_count:
		        max_end = end
		        end_max_wafer_count = interval_wafer_count 
		        #print(max_wafer_count)
		    end += datetime.timedelta(days=1)
		max_start_f = (max_start+datetime.timedelta(days=inc_days)).strftime("%Y-%m-%d")
		max_start_b = max_start.strftime("%Y-%m-%d")
		max_end_f = (max_end + datetime.timedelta(days=inc_days)).strftime("%Y-%m-%d")
		max_end_b = max_end.strftime("%Y-%m-%d")
		return max_start_b, max_start_f, max_end_b, max_end_f
		print("##Finish recommend_period: {}~{}, {}~{}".format(max_start_f,max_start_f,max_end_b,max_end_f))



	def period(self, Preprocessed_data_6, periods = None):
		#전처리 데이터(Preprocessed_data_6) 대상 기간 추출
		print("##Execute period")
		"""
		user_defined_periods = {'STEP_001': ['2016-11-19', '2016-12-03'], 
		                        'STEP_041':['2017-01-17', '2017-01-27'], 
		                        'STEP_048':['2017-01-24', '2017-02-06'], 
		                        'STEP_065':['2017-02-03', '2017-02-17'], 
		                        'STEP_075': ['2017-02-14', '2017-02-28']}
		"""
		"""
		STEP_001, 2016-11-19, 2016-12-03; STEP_041, 2017-01-17, 2017-01-27; STEP_048, 2017-01-24, 2017-02-06; STEP_065, 2017-02-03, 2017-02-17; STEP_075, 2017-02-14, 2017-02-28

		AB0000001, 2016-11-19, 2016-12-03; AB0000041, 2017-01-17, 2017-01-27; AB0000048, 2017-01-24, 2017-02-06; AB0000065, 2017-02-03, 2017-02-17; AB0000075, 2017-02-14, 2017-02-28
		"""
		user_defined_periods = periods
		Preprocessed_data_6_Period = Preprocessed_data_6.copy()
		for key, value in user_defined_periods.items():
			#print(key)
			#print(Preprocessed_data_6_Period.loc[-Preprocessed_data_6_Period['CASE_ID'].isin(Preprocessed_data_6_Period.groupby('STEP_SEQ').get_group(key)['CASE_ID']), 'CASE_ID'])
			#Preprocessed_data_6_Period = Preprocessed_data_6_Period.loc[Preprocessed_data_6_Period['CASE_ID'].isin(Preprocessed_data_6_Period.loc[(((Preprocessed_data_6_Period['STEP_SEQ'] == key) & (Preprocessed_data_6_Period['TKIN_TIME'] >= value[0]) &  (Preprocessed_data_6_Period['TKOUT_TIME'] <= value[1])) | (Preprocessed_data_6_Period.groupby('STEP_SEQ').get_group(key)['CASE_ID'] )), 'CASE_ID'])]
			Preprocessed_data_6_Period = Preprocessed_data_6_Period.loc[Preprocessed_data_6_Period['CASE_ID'].isin(Preprocessed_data_6_Period.loc[((Preprocessed_data_6_Period['STEP_SEQ'] == key) & (Preprocessed_data_6_Period['TKIN_TIME'] >= value[0]) & (Preprocessed_data_6_Period['TKOUT_TIME'] <= value[1])), 'CASE_ID']) | -Preprocessed_data_6_Period['CASE_ID'].isin(Preprocessed_data_6_Period.groupby('STEP_SEQ').get_group(key)['CASE_ID'])]

			"""
		    if key != 'AB0000041':
		        Preprocessed_data_6_Period = Preprocessed_data_6_Period.loc[Preprocessed_data_6['CASE_ID'].isin(Preprocessed_data_6.loc[
		((Preprocessed_data_6['STEP_SEQ'] == key) & (Preprocessed_data_6['TKIN_TIME'] >= value[0]) &  (Preprocessed_data_6['TKOUT_TIME'] <= value[1])), 'CASE_ID'])]
		    else:
		        Preprocessed_data_6_Period = Preprocessed_data_6_Period.loc[Preprocessed_data_6_Period['CASE_ID'].isin(Preprocessed_data_6_Period.loc[(((Preprocessed_data_6_Period['STEP_SEQ'] == 'AB0000041') & (Preprocessed_data_6_Period['TKIN_TIME'] >= value[0]) &  (Preprocessed_data_6_Period['TKOUT_TIME'] <= value[1])) | ((Preprocessed_data_6_Period['STEP_SEQ'] != 'AB0000041'))), 'CASE_ID'])]
			"""
		self.data = Preprocessed_data_6_Period
		#self.data['CHAMBER_ID'].to_csv('../input/check.csv', sep=',', index = False)
		print("##Execute period: {}".format(len(self.data)))
		
	def main(self, Preprocessed_data_6_Period, steps=None):
		#전처리 데이터(Preprocessed_data_6) 대상 주요 스텝 도출
		print("##Execute main")
		#user_defined_main_steps = ['S038', 'S039', 'S040', 'S041', 'S042', 'S043', 'S044', 'S047', 'S048', 'S049', 'S050', 'S051', 'S052', 'S053', 'S054', 'S055', 'S057', 'S059', 'S061', 'S062', 'S063', 'S064', 'S065', 'S066', 'S069', 'S070', 'S074', 'S075']

		#user_defined_main_steps = ['S038', 'S039', 'S040', 'S041', 'S042', 'S043', 'S044', 'S047', 'S048', 'S049']

		"""
		AB0000038; AB0000039; AB0000040; AB0000041; AB0000042; AB0000043; AB0000044; AB0000047; AB0000048; AB0000049; AB0000050; AB0000051; AB0000052; AB0000053; AB0000054; AB0000055; AB0000057; AB0000059; AB0000061; AB0000062; AB0000063; AB0000064; AB0000065; AB0000066; AB0000069; AB0000070; AB0000074; AB0000075                                    
		"""

		user_defined_main_steps = steps

		Preprocessed_data_6_Main = Preprocessed_data_6_Period.loc[Preprocessed_data_6_Period['STEP_SEQ'].isin(user_defined_main_steps)]
		self.data = Preprocessed_data_6_Main
		print("##Finish main: {}".format(len(self.data)))
		
		

	def export_data(self):
		self.data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)

	##outlier 제거 fucntion

	def detect_outliers(self, m=2):
		mean = self.data['VALUE'].mean(axis=0)
		std = self.data['VALUE'].mean(axis=0)
		self.data = self.data[abs(self.data['VALUE'] - mean) <m * std ]


if __name__ == '__main__':
	preprocessing = Preprocessing('../input/raw_data.txt')
	preprocessing.Incomplete_wafer(preprocessing.data, 'STEP_001', 'STEP_075')
	print(len(preprocessing.data))
	print("process 4 finished")
	preprocessing.wafer_count(preprocessing.data, 20)
	print(len(preprocessing.data))
	print("process 5 finished")
	#preprocessing.chamber_variety(preprocessing.data, 20)
	#print(len(preprocessing.data))
	#print("process 6 finished")
	print(preprocessing.recommend_period(preprocessing.data, start_step='STEP_001', end_step='STEP_075', inc_days = 14))
	preprocessing.period(preprocessing.data)
	print(len(preprocessing.data))
	print("process period finished")
	preprocessing.main(preprocessing.data)
	print(len(preprocessing.data))
	print("process main finished")
	preprocessing.diff_step_flow(preprocessing.data)
	#print(len(preprocessing.data))
	preprocessing.diff_eqp_flow(preprocessing.data)
	#print(len(preprocessing.data))
	preprocessing.detect_outliers()
	print(len(preprocessing.data))
	print("detect outliers")
	print("export preprocessed_data.csv")
	preprocessing.export_data()

















