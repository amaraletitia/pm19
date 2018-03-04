import pandas as pd
from pandas import DataFrame, Series
import numpy as np



class Import(object):
	def __init__(self, data_source):
		self.data = pd.read_csv(data_source, sep = ',', index_col = 'Unnamed: 0')
		#print(self.data)

if __name__ == '__main__':
	states = ['AB0000004_EQP_303_C', 'AB0000005_DM', 'AB0000009_DM', 'AB0000007_EQP_161_3', 'AB0000004_EQP_301_C', 'AB0000002_EQP_140_4', 'AB0000009_EQP_270_D', 'AB0000010_EQP_310_C', 'AB0000004_EQP_297_A', 'AB0000005_EQP_118_4', 'AB0000009_EQP_275_F', 'AB0000010_EQP_303_A', 'AB0000004_EQP_300_B', 'AB0000004_DM', 'AB0000004_EQP_304_A', 'AB0000006_EQP_173_4', 'AB0000004_EQP_300_C', 'AB0000006_DM', 'AB0000010_EQP_304_A', 'END', 'AB0000007_EQP_161_2', 'AB0000010_DM', 'START', 'AB0000007_DM', 'AB0000010_EQP_310_A', 'AB0000002_DM', 'AB0000008_DM', 'AB0000004_EQP_304_C', 'AB0000001_DM', 'AB0000003_EQP_140_3', 'AB0000001_EQP_236_EX2', 'AB0000003_DM']

	ip = Import('./wafer_BOB_WOW_Group.csv')
	wafer_data = ip.data.loc[:, ['CASE_ID', 'FROM', 'BOB', 'WOW']]
	#print(wafer_data)

	def assign(x):
		if x in states:
			return x
		else:
			return x.split("_")[0] + "_DM"
	wafer_data['FROM'] = wafer_data['FROM'].apply(assign)
	print(wafer_data)

	BOB_wafer = wafer_data.loc[wafer_data['BOB']==True, ['CASE_ID', 'FROM']]
	grouped = BOB_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'BOB'
	print(grouped)
	#grouped.apply(lambda x: assign(x, 'BOB'))
	BOB_seq = grouped

	WOW_wafer = wafer_data.loc[wafer_data['WOW']==True, ['CASE_ID', 'FROM']]
	grouped = WOW_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'WOW'
	#grouped.apply(lambda x: assign(x, 'WOW'))
	WOW_seq = grouped
	print(grouped)
	"""Dummy"""
	Dummy_wafer = wafer_data.loc[(wafer_data['BOB']==0)&(wafer_data['WOW']==0), ['CASE_ID', 'FROM']]
	
	grouped = Dummy_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'Dummy'
	#grouped.apply(lambda x: assign(x, 'Dummy'))
	Dummy_seq = grouped
	print(grouped)
	seqs = pd.concat([BOB_seq, WOW_seq, Dummy_seq])

	def delist(x):
		return '/'.join(x)

	#list to string
	seqs['Seq'] = seqs['Seq'].apply(delist)
	output = seqs
	print(output)
	
	output.to_csv('./result/eval_1.csv', sep=',', index = True)