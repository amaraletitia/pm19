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
    pass

#load wafer_BOB_WOW_Group, manipulate dataframe to create wafer_info
wafer_BOB_WOW_Group = pd.read_csv('../result/wafer_BOB_WOW_Group.csv', index_col = False)
del wafer_BOB_WOW_Group['Unnamed: 0']
wafer_BOB_WOW_Group.sort_values(by=['CASE_ID', 'STEP_SEQ'], inplace = True)
wafer_BOB_WOW_Group.reset_index(inplace=True)
del wafer_BOB_WOW_Group['index']


wafer_info = wafer_BOB_WOW_Group.copy()


count = 0
index = 0
case_id = wafer_info['CASE_ID'][0]
f = []
t = []
for row in wafer_info.itertuples():
    #print(row.S_E_CHAMBER_ID)
    
    if case_id == row.CASE_ID:
        if count == 0:
            f.append('START')
            t.append(row.S_E_CHAMBER_ID)
            #wafer_info['FROM'][index] = 'START'
            #wafer_info['TO'][index] = row.S_E_CHAMBER_ID
        else:
            f.append(wafer_info['S_E_CHAMBER_ID'][row.Index-1])
            t.append(row.S_E_CHAMBER_ID)
            #wafer_info['FROM'][index] = wafer_info['S_E_CHAMBER_ID'][row.Index-1]
            #wafer_info['TO'][index] = row.S_E_CHAMBER_ID
        count+=1
    else:
        count = 0
        case_id = row.CASE_ID
        if count == 0:
            f.append('START')
            t.append(row.S_E_CHAMBER_ID)
            #wafer_info['FROM'][index] = 'START'
            #wafer_info['TO'][index] = row.S_E_CHAMBER_ID
        count+=1

wafer_info = wafer_info.assign(FROM = f, TO=t)



wafer_group = pd.read_csv('../result/chamber_stat_comparison.csv')
def dummy(x):
    return x[:8] + '_dummy'

def checkEqual1(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

wafer_info_dummy_equal_from = wafer_info.copy()

unique_to = list(set(wafer_info_dummy_equal_from['TO']))
for to in unique_to:
    froms = list(set(wafer_info_dummy_equal_from.loc[wafer_info_dummy_equal_from['TO'] == to]['FROM']))
    froms_attr = wafer_group.loc[wafer_group['S_E_CHAMBER_ID'].isin(froms)]['LCresult']
    if 'START' not in froms:
        if checkEqual1(froms_attr):
            wafer_info_dummy_equal_from['TO'][wafer_info_dummy_equal_from['TO'] == to] = to[:8] + '_' + 'dummy'


wafer_trans = wafer_info_dummy_equal_from.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])


#10개 미만인 edge 삭제
#wafer_trans.drop(wafer_trans.loc[wafer_trans['BIN_VALUE', 'count_nonzero'] < 50].index, inplace=True)

transitions = []
states = []
for row in wafer_trans.itertuples():
    d = {
        'trigger': row._1.astype(str),
        'source': row.Index[0],
        'dest': row.Index[1]
    }
    transitions.append(d)
    states.append(row.Index[0])
    states
    states.append(row.Index[1])

wafer_group.reset_index(level=0, inplace=True)
BOB_subset = wafer_group.loc[wafer_group['LCresult'] == 'BOB', 'S_E_CHAMBER_ID']
WOW_subset = wafer_group.loc[wafer_group['LCresult'] == 'WOW', 'S_E_CHAMBER_ID']

states = Series(list((set(states))))
states_group = pd.DataFrame()
states_group['states'] = states
states_group['result'] = '0'
states_group['result'][states_group['states'].isin(BOB_subset)] = 'BOB'
states_group['result'][states_group['states'].isin(WOW_subset)] = 'WOW'

states = [tuple(x) for x in states_group[['states', 'result']].values]


class Matter(object):
    pass

chamber_perf = pd.read_csv('../result/chamber_perf.csv')

chamber_perf=chamber_perf.rename(columns = {'Unnamed: 0':'S_E_CHAMBER_ID'})
chamber_perf.drop(chamber_perf.index[:2], inplace=True)
chamber_perf = chamber_perf.reset_index(drop=True)
chambers = chamber_perf['S_E_CHAMBER_ID'].tolist()
chambers.append('START')

model = Matter()
machine = Machine(model=model, 
                       states=states, 
                       transitions=transitions)
model.get_graph().draw('state2.png',prog='dot')