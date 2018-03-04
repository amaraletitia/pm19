from diagrams import Graph
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os, sys, inspect
import sqlite3
import time
import statistics
cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class Model(object):
    def __init__(self, analysis, con, representation = 'sequence', type = 'prefix' ):
        #self.con = sqlite3.connect(self.TARGET_FILE_FULL_PATH)
        self.con = con
        self.makeDir()
        #self.analysis_con = sqlite3.connect(self.TARGET_FILE_FULL_PATH) 
        #self.create_prod_info_all_dummy(representation = 'sequence', type = 'prefix')
        #self.create_prod_info_from_dummy(representation = 'sequence', type = 'prefix')
        #self.create_prod_info_to_dummy(representation = 'sequence', type = 'prefix')
        #self.create_transitions_and_states()
        if(analysis == 'Wafer-based Analysis' or analysis == 'Wafer-based Analysis on specific Lot'):
            self.machine = 'chamber'
            self.prod = 'wafer'
        elif(analysis == 'Lot-based Analysis'):
            self.machine = 'eqp'
            self.prod = 'lot'

    def makeDir(self):
        self.BASE_DIR   =  os.path.abspath('.')
        self.TARGET_DIR =  os.path.join(self.BASE_DIR, "DB/analysis")
        """
        with open("../result/db_name.txt", 'r') as f:
            for line in (x.strip() for x in f):
                db_name =line
        """
        self.db_name = str(time.time())
        self.TARGET_FILE = '{}.db'.format('analysis_DB_' + self.db_name)
        self.TARGET_FILE_FULL_PATH = os.path.join(self.TARGET_DIR, self.TARGET_FILE)
        if not os.path.isdir( self.TARGET_DIR ):
            os.makedirs( self.TARGET_DIR )


    def create_prod_info_from_dummy(self, representation = 'sequence', type = 'prefix', mode = 'and'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)
        if "('UDresult', '')" in self.prod_group.columns:
            self.prod_group = self.prod_group.rename(columns = {"('UDresult', '')":'UDresult'})

        def dummy(x):
            return x.split("_")[0].strip() + '_DM'

        def checkEqual1(iterator):
            iterator = iter(iterator)
            try:
                first = next(iterator)
            except StopIteration:
                return True
            return all(first == rest for rest in iterator)
        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            if mode == 'or':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'DUMMY'), 'BOB', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'DUMMY'), 'WOW', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', None)))))))
            if mode == 'and':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', 'None')))


        unique_to = list(set(self.prod_info['TO']))
        for to in unique_to:
            froms = list(set(self.prod_info.loc[self.prod_info['TO'] == to, 'FROM']))
            #froms_attr = self.prod_group.loc[self.prod_group['TO'].isin(froms), 'LCresult']
            if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
                froms_attr = self.prod_group.loc[self.prod_group['TO'].isin(froms), 'Result']

            if 'LCresult' in self.prod_group.columns and 'UDresult' not in self.prod_group.columns:
                froms_attr = self.prod_group.loc[self.prod_group['TO'].isin(froms), 'LCresult']

            if 'LCresult' not in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
                froms_attr = self.prod_group.loc[self.prod_group['TO'].isin(froms), 'UDresult']                

            if 'START' not in froms:
                if checkEqual1(froms_attr):

                    self.prod_info.loc[self.prod_info['TO'] == to, 'TO'] = self.prod_info.loc[self.prod_info['TO'] == to, 'TO'].apply(dummy)
                    self.prod_info.loc[self.prod_info['FROM'] == to, 'FROM'] = self.prod_info.loc[self.prod_info['FROM'] == to, 'FROM'].apply(dummy)

        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        #self.prod_info.to_sql("prod_info", self.analysis_con, if_exists='fail')
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')
        self.prod_group.to_csv('../result/analysis_result.csv', sep = ',')

    def create_prod_info_to_dummy(self, representation = 'sequence', type = 'prefix', mode = 'and'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)
        if "('UDresult', '')" in self.prod_group.columns:
            self.prod_group = self.prod_group.rename(columns = {"('UDresult', '')":'UDresult'})

        def dummy(x):
            return x.split("_")[0].strip() + '_DM'

        def checkEqual1(iterator):
            iterator = iter(iterator)
            try:
                first = next(iterator)
            except StopIteration:
                return True
            return all(first == rest for rest in iterator)
        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            if mode == 'or':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'DUMMY'), 'BOB', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'DUMMY'), 'WOW', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', None)))))))
            if mode == 'and':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', 'None')))

        unique_from = list(set(self.prod_info['FROM']))
        for _from in unique_from:
            tos = list(set(self.prod_info.loc[self.prod_info['FROM'] == _from, 'TO']))
            if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
                tos_attr = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'Result']

            if 'LCresult' in self.prod_group.columns and 'UDresult' not in self.prod_group.columns:
                tos_attr = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'LCresult']

            if 'LCresult' not in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
                tos_attr = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'UDresult']
                #print(tos_attr)
                #tos_attr_lc = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'LCresult']
                #tos_attr_ud = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'UDresult']


            if _from != 'START':
                if checkEqual1(tos_attr):
                    self.prod_info.loc[self.prod_info['FROM'] == _from, 'FROM'] = self.prod_info.loc[self.prod_info['FROM'] == _from, 'FROM'].apply(dummy)
                    self.prod_info.loc[self.prod_info['TO'] == _from, 'TO'] = self.prod_info.loc[self.prod_info['TO'] == _from, 'TO'].apply(dummy)

        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        #self.prod_info.to_sql("prod_info", self.analysis_con, if_exists='fail')
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')
        self.prod_group.to_csv('../result/analysis_result.csv', sep = ',')

    
    def create_prod_info_all_dummy(self, representation = 'sequence', type = 'prefix', mode = 'and'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)
        if "('UDresult', '')" in self.prod_group.columns:
            self.prod_group = self.prod_group.rename(columns = {"('UDresult', '')":'UDresult'})

        def dummy(x):
            return x.split("_")[0].strip() + '_DM'

        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            if mode == 'or':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'DUMMY'), 'BOB', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'DUMMY'), 'WOW', np.where((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', None)))))))
            if mode == 'and':
                self.prod_group['Result'] = np.where((self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'DUMMY', np.where((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB'), 'BOB', np.where((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW'), 'WOW', 'None')))

        print("len: {}".format(len(self.prod_info)))
        self.prod_info = self.prod_info.loc[-(self.prod_info['TO'].apply(lambda x: x.split("_")[0].strip()) == self.prod_info['FROM'].apply(lambda x: x.split("_")[0].strip()))]
        print("len: {}".format(len(self.prod_info)))


        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['Result'] == 'DUMMY', 'TO']), 'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['Result'] == 'DUMMY', 'TO']), 'TO'].apply(dummy)

            self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['Result'] == 'DUMMY', 'TO']), 'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['Result'] == 'DUMMY', 'TO']), 'FROM'].apply(dummy)

        #self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'].apply(dummy)
        """
        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            if mode == 'or':
                #if and, dummy in case both are dummy
                self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'TO'].apply(dummy)
                self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'].apply(dummy)
            if mode == 'and':
                #if or, dummy in case either is dummy
                self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'TO'].apply(dummy)

                self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[(self.prod_group['LCresult'] == 'DUMMY') | (self.prod_group['UDresult'] == 'DUMMY'), 'TO']), 'FROM'].apply(dummy)
        """
        if 'LCresult' in self.prod_group.columns and 'UDresult' not in self.prod_group.columns:
            self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'TO'].apply(dummy)

            self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']), 'FROM'].apply(dummy)

        if 'LCresult' not in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            
            self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['UDresult'] == 'DUMMY','TO']),'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['UDresult'] == 'DUMMY','TO']),'TO'].apply(dummy)

            self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['UDresult'] == 'DUMMY','TO']),'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['UDresult'] == 'DUMMY','TO']), 'FROM'].apply(dummy)
        
        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')
        self.prod_group.to_csv('../result/analysis_result.csv', sep = ',')

    def create_transitions_and_states(self, mode = 'or'):
        if 'index' in self.prod_info.columns:
            del self.prod_info['index']

        #prod_info에 END 추가 -> prod_temp
        self.prod_info.sort_values(by = ['CASE_ID', 'TKIN_TIME'], inplace=True)
        self.prod_info = self.prod_info.reset_index(drop=True)

        self.prod_info.loc[self.prod_info['FROM'] == 'START', 'BOB'] = 0
        self.prod_info.loc[self.prod_info['FROM'] == 'START', 'WOW'] = 0
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')

        self.prod_temp = self.prod_info[['CASE_ID', 'TKIN_TIME','FROM', 'TO', 'VALUE', 'BOB', 'WOW']]

        rows = []
        cur = {}
        case_id = self.prod_temp['CASE_ID'][0]
        for row in self.prod_temp.itertuples():
            if case_id == row.CASE_ID:
                cur['CASE_ID'] = row.CASE_ID
                cur['TKIN_TIME'] = row.TKIN_TIME
                cur['FROM'] = row.TO
                cur['TO'] = 'END'
                cur['VALUE'] = row.VALUE
                cur['BOB'] = 0
                cur['WOW'] = 0
                #cur['STEP_SEQ'] = row.STEP_SEQ
            if case_id != row.CASE_ID:
                #cur['index'] = row.Index
                
                rows.append(cur)
                cur = {}
                case_id = row.CASE_ID
        new_df = pd.DataFrame(rows)
        new_df = new_df[['CASE_ID', 'TKIN_TIME','FROM', 'TO', 'VALUE', 'BOB', 'WOW']]
        self.prod_temp = pd.concat([self.prod_temp, new_df])
        self.prod_temp.sort_values(by = ['CASE_ID', 'TKIN_TIME'], inplace=True)
        self.prod_temp = self.prod_temp.reset_index(drop=True)
        self.prod_temp = self.prod_temp.dropna(how='all')

        #prod_temp에 step 추가하고 prod_trans 생성
        def extract_step(x):
            if x == 'END':
                return x
            else:
                return x.split("_")[0].strip()
        self.prod_temp['TO'].astype(str)
        self.prod_temp['STEP_SEQ'] = self.prod_temp['TO'].apply(extract_step)

        grouped = self.prod_temp.groupby(['FROM', 'TO'])

        def count(x):
            return x.count()

        prod_trans = grouped.VALUE.agg([count, np.mean, np.std])
        columns=pd.MultiIndex.from_product([['new'], ['one','two','three']])
        prod_trans.columns = [('VALUE', 'count_nonzero'), ('VALUE', 'mean'), ('VALUE', 'std')]
        prod_trans_temp = grouped.BOB.agg([np.count_nonzero, np.mean, np.std])
        prod_trans_temp.columns = [('BOB', 'count_nonzero'), ('BOB', 'mean'), ('BOB', 'std')]
        prod_trans_temp_2 = grouped.WOW.agg([np.count_nonzero, np.mean, np.std])
        prod_trans_temp_2.columns = [('WOW', 'count_nonzero'), ('WOW', 'mean'), ('WOW', 'std')]
        


        self.prod_trans = prod_trans.join([prod_trans_temp, prod_trans_temp_2], how='left')
        self.prod_trans.columns = pd.MultiIndex.from_product([['VALUE', 'BOB', 'WOW'], ['count_nonzero','mean','std']])
        print("columns: {}".format(self.prod_trans.columns))
        #self.prod_trans = self.prod_temp.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])
        #print("columns: {}".format(self.prod_trans.columns))
        
        #prod_temp 필터링 (count 1인 STEP 제외)
        tos = list(self.prod_trans.index.get_level_values(1))
        tos.append('START')
        states = list(set(tos))

        states_group = pd.DataFrame()
        states_group['states'] = states

        prod_trans_temp = self.prod_trans.copy()
        prod_trans_temp.reset_index(inplace=True)
        print("columns: {}".format(prod_trans_temp.columns))
        prod_trans_temp.columns = ['_'.join(col).strip() for col in prod_trans_temp.columns.values]
        prod_trans_temp['STEP_SEQ_'] = prod_trans_temp['TO_'].apply(extract_step)

        #step 내 설비별 wafer 빈도
        unique_steps = list(set(prod_trans_temp['STEP_SEQ_'].tolist()))

        num_wafer_chamber_step = {}
        for step in unique_steps:
            num_wafer = prod_trans_temp.loc[prod_trans_temp['STEP_SEQ_'] == step, "VALUE_count_nonzero"]
            num_wafer.sort_values(ascending = False, inplace = True)
            idx = (len(num_wafer)-1) * 50 * 0.01
            idx = int(idx + 0.5)

            num_wafer_chamber_step[step] = num_wafer.iloc[idx]
        self.num_wafer_chamber_step = num_wafer_chamber_step

        


        self.step_perf = prod_trans_temp.groupby('STEP_SEQ_')['VALUE_mean'].agg(['min', 'max'])

        step_machine_count = prod_trans_temp.groupby('STEP_SEQ_')['TO_'].nunique()
        step_machine_count.name = 'count'

        step_machine = prod_trans_temp.groupby('STEP_SEQ_').TO_.apply(list)
        step_machine.name = 'machine'

        self.step_perf = pd.concat((self.step_perf, step_machine_count), axis=1)
        self.step_perf = pd.concat((self.step_perf, step_machine), axis=1)
        self.step_perf.reset_index(inplace=True)
        self.step_perf = self.step_perf[self.step_perf['STEP_SEQ_'] != 'END']
        self.step_perf['diff'] = self.step_perf['max'] - self.step_perf['min']

        for row in self.step_perf.itertuples():
            self.step_perf.set_value(row.Index, 'machine', ', '.join(row.machine))
            #step['machine'] = ', '.join(step['machine'])

        print(self.step_perf)
        self.step_perf.to_sql("step_perf", self.con, if_exists="replace", index = False)
        """
        dummy_step = self.step_perf.loc[self.step_perf['count'] == 1, 'machine']
        #dummy_step_machine = [x for step in dummy_step for x in step]
        #print("Dummy step machine: {}".format(dummy_step_machine))
        print("previous len of prod_temp: {}".format(len(self.prod_temp)))
        self.prod_temp = self.prod_temp.loc[np.logical_not(self.prod_temp.STEP_SEQ.isin(self.step_perf.loc[self.step_perf['count'] == 1, 'STEP_SEQ_'])), : ]
        print("next len of prod_temp: {}".format(len(self.prod_temp)))
        """
        #prod_temp 재정리(FROM TO 관계 맞추기)
        """
        case_id = 'nothing'
        to = 'nothing'
        for row in self.prod_temp.itertuples():
            if case_id == row.CASE_ID:
                if to != row.FROM:
                    self.prod_temp.set_value(row.Index,'FROM', to)
                    #row['FROM'] = to
                to = row.TO
            else:
                case_id = row.CASE_ID
                if row.FROM != 'START':
                    self.prod_temp.set_value(row.Index,'FROM', 'START')
                    self.prod_temp.set_value(row.Index,'BOB', '0')
                    self.prod_temp.set_value(row.Index,'WOW', '0')
                    #row['FROM'] = 'START'
                to = row.TO
            #print(to)
        """
        self.prod_temp.to_csv('../result/prod_temp.csv', sep = ',')
        self.prod_temp.to_sql("prod_temp", self.con, if_exists="replace", index = False)

        grouped = self.prod_temp.groupby(['FROM', 'TO'])

        def count(x):
            return x.count()

        prod_trans = grouped.VALUE.agg([count, np.mean, np.std])
        prod_trans.columns = [('VALUE', 'count_nonzero'), ('VALUE', 'mean'), ('VALUE', 'std')]
        prod_trans_temp = grouped.BOB.agg([np.count_nonzero, np.mean, np.std])
        prod_trans_temp.columns = [('BOB', 'count_nonzero'), ('BOB', 'mean'), ('BOB', 'std')]
        prod_trans_temp_2 = grouped.WOW.agg([np.count_nonzero, np.mean, np.std])
        prod_trans_temp_2.columns = [('WOW', 'count_nonzero'), ('WOW', 'mean'), ('WOW', 'std')]

        self.prod_trans = prod_trans.join([prod_trans_temp, prod_trans_temp_2], how='left')

        #여기서 count_nonzero하면 안됨 (VALUE 값이 0일 경우 count 못함)
        #self.prod_trans = self.prod_temp.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])
        
        #create states and transitions
        self.transitions = []
        states = []
        print(self.prod_trans)
        for row in self.prod_trans.itertuples():
            trans_attr = 'B/W'
            if row._4 > 0 and row._7 == 0:
                trans_attr = 'BOB'
            if row._7 > 0 and row._4 == 0:
                trans_attr = 'WOW'
            source = row.Index[0]
            step = source.split("_")[0].strip()
            step_len = len(step)
            chamber = source[step_len:]
            source = step + "\n" + chamber

            dest = row.Index[1]
            step = dest.split("_")[0].strip()
            step_len = len(step)
            chamber = dest[step_len:]
            dest = step + "\n" + chamber

            d = {
                'status': 'None',
                'count': row._1,
                'BOB_count': row._4,
                'WOW_count': row._7,
                'attr': trans_attr,
                'trigger': str(row._1),
                'source': source,
                'dest': dest,
                'step': step

            }
            self.transitions.append(d)
            states.append(row.Index[0])
            states.append(row.Index[1])
        print("States are printed: {}".format(list(set(states))))
        #self.prod_group.reset_index(level=0, inplace=True)

        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:


            if mode == 'or':
                #if and, high subset in case one of them is BOB
                self.high_subset = self.prod_group.loc[((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'DUMMY') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM"))), 'TO']
                self.low_subset = self.prod_group.loc[((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'DUMMY') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'WOW') & (~self.prod_group['TO'].str.contains("DM"))), 'TO']
                print("high subset: {}".format(self.high_subset))
                print("low subset: {}".format(self.low_subset))
            if mode == 'and':
                #if or, high subset in case both of them are dummy
                self.high_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
                self.low_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
        if 'LCresult' in self.prod_group.columns and 'UDresult' not in self.prod_group.columns:
            
            self.high_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM")), 'TO']
            self.low_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
        if 'LCresult' not in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            
            self.high_subset = self.prod_group.loc[(self.prod_group['UDresult'] == 'BOB')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
            self.low_subset = self.prod_group.loc[(self.prod_group['UDresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']

        self.high_subset = list(set(self.high_subset))

        
        self.low_subset = list(set(self.low_subset))

        BOB_subset = self.prod_temp.loc[self.prod_temp['BOB'] == True, 'TO']
        BOB_subset = list(set(BOB_subset))
        WOW_subset = self.prod_temp.loc[self.prod_temp['WOW'] == True, 'TO']
        WOW_subset = list(set(WOW_subset))

        #create states_group
        states = Series(list((set(states))))
        print(len(states))
        states_group = pd.DataFrame()
        states_group['states'] = states
        states_group['{}'.format(self.machine)] = '0'
        states_group['{}'.format(self.machine)][states_group['states'].isin(self.high_subset)] = 'HIGH'
        states_group['{}'.format(self.machine)][states_group['states'].isin(self.low_subset)] = 'LOW'
        states_group['{}'.format(self.prod)] = '0'
        states_group['{}'.format(self.prod)][(states_group['states'].isin(BOB_subset)) & (-states_group['states'].isin(WOW_subset))] = 'BOB'
        states_group['{}'.format(self.prod)][(states_group['states'].isin(WOW_subset)) & (-states_group['states'].isin(BOB_subset))] = 'WOW'
        states_group['{}'.format(self.prod)][(states_group['states'].isin(BOB_subset)) & (states_group['states'].isin(WOW_subset))] = 'B/W'

        #update states (\n)
        states_modi = []
        for state in states:
            step = state.split("_")[0].strip()
            step_len = len(step)
            chamber = state[step_len:]
            state = step + "\n" + chamber
            states_modi.append(state)

        states_group['states'] = states_modi

        #create states parameter with modified states list
        self.states = [tuple(x) for x in states_group[['states', '{}'.format(self.machine), '{}'.format(self.prod)]].values]

        
        self.prod_trans.to_csv('../result/prod_trans.csv', sep = ',')
        self.prod_trans.to_sql("prod_trans", self.con, if_exists="replace")
        

class Matter(object):
        pass

if __name__ == '__main__':
    
    model = Model(analysis = 'Wafer-based Analysis', representation = 'sequence', type = 'prefix')
    model.create_prod_info_all_dummy()
    #self.create_prod_info_from_dummy(representation = 'sequence', type = 'prefix')
    #self.create_prod_info_to_dummy(representation = 'sequence', type = 'prefix')
    model.create_transitions_and_states()
    #matter = Matter()
    machine = Graph(states=model.states, transitions=model.transitions)
    machine.get_graph().draw('../result/state_svg.svg', format ='svg', prog='dot')