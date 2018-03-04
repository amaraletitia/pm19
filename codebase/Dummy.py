from Classifier import Classifier
import pandas as pd
from pandas import DataFrame, Series
import numpy as np
from scipy import stats
import math
from Preprocessing import Preprocessing

class Analysis(object):
	def __init__(self, con):
		with open("../result/criterion.txt", 'r') as f:
			self.BOB_mean_criterion = float(f.readline())
			self.WOW_mean_criterion = float(f.readline())
		self.con = con
		self.wafer_data = pd.read_sql_query("select * from wafer_data;", self.con)
		#self.wafer_data = pd.read_csv('../result/wafer_data.csv')
		self.wafer_BOB_WOW_Group = pd.read_sql_query("select * from wafer_BOB_WOW_Group;", self.con)
		#self.wafer_BOB_WOW_Group = pd.read_csv('../result/wafer_BOB_WOW_group.csv')
		self.chamber_perf = pd.read_sql_query("select * from chamber_perf;", self.con)
		#self.chamber_perf = pd.read_csv('../result/chamber_perf.csv')
		self.chamber_perf.set_index('TO', inplace = True)
		columns = [('VALUE', 'count_nonzero'), ('VALUE', 'mean'), ('VALUE', 'std'), ('BOB', 'count_nonzero'), ('BOB', 'mean'), ('BOB', 'std'), ('WOW', 'count_nonzero'), ('WOW', 'mean'), ('WOW', 'std'), ('BOB_stat', 'mean'), ('BOB_stat', 'std'), ('WOW_stat', 'mean'), ('WOW_stat', 'std'), ('BOB/step', 'mean'), ('WOW/step', 'mean')]
		self.chamber_perf.columns = pd.MultiIndex.from_tuples(columns)
		self.chamber_perf = self.chamber_perf.apply(pd.to_numeric)
		self.chamber_stat = pd.concat([self.chamber_perf['VALUE', 'count_nonzero'], self.chamber_perf['VALUE', 'mean']], axis=1, keys=['count', 'mean'])
		print("init: {}".format(len(self.chamber_stat)))
	def create_KS_test(self, alpha_normality=0.05):
		print("KS_test begins, alpha = {}".format(alpha_normality))
		self.user_defined_alpha_normality = alpha_normality

		def eval_normality(unique_Chamber):
		    chamber = self.wafer_data[self.wafer_data['TO'] == unique_Chamber]
		    if len(chamber['VALUE']) > 3:
		        d, p_value = stats.shapiro(chamber['VALUE'])
		    else:
		        p_value = 0.0
		    return p_value

		self.chamber_stat.loc[:,'normality_p_value'] = self.chamber_stat.index.to_series().apply(eval_normality)
		self.chamber_stat.loc[:,'Normality'] = self.chamber_stat['normality_p_value'] > self.user_defined_alpha_normality
		print("KS_test completed: {}".format(len(self.chamber_stat)))

	def create_ANOVA(self, alpha_ANOVA = 0.05, alpha_KRUSKAL=0.05):
		print("STEP_TEST begins, alpha = {}".format(alpha_ANOVA))
		#step별 정리
		unique_Steps = self.wafer_data['STEP_SEQ'].unique()
		self.user_defined_alpha_ANOVA = alpha_ANOVA
		self.user_defined_alpha_KRUSKAL = alpha_KRUSKAL

		normal_chambers = self.chamber_stat[self.chamber_stat.loc[:,'Normality'] == True].index.unique()
		print(normal_chambers)

		for unique_Step in unique_Steps:
			#self.wafer_data를 특정 STEP으로 filtering
			count_chamber = len(set(self.wafer_data.loc[self.wafer_data['STEP_SEQ'] == unique_Step, 'TO']))
			#print("STEP {} has chamber: {}".format(unique_Step, count_chamber))
			if count_chamber < 2:
				print("Doesn't require STEP_test")
				continue
			filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]

			unique_chambers = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]['TO'].unique()

			if all(x in normal_chambers for x in unique_chambers):
				ANOVA = True
			else:
				ANOVA = False

			#step 내 설비들의 VALUE를 저장
			step_chamber_values = {}
			for unique_chamber in unique_chambers:
				#filtered['TO']가 필요, 모든 observation이 필요하므로
				step_chamber_values[unique_chamber]=(filtered.loc[filtered['TO']==unique_chamber, 'VALUE'])

			if ANOVA == False:
				statistic, p_value = stats.kruskal(*step_chamber_values.values())
				self.chamber_stat.loc[unique_chambers, 'kruskal_p_value'] = p_value
				self.chamber_stat.loc[:,'KRUSKAL'] = self.chamber_stat['kruskal_p_value'] > self.user_defined_alpha_KRUSKAL
			else:
				statistic, p_value = stats.f_oneway(*step_chamber_values.values())
				self.chamber_stat.loc[unique_chambers, 'anova_p_value'] = p_value
				self.chamber_stat.loc[:,'STEP_TEST'] = self.chamber_stat['anova_p_value'] > self.user_defined_alpha_ANOVA
		print("STEP_TEST completed: {}".format(len(self.chamber_stat)))
		self.chamber_stat.to_csv('../result/chamber_stat.csv', sep=',')


	def create_Kruskal(self, alpha_KRUSKAL=0.05):
		print("KRUSKAL begins, alpha = {}".format(alpha_KRUSKAL))
		self.user_defined_alpha_KRUSKAL = alpha_KRUSKAL
		#step별 정리
		unique_Steps = self.wafer_data['STEP_SEQ'].unique()
		for unique_Step in unique_Steps:
		    #self.wafer_data를 특정 STEP으로 filtering
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    
		    unique_chambers = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]['TO'].unique()

		    #step 내 설비들의 VALUE를 저장
		    step_chamber_values = {}
		    for unique_chamber in unique_chambers:
		        #filtered['TO']가 필요, 모든 observation이 필요하므로 
		        step_chamber_values[unique_chamber]=(filtered.loc[filtered['TO']==unique_chamber, 'VALUE'])

		    statistic, p_value = stats.kruskal(*step_chamber_values.values())


		    self.chamber_stat.loc[unique_chambers, 'kruskal_p_value'] = p_value
		self.chamber_stat.loc[:,'KRUSKAL'] = self.chamber_stat['kruskal_p_value'] < self.user_defined_alpha_KRUSKAL
		print("KRUSKAL completed: {}".format(len(self.chamber_stat)))
		#self.chamber_stat.to_csv('../result/chamber_stat.csv', sep=',')
	
	

	def create_stat_analysis(self, alpha_LC = 0.05, alpha_NLC = 0.05):
		print("Linear_Contrasts begins, alpha_LC = {}, alpha_NLC = {}".format(alpha_LC, alpha_NLC))
		def Linear_Contrast(row, other_rows, unique_Step):
		    #N is total observations
		    N = sum(other_rows['VALUE', 'count_nonzero'])
		    
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
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
		    
		    t_contrast = L/std
		    
		    p_value = stats.t.sf(t_contrast, DFwithin)
		    return p_value

		def Nonparametric_Linear_Contrast(row, other_rows, unique_Step):
		    #N is total observations
		    other_rows = other_rows.drop(row.name)
		    
		    
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    other_rows_filtered_VALUE = filtered.loc[filtered['TO'].isin(other_rows.index), 'VALUE']
		    row_filtered_VALUE = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    statistic, p_value = stats.mannwhitneyu(other_rows_filtered_VALUE, row_filtered_VALUE)
		    return p_value




				#통계분석
		#기본적으로 DUMMY화 시켜놓고, BOB/WOW 설비만 재설정

		self.chamber_stat_LC = self.chamber_stat.copy()
		self.user_defined_alpha_LC = alpha_LC
		self.user_defined_alpha_NLC = alpha_NLC

		self.chamber_stat_LC.loc[:,'LC_p_value'] = 1.0
		self.chamber_stat_LC.loc[:, 'LCresult'] = 'DUMMY'

		unique_Steps = self.wafer_data['STEP_SEQ'].unique()
		#count_k=0
		#count_a=0
		#count = 0
		for unique_Step in unique_Steps:
		    #count +=1
		    #self.wafer_data를 특정 STEP으로 filtering
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    #해당 step의 self.chamber_stat, filtered['TO'].unique()가 필요, 어떤 chamber가 있는지가 필요하므로
		    step_chamber_stat = self.chamber_stat_LC.loc[filtered['TO'].unique()]
		    
		    #pass Normality test
		    if all(step_chamber_stat['normality_p_value'] > self.user_defined_alpha_normality):
		        #count_a+=1
		        #ANOVA result: 유의미한 차이 없음
		        if (step_chamber_stat['anova_p_value'] > self.user_defined_alpha_ANOVA).any():
		            self.chamber_stat_LC.loc[step_chamber_stat.index, 'LCresult'] = 'DUMMY'
		        else:
		            #Linear Contrast 수행
		            sorted_chamber_perf = self.chamber_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')],ascending=False)
		            len_sorted_chamber_perf = len(sorted_chamber_perf)
		            for index, row in sorted_chamber_perf.iterrows():
		                p_value = Linear_Contrast(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.chamber_stat_LC.loc[row.name, 'LC_p_value']  = p_value
		                #Linear Contrast 결과 유의미한 경우
		                if p_value < self.user_defined_alpha_LC:
		                    self.chamber_stat_LC.loc[row.name, 'LCresult'] = 'BOB'
		                else:
		                    break
		            sorted_chamber_perf = self.chamber_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')])            
		            for index, row in sorted_chamber_perf.iterrows():
		                p_value = Linear_Contrast(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.chamber_stat_LC.loc[row.name, 'LC_p_value']  = p_value
		                if p_value < self.user_defined_alpha_LC:
		                    self.chamber_stat_LC.loc[row.name, 'LCresult'] = 'WOW'
		                else:
		                    break
		                    
		    #Non-parametric method
		    else:
		        #count_k+=1
		        if (step_chamber_stat['kruskal_p_value'] > self.user_defined_alpha_KRUSKAL).any():
		            self.chamber_stat_LC.loc[step_chamber_stat.index, 'LCresult'] = 'DUMMY'
		            
		        else:
		            #non-parametric linear contrast
		            
		            #from the best
		            sorted_chamber_perf = self.chamber_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')],ascending=False)
		            len_sorted_chamber_perf = len(sorted_chamber_perf)
		            count = 0
		            for index, row in sorted_chamber_perf.iterrows():
		                count += 1    
		                if count >= len_sorted_chamber_perf/2:
		                    break
		            
		                p_value = Nonparametric_Linear_Contrast(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.chamber_stat_LC.loc[row.name, 'LC_p_value']  = p_value
		                #Linear Contrast 결과 유의미한 경우
		                if p_value < self.user_defined_alpha_NLC:
		                    self.chamber_stat_LC.loc[row.name, 'LCresult'] = 'BOB'
		                else:
		                    break
		            #from the worst
		            sorted_chamber_perf = self.chamber_perf.loc[filtered['TO'].unique()].sort_values(by=[('VALUE','mean')])            
		            #print(sorted_chamber_perf)
		            count = 0
		            for index, row in sorted_chamber_perf.iterrows():
		                count += 1
		                if count >= len_sorted_chamber_perf/2:
		            		    break;
		            		
		                p_value = Nonparametric_Linear_Contrast(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step)
		                self.chamber_stat_LC.loc[row.name, 'LC_p_value']  = p_value
		                if p_value < self.user_defined_alpha_NLC:
		                    self.chamber_stat_LC.loc[row.name, 'LCresult'] = 'WOW'
		                else:
		                    break
		self.chamber_stat_LC.to_sql("chamber_stat_LC", self.con, if_exists="replace")
		self.chamber_stat_LC.to_csv('../result/chamber_stat_LC.csv', sep=',')
		print("Linear_Contrasts completed")
                        
	

	def create_mt_stat_test(self, alpha_tt = 0.01, alpha_ut = 0.01):
		print("Multiple t-test begins, alpha_tt = {}, alpha_ut = {}".format(alpha_tt, alpha_ut))
		def Multiple_t_test(row, other_rows, unique_Step, label):
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    count = len(other_rows.index.unique())
		    other_rows = other_rows.drop(row.name)
		    ref = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    for index, instance in other_rows.iterrows():
		        
		        target = filtered.loc[filtered['TO'] == instance.name, 'VALUE']
		        t_statistic, p_value = stats.ttest_ind(ref, target)
		        #Bonferonni
		        #if p_value < self.user_defined_alpha_tt/count:
		        if p_value < self.user_defined_alpha_tt:
		            if self.chamber_stat_MTTest.loc[self.chamber_stat_MTTest['TO'] == row.name, 'mean'] > self.chamber_stat_MTTest.loc[self.chamber_stat_MTTest['TO'] == instance.name, ['VALUE', 'mean']]:
		                BOB.append(self.chamber_stat_MTTest['t_test_result'][row.name])
		                WOW.append(self.chamber_stat_MTTest['t_test_result'][instance.name])
		            else:
		                BOB.append(self.chamber_stat_MTTest['t_test_result'][instance.name])
		                WOW.append(self.chamber_stat_MTTest['t_test_result'][row.name])

		def Multiple_u_test(row, other_rows, unique_Step, label):
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    count = len(other_rows.index.unique())
		    other_rows = other_rows.drop(row.name)
		    ref = filtered.loc[filtered['TO'] == row.name, 'VALUE']
		    for index, instance in other_rows.iterrows():
		        target = filtered.loc[filtered['TO'] == instance.name, 'VALUE']
		        u_statistic, p_value = stats.mannwhitneyu(ref, target)
		        #if p_value < self.user_defined_alpha_ut/count:
		        if p_value < self.user_defined_alpha_ut:
		            if self.chamber_stat_MTTest.loc[row.name]['mean'] > self.chamber_stat_MTTest.loc[instance.name]['mean']:
		                BOB.append(row.name)
		                WOW.append(instance.name)
		            else:
		                BOB.append(instance.name)
		                WOW.append(row.name)



		#Multiple t-test
		self.user_defined_alpha_tt = alpha_tt
		self.user_defined_alpha_ut = alpha_ut
		self.user_defined_tt_BOB_criterion = self.BOB_mean_criterion
		self.user_defined_tt_WOW_criterion = self.WOW_mean_criterion
		self.chamber_stat_MTTest = self.chamber_stat.copy()




		self.chamber_stat_MTTest['t_test_result'] = 'DUMMY'

		unique_Steps = self.wafer_data['STEP_SEQ'].unique()
		#print (unique_Steps)
		#a_count = 0
		k_count = 0
		#count = 0
		count_z=0
		for unique_Step in unique_Steps:
		    BOB = []
		    WOW = []
		    #count+=1
		    #self.wafer_data를 특정 STEP으로 filtering
		    filtered = self.wafer_data[self.wafer_data['STEP_SEQ'] == unique_Step]
		    #해당 step의 self.chamber_stat, filtered['TO'].unique()가 필요, 어떤 chamber가 있는지가 필요하므로
		    step_chamber_stat2 = self.chamber_stat_MTTest.loc[filtered['TO'].unique()]
		    
		    #pass Normality test
		    if all(step_chamber_stat2['normality_p_value'] > self.user_defined_alpha_normality):
		        #a_count +=1
		        #ANOVA result: 유의미한 차이 없음
		        if (step_chamber_stat2['anova_p_value'] > self.user_defined_alpha_ANOVA).any():
		            #self.chamber_stat.loc[step_chamber_stat.index]['result'] = 'DUMMY' #왜 안되냐?
		            self.chamber_stat_MTTest['t_test_result'][step_chamber_stat2.index] = 'DUMMY'
		            
		        else:
		            #Multiple t-test 수행
		            #Linear contrast와 마찬가지로 상위 20% 하위 20% 설비에 대해서만(환경변수) 타 설비와 t-test를 진행 
		            VALUE = self.chamber_perf.loc[filtered['TO'].unique()]['VALUE', 'mean']
		            for index, row in self.chamber_perf.loc[filtered['TO'].unique()].iterrows():
		                
		                if row['VALUE', 'mean'] > self.user_defined_tt_BOB_criterion:
		                    label = 'BOB'
		                    Multiple_t_test(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step, label)
		                    
		                elif row['VALUE', 'mean'] <self.user_defined_tt_WOW_criterion:
		                    label = 'WOW'
		                    Multiple_t_test(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step, label)
		    else:
		        #k_count +=1
		        if (step_chamber_stat2['kruskal_p_value'] > self.user_defined_alpha_KRUSKAL).any():
		            self.chamber_stat_MTTest['t_test_result'][step_chamber_stat2.index] = 'DUMMY'
		        else:
		            #nonparametric method: Mann-Whitney U-test

		            VALUE = self.chamber_perf.loc[filtered['TO'].unique()]['VALUE', 'mean']
		            for index, row in self.chamber_perf.loc[filtered['TO'].unique()].iterrows():
		                if float(row['VALUE', 'mean']) > self.user_defined_tt_BOB_criterion:
		                    label = 'BOB'
		                    Multiple_u_test(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step, label)
		                    
		                elif float(row['VALUE', 'mean']) <self.user_defined_tt_WOW_criterion:
		                    label = 'WOW'
		                    Multiple_u_test(row, self.chamber_perf.loc[filtered['TO'].unique()], unique_Step, label)
		    #l3 = [x for x in l1 if x not in l2]
		    BOB = list(set([chamber for chamber in BOB if chamber not in WOW]))
		    BOB = [chamber for chamber in BOB if float(self.chamber_stat_MTTest.loc[chamber]['mean']) > self.user_defined_tt_BOB_criterion]
		    WOW = list(set([chamber for chamber in WOW if chamber not in BOB]))
		    WOW = [chamber for chamber in WOW if float(self.chamber_stat_MTTest.loc[chamber]['mean']) < self.user_defined_tt_WOW_criterion]
		    self.chamber_stat_MTTest['t_test_result'][BOB] = 'BOB'
		    self.chamber_stat_MTTest['t_test_result'][WOW] = 'WOW'
		#self.chamber_stat_MTTest.loc[self.chamber_stat_MTTest['t_test_result'] == 'WOW']
		self.chamber_stat_MTTest.to_sql("chamber_stat_MTTest", self.con, if_exists="replace")
		#self.chamber_stat_MTTest.to_csv('../result/chamber_stat_MTTest.csv', sep=',')
		print("Multiple t-test completed")

	def create_user_defined_analysis(self, BOB_avg, WOW_avg, BOB_prop, WOW_prop, chamber_weight = 0.5, step_weight = 0.5, mode = None):
		print("User_defined test begins, BOB_avg = {}, WOW_avg = {}, BOB_prop = {}, WOW_prop = {}, chamber_weight = {}, step_weight = {}, mode = {}".format(BOB_avg, WOW_avg, BOB_prop, WOW_prop, chamber_weight, step_weight, mode))
		self.chamber_perf_user_defined = self.chamber_perf.copy()

		self.user_defined_BOB_avg = BOB_avg
		self.user_defined_WOW_avg = WOW_avg

		self.user_defined_BOB_Prop = BOB_prop
		self.user_defined_WOW_Prop = WOW_prop
		self.user_defined_chamber_weight = chamber_weight
		self.user_defined_step_weight = step_weight

		self.chamber_perf_user_defined['VALUE', 'mean'] = pd.to_numeric(self.chamber_perf_user_defined['VALUE', 'mean'])
		
		self.chamber_perf_user_defined['BOB', 'mean'] = pd.to_numeric(self.chamber_perf_user_defined['BOB', 'mean'])

		self.chamber_perf_user_defined['BOB/step','mean'] = pd.to_numeric(self.chamber_perf_user_defined['BOB/step','mean'])

		self.chamber_perf_user_defined['WOW', 'mean'] = pd.to_numeric(self.chamber_perf_user_defined['WOW', 'mean'])

		self.chamber_perf_user_defined['WOW/step','mean'] = pd.to_numeric(self.chamber_perf_user_defined['WOW/step','mean'])
		
		#t-test
		if self.user_defined_BOB_avg != None and self.user_defined_WOW_avg != None:
			chamber_status = []
			self.chamber_perf_user_defined['AVG_Test'] = 'DUMMY'
			for chamber in self.chamber_perf.index:
				#print(chamber)
				chamber_values = self.wafer_data.loc[self.wafer_data['TO'] == chamber, 'VALUE']
				chamber_mean = chamber_values.mean()
				chamber_std = chamber_values.std()
				chamber_size = len(chamber_values)
				
				try:
					BOB_t = (chamber_mean - self.user_defined_BOB_avg)/(chamber_std/chamber_size)
				except ZeroDivisionError as e:
					print(e)
				BOB_avg_p_value = 1 - stats.t.cdf(x = BOB_t, df = chamber_size - 1)
				if BOB_avg_p_value < 0.05:
					self.chamber_perf_user_defined.set_value(chamber, 'AVG_Test', 'BOB')
					#print("BOB!")
				try:
					WOW_t = (chamber_mean - self.user_defined_WOW_avg)/(chamber_std/chamber_size)
				except ZeroDivisionError as e:
					print(e)
				WOW_avg_p_value = stats.t.cdf(x = WOW_t, df = chamber_size - 1)
				if WOW_avg_p_value < 0.05:
					self.chamber_perf_user_defined.set_value(chamber, 'AVG_Test', 'WOW')

		if self.user_defined_BOB_Prop != None and self.user_defined_WOW_Prop != None:
			self.chamber_perf_user_defined['Prop_Test'] = np.where(self.user_defined_chamber_weight*self.chamber_perf_user_defined['BOB', 'mean'] + self.user_defined_step_weight*self.chamber_perf_user_defined['BOB/step','mean'] > self.user_defined_BOB_Prop, np.where(self.user_defined_chamber_weight*self.chamber_perf_user_defined['WOW', 'mean'] + self.user_defined_step_weight*self.chamber_perf_user_defined['WOW/step', 'mean'] > self.user_defined_WOW_Prop, 'DUMMY', 'BOB'), np.where(self.user_defined_chamber_weight*self.chamber_perf_user_defined['WOW', 'mean'] + self.user_defined_step_weight*self.chamber_perf_user_defined['WOW/step', 'mean'] > self.user_defined_WOW_Prop, 'WOW', 'DUMMY'))
			


		self.user_defined_mode = mode

		def and_assign(chamber):
		    x = self.chamber_perf_user_defined.loc[chamber]['AVG_Test']
		    y = self.chamber_perf_user_defined.loc[chamber]['Prop_Test']
		    x = x.values
		    y = y.values
		    if x==y:
		        return x[0]
		    else:
		        return 'DUMMY'

		def or_assign(chamber):
		    x = self.chamber_perf_user_defined.loc[chamber]['AVG_Test']
		    y = self.chamber_perf_user_defined.loc[chamber]['Prop_Test']
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
		    self.chamber_perf_user_defined['UDresult'] = self.chamber_perf_user_defined.index.to_series().apply(and_assign)
		elif self.user_defined_mode == 'or':
		    self.chamber_perf_user_defined['UDresult'] = self.chamber_perf_user_defined.index.to_series().apply(or_assign)
		elif 'Prop_Test' not in self.chamber_perf_user_defined.columns:
			self.chamber_perf_user_defined['UDresult'] = self.chamber_perf_user_defined['AVG_Test']
			
		elif 'AVG_Test' not in self.chamber_perf_user_defined.columns:
			self.chamber_perf_user_defined['UDresult'] = self.chamber_perf_user_defined['Prop_Test']
			

		self.chamber_perf_user_defined.to_sql("chamber_perf_user_defined", self.con, if_exists="replace")
		self.chamber_perf_user_defined.to_csv('../result/chamber_perf_user_defined.csv', sep=',')
		
		print("User_defined test completed")

	def create_chamber_info(self):
		print("create chamber_info")
		try:	
			self.chamber_info = pd.concat([self.chamber_perf, self.chamber_stat_LC], axis=1)
			del self.chamber_info['mean']
			del self.chamber_info['count']

		except AttributeError:
			self.chamber_info = self.chamber_perf.copy()
		try:
			self.chamber_info['UDresult'] = self.chamber_perf_user_defined['UDresult']
		except AttributeError:
			pass
		
		#del self.chamber_info['TO']
		
		#self.chamber_info['t_test_result'] = self.chamber_stat_MTTest['t_test_result']
		self.chamber_info.to_sql("chamber_info", self.con, if_exists="replace")
		self.chamber_info.to_csv('../result/chamber_info.csv', sep=',')
		
	def create_chamber_comparison(self):
		print("create chamber_comparison")
		self.chamber_comparison = self.chamber_info.loc[(self.chamber_info['LCresult'] != 'DUMMY') & (self.chamber_info['UDresult'] != 'DUMMY') & (self.chamber_info['t_test_result'] != 'DUMMY') & ((self.chamber_info[('BOB', 'mean')] > self.chamber_info[('WOW', 'mean')]*3) | (self.chamber_info[('WOW', 'mean')] > self.chamber_info[('BOB', 'mean')]*3)) & ((self.chamber_info[('VALUE', 'mean')] > self.BOB_mean_criterion) | (self.chamber_info[('VALUE', 'mean')] < self.WOW_mean_criterion))]
		self.chamber_comparison.to_sql("chamber_comparison", self.con, if_exists="replace")
		#self.chamber_comparison.to_csv('../result/chamber_comparison.csv', sep=',')
                        
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


	preprocessed_data = preprocessing.data
	print("export preprocessed_data")
	preprocessed_data.to_sql("preprocessed_data", preprocessing.con, if_exists="replace", index = False)
	preprocessed_data.to_csv('../input/preprocessed_data.csv', sep=',', index = False)
	
	classifier = Classifier(preprocessed_data)
	classifier.create_raw_lot_data()
	classifier.relative_ratio_std_criterion()
	classifier.extract_deviated_lot()
	classifier.create_wafer_data(horizon=1)
	classifier.wafer_data.to_sql("wafer_data", preprocessing.con, if_exists="replace", index = False)
	classifier.wafer_data.to_csv('../result/wafer_data.csv', sep=',', index = False)


	# 7. 수율 Relative Ratio 기준ye
	#classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = 70, WOW_mean_rela_criterion = 30)

	# 7. 수율 Rank-based 기준
	classifier.rank_based_mean_criterion(BOB_n = 0, WOW_n = 1)

	# 7. 수율 Absolute value 기준
	#classifier.absoulte_value_mean_criterion(BOB_mean_abs_criterion = 8.0, WOW_mean_abs_criterion = 7.0)

	classifier.create_wafer_BOB_WOW_group()
	classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", preprocessing.con, if_exists="replace", index = False)
	classifier.wafer_BOB_WOW_Group.to_csv('../result/wafer_BOB_WOW_group.csv', sep=',', index = False)
	
	classifier.create_chamber_perf()
	classifier.chamber_perf.to_sql("chamber_perf", preprocessing.con, if_exists="replace")
	classifier.chamber_perf.to_csv('../result/chamber_perf.csv', sep=',')


	print("Analysis begins")
	analyzer = Analysis(preprocessing.con)

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
	
	analyzer.create_user_defined_analysis(BOB_avg = 8.0, WOW_avg = 8.0, BOB_prop = 0.20, WOW_prop = 0.20, chamber_weight = 0.5, step_weight = 0.5, mode = 'and')
	

	#analyzer.create_combined_results()
	
	analyzer.create_chamber_info()
	
	#analyzer.create_chamber_comparison())