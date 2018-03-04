from diagrams import Graph
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os, sys, inspect
import sqlite3
cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class Model(object):
    def __init__(self, analysis, representation = 'sequence', type = 'prefix' ):
        self.makeDir()
        self.con = sqlite3.connect(self.TARGET_FILE_FULL_PATH)
        #self.create_prod_info_all_dummy(representation = 'sequence', type = 'prefix')
        #self.create_prod_info_from_dummy(representation = 'sequence', type = 'prefix')
        #self.create_prod_info_to_dummy(representation = 'sequence', type = 'prefix')
        #self.create_transitions_and_states()
        if(analysis == 'Wafer_based_analysis'):
            self.machine = 'chamber'
            self.prod = 'wafer'
        elif(analysis == 'LOT_based_analysis'):
            self.machine = 'eqp'
            self.prod = 'lot'

    def makeDir(self):
        self.BASE_DIR   =  os.path.abspath('.')
        self.TARGET_DIR =  os.path.join(self.BASE_DIR, "DB")
        with open("../result/db_name.txt", 'r') as f:
            for line in (x.strip() for x in f):
                db_name =line
        self.TARGET_FILE = '{}.db'.format('DB_' + str(db_name))
        self.TARGET_FILE_FULL_PATH = os.path.join(self.TARGET_DIR, self.TARGET_FILE)
        if not os.path.isdir( self.TARGET_DIR ):
            os.makedirs( self.TARGET_DIR )


    def create_prod_info_from_dummy(self, representation = 'sequence', type = 'prefix'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)

        def dummy(x):
            return x[:4] + '_DM'

        def checkEqual1(iterator):
            iterator = iter(iterator)
            try:
                first = next(iterator)
            except StopIteration:
                return True
            return all(first == rest for rest in iterator)

        unique_to = list(set(self.prod_info['TO']))
        for to in unique_to:
            froms = list(set(self.prod_info.loc[self.prod_info['TO'] == to, 'FROM']))
            froms_attr = self.prod_group.loc[self.prod_group['TO'].isin(froms), 'LCresult']

            if 'START' not in froms:
                if checkEqual1(froms_attr):
                    self.prod_info.loc[self.prod_info['TO'] == to, 'TO'] = self.prod_info.loc[self.prod_info['TO'] == to, 'TO'].apply(dummy)

        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')

    def create_prod_info_to_dummy(self, representation = 'sequence', type = 'prefix'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)

        def dummy(x):
            return x[:4] + '_DM'

        def checkEqual1(iterator):
            iterator = iter(iterator)
            try:
                first = next(iterator)
            except StopIteration:
                return True
            return all(first == rest for rest in iterator)

        unique_from = list(set(self.prod_info['FROM']))
        for _from in unique_from:
            tos = list(set(self.prod_info.loc[self.prod_info['FROM'] == _from, 'TO']))
            tos_attr = self.prod_group.loc[self.prod_group['TO'].isin(tos), 'LCresult']

            if 'START' not in tos:
                if checkEqual1(tos_attr):
                    self.prod_info.loc[self.prod_info['FROM'] == _from, 'FROM'] = self.prod_info.loc[self.prod_info['FROM'] == _from, 'FROM'].apply(dummy)

        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')

    
    def create_prod_info_all_dummy(self, representation = 'sequence', type = 'prefix'):
        self.prod_BOB_WOW_Group = pd.read_sql_query("select * from {}_BOB_WOW_Group;".format(self.prod), self.con)

        self.prod_info = self.prod_BOB_WOW_Group.copy()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.machine), self.con)

        def dummy(x):
            return x[:4] + '_DM'

        self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'TO'] = self.prod_info.loc[self.prod_info['TO'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'TO'].apply(dummy)

        self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']),'FROM'] = self.prod_info.loc[self.prod_info['FROM'].isin(self.prod_group.loc[self.prod_group['LCresult'] == 'DUMMY','TO']), 'FROM'].apply(dummy)

        self.prod_info.to_sql("prod_info", self.con, if_exists="replace")
        self.prod_info.to_csv('../result/prod_info.csv', sep = ',')

    def create_transitions_and_states(self):
        self.prod_trans = self.prod_info.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])

        #10개 미만인 edge 삭제
        #self.prod_trans.drop(self.prod_trans.loc[self.prod_trans['BIN_VALUE', 'count_nonzero'] < 50].index, inplace=True)

        self.transitions = []
        states = []
        for row in self.prod_trans.itertuples():
            trans_attr = 'B/W'
            if row._4 > 0 and row._7 == 0:
                trans_attr = 'BOB'
            if row._7 > 0 and row._4 == 0:
                trans_attr = 'WOW'
            d = {
                'attr': trans_attr,
                'trigger': row._1.astype(str),
                'source': row.Index[0],
                'dest': row.Index[1]
            }
            self.transitions.append(d)
            states.append(row.Index[0])
            states
            states.append(row.Index[1])
        print(self.transitions)

        self.prod_group.reset_index(level=0, inplace=True)
        self.high_subset = self.prod_group.loc[self.prod_group['LCresult'] == 'BOB', 'TO']
        self.high_subset = list(set(self.high_subset))

        self.low_subset = self.prod_group.loc[self.prod_group['LCresult'] == 'WOW', 'TO']
        self.low_subset = list(set(self.low_subset))

        BOB_subset = self.prod_info.loc[self.prod_info['BOB'] == True, 'TO']
        BOB_subset = list(set(BOB_subset))
        #print(BOB_subset)
        WOW_subset = self.prod_info.loc[self.prod_info['WOW'] == True, 'TO']
        WOW_subset = list(set(WOW_subset))
        #print(WOW_subset)

        states = Series(list((set(states))))
        print(len(states))
        states_group = pd.DataFrame()
        states_group['states'] = states
        #print(states_group)
        states_group['{}'.format(self.machine)] = '0'
        states_group['{}'.format(self.machine)][states_group['states'].isin(self.high_subset)] = 'HIGH'
        states_group['{}'.format(self.machine)][states_group['states'].isin(self.low_subset)] = 'LOW'
        states_group['{}'.format(self.prod)] = '0'
        states_group['{}'.format(self.prod)][(states_group['states'].isin(BOB_subset)) & (-states_group['states'].isin(WOW_subset))] = 'BOB'
        #print(states_group['prod'][(states_group['states'].isin(BOB_subset)) & (-states_group['states'].isin(WOW_subset))])
        states_group['{}'.format(self.prod)][(states_group['states'].isin(WOW_subset)) & (-states_group['states'].isin(BOB_subset))] = 'WOW'
        #print(states_group['prod'][(states_group['states'].isin(WOW_subset)) & (-states_group['states'].isin(BOB_subset))])
        states_group['{}'.format(self.prod)][(states_group['states'].isin(BOB_subset)) & (states_group['states'].isin(WOW_subset))] = 'B/W'
        #print(states_group['prod'][(states_group['states'].isin(BOB_subset)) & (states_group['states'].isin(WOW_subset))])

        self.states = [tuple(x) for x in states_group[['states', '{}'.format(self.machine), '{}'.format(self.prod)]].values]
        self.prod_trans.to_csv('../result/prod_trans.csv', sep = ',')

class Matter(object):
        pass
"""class Matter(object):
    pass

machine_perf = pd.read_csv('../result/machine_perf.csv')

machine_perf=machine_perf.rename(columns = {'Unnamed: 0':'TO'})
machine_perf.drop(machine_perf.index[:2], inplace=True)
machine_perf = machine_perf.reset_index(drop=True)
machines = machine_perf['TO'].tolist()
machines.append('START')

matter = Matter()
machine = Machine(model=model, 
                       states=states, 
                       transitions=transitions)
model.get_graph().draw('state2.png',prog='dot')"""

if __name__ == '__main__':
    
    model = Model(analysis = 'Wafer_based_analysis', representation = 'sequence', type = 'prefix')
    model.create_prod_info_all_dummy()
    #self.create_prod_info_from_dummy(representation = 'sequence', type = 'prefix')
    #self.create_prod_info_to_dummy(representation = 'sequence', type = 'prefix')
    model.create_transitions_and_states()
    #matter = Matter()
    machine = Graph(states=model.states, transitions=model.transitions)
    machine.get_graph().draw('../result/state.png', prog='dot')