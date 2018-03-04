from LOT_Classifier import LOT_Classifier
from Preprocessing import Preprocessing
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from scipy import stats
import math

class LOT_Analysis(object):
	def __init__(self,con):
		with open("../result/criterion.txt", 'r') as f:
			self.BOB_mean_criterion = float(f.readline())
			self.WOW_mean_criterion = float(f.readline())
		self.con = con
		self.lot_data = pd.read_sql_query("select * from lot_data;", self.con)
		self.lot_BOB_WOW_Group = pd.read_sql_query("select * from lot_BOB_WOW_Group;", self.con)
		self.eqp_perf = pd.read_sql_query("select * from eqp_perf;", self.con)
		#self.eqp_perf = self.eqp_perf[2:]
		#self.eqp_perf.set_index('Unnamed: 0', inplace = True)
		#self.eqp_perf.index.name = 'TO'
		self.eqp_perf.set_index('TO', inplace = True)
		columns = [('VALUE', 'count_nonzero'), ('VALUE', 'mean'), ('VALUE', 'std'), ('BOB', 'count_nonzero'), ('BOB', 'mean'), ('BOB', 'std'), ('WOW', 'count_nonzero'), ('WOW', 'mean'), ('WOW', 'std'), ('BOB_stat', 'mean'), ('BOB_stat', 'std'), ('WOW_stat', 'mean'), ('WOW_stat', 'std'), ('BOB/step', 'mean'), ('WOW/step', 'mean')]
		self.eqp_perf.columns = pd.MultiIndex.from_tuples(columns)
		self.eqp_perf = self.eqp_perf.apply(pd.to_numeric)
		self.eqp_stat = pd.concat([self.eqp_perf['VALUE', 'count_nonzero'], self.eqp_perf['VALUE', 'mean']], axis=1, keys=['count', 'mean'])

	def create_KS_test(self, alpha_normality=0.05):
		print("KS_test begins, alpha = {}".format(alpha_normality))
		self.user_defined_alpha_normality = alpha_normality

		def eval_normality(unique_eqp):
		    eqp = self.lot_data[self.lot_data['TO'] == unique_eqp]
		    if len(eqp['VALUE']) > 3:
		        d, p_value = stats.shapiro(eqp['VALUE'])
		    else:
		        p_value = 0.0
		    return p_value

		self.eqp_stat['normality_p_value'] = self.eqp_stat.index.to_series().apply(eval_normality)
		self.eqp_stat['Normality'] = self.eqp_stat['normality_p_value'] > self.user_defined_alpha_normality
		print("KS_test completed: {}".format(len(self.eqp_stat)))

	def create_ANOVA(self, alpha_ANOVA = 0.05):
		print("ANOVA begins, alpha = {}".format(alpha_ANOVA))
		#step별 정리
		unique_Steps = self.lot_data['STEP_SEQ'].unique()
		self.user_defined_alpha_ANOVA = alpha_ANOVA

		for unique_Step in unique_Steps:
		    #self.lot_data를 특정 STEP으로 filtering
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    
		    unique_eqps = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]['TO'].unique()

		    #step 내 설비들의 VALUE를 저장
		    step_eqp_values = {}
		    for unique_eqp in unique_eqps:
		        #filtered['TO']가 필요, 모든 observation이 필요하므로
		        step_eqp_values[unique_eqp]=(filtered.loc[filtered['TO']==unique_eqp, 'VALUE'])

		    statistic, p_value = stats.f_oneway(*step_eqp_values.values())


		    self.eqp_stat.loc[unique_eqps, 'anova_p_value'] = p_value

		self.eqp_stat['ANOVA'] = self.eqp_stat['anova_p_value'] < self.user_defined_alpha_ANOVA
		print("ANOVA completed: {}".format(len(self.eqp_stat)))

	def create_Kruskal(self, alpha_KRUSKAL=0.05):
		print("KRUSKAL begins, alpha = {}".format(alpha_KRUSKAL))
		#KRUSKAL
		self.user_defined_alpha_KRUSKAL = alpha_KRUSKAL
		#step별 정리
		unique_Steps = self.lot_data['STEP_SEQ'].unique()
		for unique_Step in unique_Steps:
		    #self.lot_data를 특정 STEP으로 filtering
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    
		    unique_eqps = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]['TO'].unique()

		    #step 내 설비들의 VALUE를 저장
		    step_eqp_values = {}
		    for unique_eqp in unique_eqps:
		        #filtered['TO']가 필요, 모든 observation이 필요하므로 
		        step_eqp_values[unique_eqp]=(filtered.loc[filtered['TO']==unique_eqp, 'VALUE'])

		    statistic, p_value = stats.kruskal(*step_eqp_values.values())


		    self.eqp_stat.loc[unique_eqps, 'kruskal_p_value'] = p_value
		self.eqp_stat['KRUSKAL'] = self.eqp_stat['kruskal_p_value'] < self.user_defined_alpha_KRUSKAL
		print("KRUSKAL completed: {}".format(len(self.eqp_stat)))
		self.eqp_stat.to_csv('../result/eqp_stat.csv', sep=',')

	def create_stat_analysis(self, alpha_LC = 0.05, alpha_NLC = 0.05):
		print("Linear_Contrasts begins, alpha_LC = {}, alpha_NLC = {}".format(alpha_LC, alpha_NLC))
		def Linear_Contrast(row, other_rows, unique_Step):
		    #N is total observations
		    N = sum(other_rows['VALUE', 'count_nonzero'])
		    
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    filtered_VALUE = filtered.loc[filtered['TO'].isin(other_rows.index), 'VALUE']
		    
		    #calculate SS_error
		    sum_y_squared = sum([value**2 for value in filtered_VALUE])
		    SS_error = sum_y_squared - sum(filtered.groupby('TO').sum()['VALUE']**2/filtered.groupby('TO').size())
		    
		    #exclude 비교대상
		    other_rows = other_rows.drop(row.name)
		    
		    #k is # groups
		    k = len(other_rows.index)
		    
		    #calcualte SS contrast
		    L = k*row['VALUE', 'mean']
		    for mean in other_rows['VALUE', 'mean']:
		        L -= mean
		    
		    denominator = k*k/row['VALUE', 'count_nonzero']
		    for no_obs in other_rows['VALUE', 'count_nonzero']:
		        denominator += 1/no_obs
		        N +=no_obs
		        
		    #degrees of freedom
		    DFbetween = 1
		    DFwithin = N - k
		    
		    MS_error = SS_error / DFwithin
		    
		    std = math.sqrt(MS_error*denominator)
		    
		    t_contrast = abs(L)/std
		    
		    p_value = stats.t.sf(t_contrast, DFwithin)
		    return p_value

		def Nonparametric_Linear_Contrast(row, other_rows, unique_Step):
		    #N is total observations
		    other_rows = other_rows.drop(row.name)
		    
		    
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    other_rows_filtered_VALUE = filtered.loc[filtered['TO'].isin(other_rows.index), 'VALUE']
		    #print(other_rows_filtered_VALUE)
		    row_filtered_VALUE = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    #print(row_filtered_VALUE)
		    statistic, p_value = stats.mannwhitneyu(other_rows_filtered_VALUE, row_filtered_VALUE)
		    #print(p_value)
		    return p_value


		self.eqp_stat_LC = self.eqp_stat.copy()
		self.user_defined_alpha_LC = alpha_LC
		self.user_defined_alpha_NLC = alpha_NLC

		self.eqp_stat_LC['LC_p_value'] = 1.0
		self.eqp_stat_LC['LCresult'] = 'DUMMY'

		unique_Steps = self.lot_data['STEP_SEQ'].unique()
		#count_k=0
		#count_a=0
		#count = 0
		for unique_Step in unique_Steps:
		    #count +=1
		    #self.lot_data를 특정 STEP으로 filtering
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    #해당 step의 self.eqp_stat, filtered['TO'].unique()가 필요, 어떤 eqp가 있는지가 필요하므로
		    self.step_eqp_stat = self.eqp_stat_LC.loc[filtered['TO'].unique()]
		    
		    #pass Normality test
		    if all(self.step_eqp_stat['normality_p_value'] > self.user_defined_alpha_normality):
		        #count_a+=1
		        #ANOVA result: 유의미한 차이 없음
		        if (self.step_eqp_stat['anova_p_value'] > self.user_defined_alpha_ANOVA).any():
		            #self.eqp_stat.loc[self.step_eqp_stat.index]['result'] = 'DUMMY' #왜 안되냐?
		            self.eqp_stat_LC['LCresult'][self.step_eqp_stat.index] = 'DUMMY'
		            #print(self.eqp_stat.loc[self.step_eqp_stat.index]['result'])
		        else:
		            #Linear Contrast 수행
		            self.sorted_eqp_perf = self.eqp_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')],ascending=False)
		            #print(self.sorted_eqp_perf)
		            for index, row in self.sorted_eqp_perf.iterrows():
		                p_value = Linear_Contrast(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.eqp_stat_LC['LC_p_value'][row.name]  = p_value
		                ###Linear Contrast 결과 유의미한 경우
		                if p_value < self.user_defined_alpha_LC:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'BOB'
		                else:
		                    break
		            self.sorted_eqp_perf = self.eqp_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')])            
		            for index, row in self.sorted_eqp_perf.iterrows():
		                p_value = Linear_Contrast(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.eqp_stat_LC['LC_p_value'][row.name]  = p_value
		                if p_value < self.user_defined_alpha_LC:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'WOW'
		                else:
		                    break
		                    
		    #Non-parametric method
		    else:
		        #count_k+=1
		        if (self.step_eqp_stat['kruskal_p_value'] > self.user_defined_alpha_KRUSKAL).any():
		            self.eqp_stat_LC['LCresult'][self.step_eqp_stat.index] = 'DUMMY'
		            
		        else:
		            ###non-parametric linear contrast
		            
		            #from the best
		            self.sorted_eqp_perf = self.eqp_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')],ascending=False)
		            for index, row in self.sorted_eqp_perf.iterrows():
		                p_value = Nonparametric_Linear_Contrast(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.eqp_stat_LC['LC_p_value'][row.name]  = p_value
		                ###Linear Contrast 결과 유의미한 경우
		                if p_value < self.user_defined_alpha_NLC:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'BOB'
		                else:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'DUMMY'
		                    break
		            #from the worst
		            self.sorted_eqp_perf = self.eqp_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')])            
		            for index, row in self.sorted_eqp_perf.iterrows():
		                p_value = Nonparametric_Linear_Contrast(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.eqp_stat_LC['LC_p_value'][row.name]  = p_value
		                if p_value < self.user_defined_alpha_NLC:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'WOW'
		                else:
		                    self.eqp_stat_LC['LCresult'][row.name] = 'DUMMY'
		                    break
		self.eqp_stat_LC.to_sql("eqp_stat_LC", self.con, if_exists="replace")
		self.eqp_stat_LC.to_csv('../result/eqp_stat_LC.csv', sep=',')
		print("Linear_Contrasts completed")
                        
	

	def create_mt_stat_test(self, alpha_tt = 0.01, alpha_ut = 0.01, BOB_criterion = 8.0, WOW_criterion = 7.0):
		print("Multiple t-test begins, alpha_tt = {}, alpha_ut = {}".format(alpha_tt, alpha_ut))
		def Multiple_t_test(row, other_rows, unique_Step, label):
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    count = len(other_rows.index.unique())
		    other_rows = other_rows.drop(row.name)
		    ref = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    for index, instance in other_rows.iterrows():
		        
		        target = filtered.loc[filtered['TO'] == instance.name, 'VALUE']
		        t_statistic, p_value = stats.ttest_ind(ref, target)
		        #Bonferonni
		        #if p_value < self.user_defined_alpha_tt/count:
		        if p_value < self.user_defined_alpha_tt:
		            if self.eqp_stat_MTTest.loc[self.eqp_stat_MTTest['TO'] == row.name, 'mean'] > self.eqp_stat_MTTest.loc[self.eqp_stat_MTTest['TO'] == instance.name, ['VALUE', 'mean']]:
		                BOB.append(self.eqp_stat_MTTest['t_test_result'][row.name])
		                WOW.append(self.eqp_stat_MTTest['t_test_result'][instance.name])
		            else:
		                BOB.append(self.eqp_stat_MTTest['t_test_result'][instance.name])
		                WOW.append(self.eqp_stat_MTTest['t_test_result'][row.name])

		def Multiple_u_test(row, other_rows, unique_Step, label):
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		    count = len(other_rows.index.unique())
		    other_rows = other_rows.drop(row.name)
		    ref = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    for index, instance in other_rows.iterrows():
		        target = filtered.loc[filtered['TO'] == instance.name, 'VALUE']
		        u_statistic, p_value = stats.mannwhitneyu(ref, target)
		        #if p_value < self.user_defined_alpha_ut/count:
		        if p_value < self.user_defined_alpha_ut:
		            if self.eqp_stat_MTTest.loc[row.name]['mean'] > self.eqp_stat_MTTest.loc[instance.name]['mean']:
		                BOB.append(row.name)
		                WOW.append(instance.name)
		            else:
		                BOB.append(instance.name)
		                WOW.append(row.name)



		#Multiple t-test
		self.user_defined_alpha_tt = alpha_tt
		self.user_defined_alpha_ut = alpha_ut
		self.user_defined_tt_BOB_criterion = BOB_criterion
		self.user_defined_tt_WOW_criterion = WOW_criterion
		self.eqp_stat_MTTest = self.eqp_stat.copy()




		self.eqp_stat_MTTest['t_test_result'] = 'DUMMY'

		unique_Steps = self.lot_data['STEP_SEQ'].unique()
		#print (unique_Steps)
		#a_count = 0
		k_count = 0
		#count = 0
		count_z=0
		for unique_Step in unique_Steps:
		    BOB = []
		    WOW = []
		    #count+=1
		    #self.lot_data를 특정 STEP으로 filtering
		    filtered = self.lot_data[self.lot_data['STEP_SEQ'] == unique_Step]
		#    print(filtered)
		    #해당 step의 self.eqp_stat, filtered['TO'].unique()가 필요, 어떤 eqp가 있는지가 필요하므로
		    self.step_eqp_stat2 = self.eqp_stat_MTTest.loc[filtered['TO'].unique()]
		    
		    #pass Normality test
		    if all(self.step_eqp_stat2['normality_p_value'] > self.user_defined_alpha_normality):
		        #a_count +=1
		        #ANOVA result: 유의미한 차이 없음
		        if (self.step_eqp_stat2['anova_p_value'] > self.user_defined_alpha_ANOVA).any():
		            #self.eqp_stat.loc[self.step_eqp_stat.index]['result'] = 'DUMMY' #왜 안되냐?
		            self.eqp_stat_MTTest['t_test_result'][self.step_eqp_stat2.index] = 'DUMMY'
		            #print(self.eqp_stat.loc[self.step_eqp_stat.index]['result'])
		            
		        else:
		            #Multiple t-test 수행
		            #Linear contrast와 마찬가지로 상위 20% 하위 20% 설비에 대해서만(환경변수) 타 설비와 t-test를 진행 
		            VALUE = self.eqp_perf.loc[filtered['TO'].unique()]['VALUE', 'mean']
		            for index, row in self.eqp_perf.loc[filtered['TO'].unique()].iterrows():
		                
		                if row['VALUE', 'mean'] > self.user_defined_tt_BOB_criterion:
		                    label = 'BOB'
		                    Multiple_t_test(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step, label)
		                    
		                elif row['VALUE', 'mean'] <self.user_defined_tt_WOW_criterion:
		                    label = 'WOW'
		                    Multiple_t_test(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step, label)
		    else:
		        #k_count +=1
		        if (self.step_eqp_stat2['kruskal_p_value'] > self.user_defined_alpha_KRUSKAL).any():
		            self.eqp_stat_MTTest['t_test_result'][self.step_eqp_stat2.index] = 'DUMMY'
		        else:
		            #nonparametric method: Mann-Whitney U-test

		            VALUE = self.eqp_perf.loc[filtered['TO'].unique()]['VALUE', 'mean']
		            for index, row in self.eqp_perf.loc[filtered['TO'].unique()].iterrows():
		                if float(row['VALUE', 'mean']) > self.user_defined_tt_BOB_criterion:
		                    label = 'BOB'
		                    Multiple_u_test(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step, label)
		                    
		                elif float(row['VALUE', 'mean']) <self.user_defined_tt_WOW_criterion:
		                    label = 'WOW'
		                    Multiple_u_test(row, self.eqp_perf.loc[filtered['TO'].unique()], unique_Step, label)
		    #l3 = [x for x in l1 if x not in l2]
		    BOB = list(set([eqp for eqp in BOB if eqp not in WOW]))
		    BOB = [eqp for eqp in BOB if float(self.eqp_stat_MTTest.loc[eqp]['mean']) > self.user_defined_tt_BOB_criterion]
		    WOW = list(set([eqp for eqp in WOW if eqp not in BOB]))
		    WOW = [eqp for eqp in WOW if float(self.eqp_stat_MTTest.loc[eqp]['mean']) < self.user_defined_tt_WOW_criterion]
		    self.eqp_stat_MTTest['t_test_result'][BOB] = 'BOB'
		    self.eqp_stat_MTTest['t_test_result'][WOW] = 'WOW'
		#self.eqp_stat_MTTest.loc[self.eqp_stat_MTTest['t_test_result'] == 'WOW']
		self.eqp_stat_MTTest.to_sql("eqp_stat_MTTest", self.con, if_exists="replace")
		#self.eqp_stat_MTTest.to_csv('../result/eqp_stat_MTTest.csv', sep=',')
		print("Multiple t-test completed")

	def create_user_defined_analysis(self, BOB_avg = 8.0, WOW_avg = 7.0, BOB_prop = 0.20, WOW_prop = 0.20, eqp_weight = 0.5, step_weight = 0.5, mode = 'and'):
		print("User_defined test begins, BOB_avg = {}, WOW_avg = {}, BOB_prop = {}, WOW_prop = {}, eqp_weight = {}, step_weight = {}, mode = {}".format(BOB_avg, WOW_avg, BOB_prop, WOW_prop, eqp_weight, step_weight, mode))
		self.eqp_perf_user_defined = self.eqp_perf.copy()

		self.user_defined_BOB_avg = BOB_avg
		self.user_defined_WOW_avg = WOW_avg

		self.user_defined_BOB_Prop = BOB_prop
		self.user_defined_WOW_Prop = WOW_prop

		self.user_defined_eqp_weight = eqp_weight
		self.user_defined_step_weight = step_weight

		self.eqp_perf_user_defined['VALUE', 'mean'] = pd.to_numeric(self.eqp_perf_user_defined['VALUE', 'mean'])
		
		self.eqp_perf_user_defined['BOB', 'mean'] = pd.to_numeric(self.eqp_perf_user_defined['BOB', 'mean'])

		self.eqp_perf_user_defined['BOB/step','mean'] = pd.to_numeric(self.eqp_perf_user_defined['BOB/step','mean'])

		self.eqp_perf_user_defined['WOW', 'mean'] = pd.to_numeric(self.eqp_perf_user_defined['WOW', 'mean'])

		self.eqp_perf_user_defined['WOW/step','mean'] = pd.to_numeric(self.eqp_perf_user_defined['WOW/step','mean'])

		self.eqp_perf_user_defined['AVG_Test'] = np.where(self.eqp_perf_user_defined['VALUE', 'mean']  > self.user_defined_BOB_avg, 'BOB', np.where(self.eqp_perf_user_defined['VALUE', 'mean'] < self.user_defined_WOW_avg, 'WOW', 'DUMMY'))
		self.eqp_perf_user_defined['Prop_Test'] = np.where(self.user_defined_eqp_weight*self.eqp_perf_user_defined['BOB', 'mean'] + self.user_defined_step_weight*self.eqp_perf_user_defined['BOB/step','mean'] > self.user_defined_BOB_Prop, np.where(self.user_defined_eqp_weight*self.eqp_perf_user_defined['WOW', 'mean'] + self.user_defined_step_weight*self.eqp_perf_user_defined['WOW/step', 'mean'] > self.user_defined_WOW_Prop, 'DUMMY', 'BOB'), np.where(self.user_defined_eqp_weight*self.eqp_perf_user_defined['WOW', 'mean'] + self.user_defined_step_weight*self.eqp_perf_user_defined['WOW/step', 'mean'] > self.user_defined_WOW_Prop, 'WOW', 'DUMMY'))

		self.user_defined_mode = mode

		def and_assign(eqp):
		    x = self.eqp_perf_user_defined.loc[eqp]['AVG_Test']
		    y = self.eqp_perf_user_defined.loc[eqp]['Prop_Test']
		    x = x.values
		    y = y.values
		    if x==y:
		        return x[0]
		    else:
		        return 'DUMMY'

		def or_assign(eqp):
		    x = self.eqp_perf_user_defined.loc[eqp]['AVG_Test']
		    y = self.eqp_perf_user_defined.loc[eqp]['Prop_Test']
		    x = x.values
		    y = y.values
		    x = x[0]
		    y = y[0]
		    if x==y:
		        return x
		    else:
		        if x != 'DUMMY':
		            return x
		        elif y != 'DUMMY':
		            return y
		        else:
		            return 'DUMMY'
		        

		if self.user_defined_mode == 'and':
		    self.eqp_perf_user_defined['UDresult'] = self.eqp_perf_user_defined.index.to_series().apply(and_assign)
		elif self.user_defined_mode == 'or':
		    self.eqp_perf_user_defined['UDresult'] = self.eqp_perf_user_defined.index.to_series().apply(or_assign)
		
		self.eqp_perf_user_defined.to_sql("eqp_perf_user_defined", self.con, if_exists="replace")
		self.eqp_perf_user_defined.to_csv('../result/eqp_perf_user_defined.csv', sep=',')
		print("User_defined test completed")

	def create_combined_results(self):
		#linear contrast 방법과 multiple t-test 방법을 비교하기 위한 table
		self.eqp_stat_comparison = pd.merge(self.eqp_stat_LC, self.eqp_stat_MTTest, left_index=True, right_index=True)
		self.eqp_stat_comparison = pd.merge(self.eqp_stat_comparison, self.eqp_perf_user_defined, left_index = True, right_index = True)
		self.eqp_stat_comparison = self.eqp_stat_comparison[['count_x', 'mean_x', 'LCresult', 't_test_result']]
		#self.eqp_stat_comparison.loc[self.eqp_stat_LC['LCresult'] != self.eqp_stat_MTTest['t_test_result']][['LCresult','t_test_result']]
		#linear contrast를 통한 결과와 t-test를 통한 결과가 다른 설비들
		self.eqp_stat_comparison.to_csv('../result/eqp_stat_comparison.csv', sep=',')

	def create_dummy_log(self):
		dummy_log = self.lot_data.copy()
		self.eqp_stat_LC['TO'] = self.eqp_stat_LC.index
		self.eqp_perf_user_defined['TO'] = self.eqp_perf_user_defined.index
		self.eqp_perf_user_defined.columns = self.eqp_perf_user_defined.columns.get_level_values(0)

		#self.eqp_stat_LC
		dummy_log = dummy_log.merge(self.eqp_stat_LC,on='TO',how='left')
		dummy_log = dummy_log.merge(self.eqp_perf_user_defined,on='TO',how='left')
		#dummy_log
		#dummy_log[['CASE_ID', 'STEP_SEQ', 'TO', 'VALUE_x', 'LCresult', 'AVG_Test', 'Prop_Test']]

		dummy_log['TO'] = np.where(dummy_log['LCresult'] == 'DUMMY', dummy_log['STEP_SEQ']+'_'+'DUMMY', np.where(dummy_log['AVG_Test'] == 'DUMMY', dummy_log['STEP_SEQ']+'_'+'DUMMY', dummy_log['TO']))

		dummy_log_f = dummy_log[['CASE_ID', 'STEP_SEQ', 'TO']]
		dummy_log_f.to_csv('../result/dummylog.csv', sep=',', index = False)

	def create_eqp_info(self):
		print("create eqp_info")
		try:	
			self.eqp_info = pd.concat([self.eqp_perf, self.eqp_stat_LC], axis=1)
			del self.eqp_info['mean']
			del self.eqp_info['count']

		except AttributeError:
			self.eqp_info = self.eqp_perf.copy()

		try:
			self.eqp_info['UDresult'] = self.eqp_perf_user_defined['UDresult']
		except AttributeError:
			pass
		
		#del self.eqp_info['TO']
		
		#self.eqp_info['t_test_result'] = self.eqp_stat_MTTest['t_test_result']
		self.eqp_info.to_sql("eqp_info", self.con, if_exists="replace")
		self.eqp_info.to_csv('../result/eqp_info.csv', sep=',')

	def create_eqp_comparison(self):
		#print(self.eqp_info.columns)
		self.eqp_comparison = self.eqp_info.loc[(self.eqp_info['LCresult'] != 'DUMMY') & (self.eqp_info['UDresult'] != 'DUMMY') & (self.eqp_info['t_test_result'] != 'DUMMY') & ((self.eqp_info['BOB', 'mean'] > self.eqp_info['WOW', 'mean']*3) | (self.eqp_info['WOW', 'mean'] > self.eqp_info['BOB', 'mean']*3)) & ((self.eqp_info['VALUE', 'mean'] > self.BOB_mean_criterion) | (self.eqp_info['VALUE', 'mean'] < self.WOW_mean_criterion)) & (self.eqp_info['VALUE', 'std'] < 2)]
		self.eqp_comparison.to_csv('../result/eqp_comparison.csv', sep=',')
                        
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

	preprocessing.diff_eqp_flow(preprocessing.data)

	preprocessed_data = preprocessing.data
	print("export preprocessed_data")
	preprocessed_data.to_sql("preprocessed_data", preprocessing.con, if_exists="replace", index = False)
	preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)


	classifier = LOT_Classifier(preprocessed_data)

	classifier.create_raw_lot_data()
	classifier.create_lot_data(horizon=2)
	classifier.lot_data.to_sql("lot_data", preprocessing.con, if_exists="replace", index = False)
	classifier.lot_data.to_csv('../result/lot_data.csv', sep=',', index = False)

	classifier.relative_ratio_std_criterion()
	classifier.relative_ratio_mean_criterion()
	classifier.create_lot_BOB_WOW_group()
	classifier.lot_BOB_WOW_Group.to_sql("lot_BOB_WOW_Group", preprocessing.con, if_exists="replace", index = False)
	classifier.lot_BOB_WOW_Group.to_csv('../result/lot_BOB_WOW_group.csv', sep=',', index = False)

	classifier.create_eqp_perf()
	classifier.eqp_perf.to_sql("eqp_perf", preprocessing.con, if_exists="replace")
	classifier.eqp_perf.to_csv('../result/eqp_perf.csv', sep=',')

	print("Analysis begins")
	analyzer = LOT_Analysis(preprocessing.con)

	# 8. Kolmogorov-Smirnov one sample Test 수행
	
	analyzer.create_KS_test(alpha_normality=0.05)
	

	# 9. ANOVA (Normality) 수행 
	
	analyzer.create_ANOVA(alpha_ANOVA = 0.05)
	

	# 10. Kruskal-Wallis H-Test (Non-normality) 수행
	
	analyzer.create_Kruskal(alpha_KRUSKAL=0.05)
	

	# 11. Linear Contrast 수행
	
	analyzer.create_stat_analysis(alpha_LC = 0.05, alpha_NLC = 0.05)
	

	# 12. Multiple t-test 수행
	
	#analyzer.create_mt_stat_test(alpha_tt = 0.01, alpha_ut = 0.01)
	

	# 13. 사용자 지정 기준 분석 수행 
	
	analyzer.create_user_defined_analysis(BOB_avg = 8.0, WOW_avg = 8.0, BOB_prop = 0.20, WOW_prop = 0.20, eqp_weight = 0.5, step_weight = 0.5, mode = 'and')
	

	#analyzer.create_combined_results()
	
	analyzer.create_eqp_info()
	
	#analyzer.create_eqp_comparison()