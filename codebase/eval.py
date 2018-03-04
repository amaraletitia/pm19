import pandas as pd
from pandas import DataFrame, Series
import numpy as np

class Import(object):
	def __init__(self, data_source):
		self.data = pd.read_csv(data_source, sep = ',', index_col = 'Unnamed: 0')
		#print(self.data)



def assign(x, sign):
	x.append(sign)

if __name__ == '__main__':
	ip = Import('./result/prod_temp.csv')
	"""BOB"""
	BOB_wafer = ip.data.loc[ip.data['BOB']==1, ['CASE_ID', 'FROM']]
	
	grouped = BOB_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'BOB'
	print(grouped)
	#grouped.apply(lambda x: assign(x, 'BOB'))
	BOB_seq = grouped
	"""WOW"""
	WOW_wafer = ip.data.loc[ip.data['WOW']==1, ['CASE_ID', 'FROM']]
	
	grouped = WOW_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'WOW'
	#grouped.apply(lambda x: assign(x, 'WOW'))
	WOW_seq = grouped
	print(grouped)
	"""Dummy"""
	Dummy_wafer = ip.data.loc[(ip.data['BOB']==0)&(ip.data['WOW']==0), ['CASE_ID', 'FROM']]
	
	grouped = Dummy_wafer.groupby('CASE_ID').FROM.apply(list)
	grouped = grouped.to_frame('Seq')
	grouped['Result'] = 'Dummy'
	#grouped.apply(lambda x: assign(x, 'Dummy'))
	Dummy_seq = grouped
	print(grouped)
	seqs = pd.concat([BOB_seq, WOW_seq, Dummy_seq])
	seqs['value'] = 1
	
	def delist(x):
		return '/'.join(x)

	#list to string
	seqs['Seq'] = seqs['Seq'].apply(delist)
	#count based on seq and result
	grouped = seqs.groupby(('Seq', 'Result'))
	seq_res_count = grouped.value.apply(np.count_nonzero)
	seq_res_count = seq_res_count.to_frame('COUNT')
	seq_res_count.reset_index(inplace=True)
	print(seq_res_count)

	#max 값만 남기고 나머지는 삭제
	seqs = seq_res_count.groupby('Seq').COUNT.max()
	seqs = seqs.to_frame('COUNT')
	seqs.reset_index(inplace=True)
	print(seqs)

	output = pd.merge(seqs, seq_res_count, on=['Seq','COUNT'], how='left')
	#del output['COUNT_MAX']
	print(output)

	#seqs.drop_duplicates(inplace=True)
	
	output.to_csv('./result/eval.csv', sep=',', index = True)