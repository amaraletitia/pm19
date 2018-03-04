from diagrams import GraphMachine as Machine
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import os, sys, inspect
cmd_folder = os.path.realpath(
    os.path.dirname(
        os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])))

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class Model(object):
    def __init__(self):
        self.create_wafer_info()
        self.create_transitions_and_states()
    
    def create_wafer_info(self):
        self.wafer_BOB_WOW_Group = pd.read_csv('../result/wafer_BOB_WOW_Group.csv', index_col = False)
        del self.wafer_BOB_WOW_Group['Unnamed: 0']
        self.wafer_BOB_WOW_Group.sort_values(by=['CASE_ID', 'STEP_SEQ'], inplace = True)
        self.wafer_BOB_WOW_Group.reset_index(inplace=True)
        del self.wafer_BOB_WOW_Group['index']
        
        self.wafer_info = self.wafer_BOB_WOW_Group.copy()

        count = 0
        index = 0
        case_id = self.wafer_info['CASE_ID'][0]
        f = []
        t = []
        for row in self.wafer_info.itertuples():
            #print(row.S_E_CHAMBER_ID)
            
            if case_id == row.CASE_ID:
                if count == 0:
                    f.append('START')
                    t.append(row.S_E_CHAMBER_ID)
                else:
                    f.append(self.wafer_info['S_E_CHAMBER_ID'][row.Index-1])
                    t.append(row.S_E_CHAMBER_ID)
                count+=1
            else:
                count = 0
                case_id = row.CASE_ID
                if count == 0:
                    f.append('START')
                    t.append(row.S_E_CHAMBER_ID)
                count+=1

        self.wafer_info = self.wafer_info.assign(FROM = f, TO=t)
        self.wafer_info.to_csv('../result/wafer_info.csv', sep = ',')

    def create_transitions_and_states(self):
        self.wafer_group = pd.read_csv('../result/chamber_info.csv')
        def dummy(x):
            return x[:8] + '_dummy'

        self.wafer_info_dummy = self.wafer_info.copy()

        self.wafer_info_dummy['FROM'][self.wafer_info_dummy['FROM'].isin(self.wafer_group.loc[self.wafer_group['LCresult'] == 'DUMMY','S_E_CHAMBER_ID'])] = self.wafer_info_dummy['FROM'][self.wafer_info_dummy['FROM'].isin(self.wafer_group.loc[self.wafer_group['LCresult'] == 'DUMMY','S_E_CHAMBER_ID'])].apply(dummy)

        self.wafer_info_dummy['TO'][self.wafer_info_dummy['TO'].isin(self.wafer_group.loc[self.wafer_group['LCresult'] == 'DUMMY','S_E_CHAMBER_ID'])] = self.wafer_info_dummy['TO'][self.wafer_info_dummy['TO'].isin(self.wafer_group.loc[self.wafer_group['LCresult'] == 'DUMMY','S_E_CHAMBER_ID'])].apply(dummy)


        self.wafer_trans = self.wafer_info_dummy.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])
        self.wafer_info_dummy.to_csv('../result/wafer_info_dummy.csv', sep = ',')

        #10개 미만인 edge 삭제
        #self.wafer_trans.drop(self.wafer_trans.loc[self.wafer_trans['BIN_VALUE', 'count_nonzero'] < 50].index, inplace=True)

        self.transitions = []
        states = []
        for row in self.wafer_trans.itertuples():
            d = {
                'trigger': row._1.astype(str),
                'source': row.Index[0],
                'dest': row.Index[1]
            }
            self.transitions.append(d)
            states.append(row.Index[0])
            states
            states.append(row.Index[1])

        self.wafer_group.reset_index(level=0, inplace=True)
        self.high_subset = self.wafer_group.loc[self.wafer_group['LCresult'] == 'BOB', 'S_E_CHAMBER_ID']
        self.high_subset = list(set(self.high_subset))

        self.low_subset = self.wafer_group.loc[self.wafer_group['LCresult'] == 'WOW', 'S_E_CHAMBER_ID']
        self.low_subset = list(set(self.low_subset))

        BOB_subset = self.wafer_info.loc[self.wafer_info['BOB'] == True, 'S_E_CHAMBER_ID']
        BOB_subset = list(set(BOB_subset))
        WOW_subset = self.wafer_info.loc[self.wafer_info['WOW'] == True, 'S_E_CHAMBER_ID']
        WOW_subset = list(set(WOW_subset))

        states = Series(list((set(states))))
        states_group = pd.DataFrame()
        states_group['states'] = states
        states_group['chamber'] = '0'
        states_group['chamber'][states_group['states'].isin(self.high_subset)] = 'HIGH'
        states_group['chamber'][states_group['states'].isin(self.low_subset)] = 'LOW'
        states_group['wafer'] = '0'
        states_group['wafer'][(states_group['states'].isin(BOB_subset)) & (-states_group['states'].isin(WOW_subset))] = 'BOB'
        states_group['wafer'][(states_group['states'].isin(WOW_subset)) & (-states_group['states'].isin(BOB_subset)) ] = 'WOW'

        self.states = [tuple(x) for x in states_group[['states', 'chamber', 'wafer']].values]



"""class Matter(object):
    pass

chamber_perf = pd.read_csv('../result/chamber_perf.csv')

chamber_perf=chamber_perf.rename(columns = {'Unnamed: 0':'S_E_CHAMBER_ID'})
chamber_perf.drop(chamber_perf.index[:2], inplace=True)
chamber_perf = chamber_perf.reset_index(drop=True)
chambers = chamber_perf['S_E_CHAMBER_ID'].tolist()
chambers.append('START')

matter = Matter()
machine = Machine(model=model, 
                       states=states, 
                       transitions=transitions)
model.get_graph().draw('state2.png',prog='dot')"""

if __name__ == '__main__':
    class Matter(object):
        pass
    model = Model()
    matter = Matter()
    machine = Machine(model=matter, 
                           states=model.states, 
                           transitions=model.transitions)
    matter.get_graph().draw('../result/state.png',prog='dot')