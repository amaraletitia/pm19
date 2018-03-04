import pandas as pd
from pandas import DataFrame, Series
import numpy as np

class Import(object):
	def __init__(self, data_source):
		self.data = pd.read_csv(data_source, sep = ',')
		#print(self.data)

if __name__ == '__main__':
	eval_0 = Import('./eval_0.csv')
	eval_0 = eval_0.data
	eval_1 = Import('./eval_1.csv')
	eval_1 = eval_1.data

	bb = 0
	bd = 0
	bw = 0
	ww = 0
	wd = 0
	wb = 0
	dd = 0
	db = 0
	dw = 0
	count = 0
	for index, row in eval_1.iterrows():
		count+=1
		if row['Result'] == 'BOB':
			BOB_fit = False
			Dummy_fit = False
			WOW_fit = False
			
			eval_0_result = eval_0.loc[eval_0['Seq'] == row['Seq'],'Result']
			for i in eval_0_result:
				if i == row['Result']:
					BOB_fit = True
			if BOB_fit == True:
				bb += 1
				continue
			else:
				for i in eval_0_result:
					if i == 'Dummy':
						Dummy_fit=True
				if Dummy_fit==True:
					bd+=1
					continue
				else:
					bw+=1
					continue

		if row['Result'] == 'WOW':
			BOB_fit = False
			Dummy_fit = False
			WOW_fit = False
			
			eval_0_result = eval_0.loc[eval_0['Seq'] == row['Seq'],'Result']
			for i in eval_0_result:
				if i == row['Result']:
					WOW_fit = True
			if WOW_fit == True:
				ww += 1
				continue
			else:
				for i in eval_0_result:
					if i == 'Dummy':
						Dummy_fit=True
				if Dummy_fit==True:
					wd+=1
					continue
				else:
					wb+=1
					continue

		if row['Result'] == 'Dummy':
			BOB_fit = False
			Dummy_fit = False
			WOW_fit = False
			
			eval_0_result = eval_0.loc[eval_0['Seq'] == row['Seq'],'Result']
			for i in eval_0_result:
				if i == row['Result']:
					Dummy_fit = True
			if Dummy_fit == True:
				dd += 1
				continue
			else:
				for i in eval_0_result:
					if i == 'BOB':
						BOB_fit=True
				if BOB_fit==True:
					db+=1
					continue
				else:
					dw+=1
					continue




	#bb = bb/count
	print("bb: {}, bd: {}, bw: {}, db:{}, dd: {}, dw: {}, wb: {}, wd: {}, ww: {}, count: {}".format(bb, bd, bw, db, dd, dw, wb, wd, ww, count))