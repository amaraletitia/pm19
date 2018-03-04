#from preprocess import Preprocess



class Remove(object):
	def __init__(self):
		pass
	def remove_duplicate(self, eventlog):
		print("##remove duplicates, {}".format(len(eventlog)))
		eventlog = eventlog.drop_duplicates()
		eventlog = eventlog.reset_index(drop=True)
		print("result: {}".format(len(eventlog)))
		return eventlog

	#한 컬럼을 제외한 나머지 값들이 모두 같을 때?
	def remove_duplicates_except_one(self, eventlog, one='CHAMBER_ID'):
		print("##remove duplicates except one, {}".format(len(eventlog)))
		columns = list(eventlog.columns)
		columns_except_one = [x for x in columns if x != one]
		dup = eventlog.loc[eventlog.duplicated(columns_except_one, keep=False)]

		#CHAMEBER_ID & UNIT_ID가 같은 경우 하나로 합쳐주는 작업
		columns_except_chamber_unit_id = [x for x in columns if x !='CHAMBER_ID' and x != 'UNIT_ID']
		#print(columns_except_chamber_unit_id)
		try:
			duplicate_list = dup.groupby(columns_except_chamber_unit_id).apply(lambda x: list(x.index)).tolist()
			print("len of chamber_unit_id_duplicates: {}".format(len(duplicate_list)))
			idx = []
			del_idx = []
			value = []
			for pair in duplicate_list:
				chamber_id = eventlog['CHAMBER_ID'][pair[0]] + '-' + eventlog['CHAMBER_ID'][pair[1]]
				idx.append(pair[0])
				value.append(chamber_id)
				del_idx.append(pair[1])
				#value.append(chamber_id)
			#print(len(eventlog))
			eventlog.drop(eventlog.index[del_idx], inplace = True)
			eventlog.loc[idx, 'CHAMBER_ID'] = value
			eventlog = eventlog.reset_index(drop=True)
		except AttributeError:
			pass
		print("result: {}".format(len(eventlog)))
		return eventlog

	def remove_duplicate_chambers(self, eventlog):
		print("##Remove_duplicates_chamber")
		columns = list(eventlog.columns)
		print("HERE: {}".format(columns))
		columns_not_chamber_id = [x for x in columns if x != 'CHAMBER_ID' and x != 'UNIT_ID' and x != 'RESOURCE']
		#print(columns_not_chamber_id)
		#print(eventlog.duplicated(columns_not_chamber_id, keep='first'))
		eventlog = eventlog.loc[~eventlog.duplicated(columns_not_chamber_id, keep='first')]

		print("result: {}".format(len(eventlog)))
		return eventlog

	#하나의 케이스가 두 개 이상의 수율값을 가지면 해당 케이스 제거
	def remove_multiple_value(self, eventlog, value):
		print("##remove multiple value, {}".format(len(eventlog)))
		val_cnt_per_case = eventlog.groupby('CASE_ID')[value].nunique()
		eventlog = eventlog[eventlog.CASE_ID.isin(val_cnt_per_case[val_cnt_per_case == 1].index)]
		eventlog = eventlog.reset_index(drop=True)
		print("result: {}".format(len(eventlog)))
		return eventlog

	def remove_incomplete_wafer(self, eventlog, start, end):
		print("##remove incompleted wafer {}, Start_step: {}, End_step: {}".format(len(eventlog),start,end))
		user_defined_start = start
		user_defined_end = end

		START_STEP = eventlog.loc[(eventlog['ACTIVITY'] == user_defined_start)].CASE_ID
		START_STEP = START_STEP.reset_index(drop=True)
		END_STEP = eventlog.loc[(eventlog['ACTIVITY'] == user_defined_end)].CASE_ID
		END_STEP = END_STEP.reset_index(drop=True)

		eventlog = eventlog[eventlog.CASE_ID.isin(list(set(START_STEP) & set(END_STEP)))]
		print("result: {}".format(len(eventlog)))
		return eventlog

	def remove_incomplete_lot(self, eventlog, wafer_count=20):
		print("##Execute wafer_count {}, count: {}".format(len(eventlog) ,wafer_count))
		#LOT 내 Wafer 수가 23개 미만인 LOT 제외
		user_defined_wafer_count = wafer_count
		distinct_wafer_count = eventlog.groupby('ROOT_LOT_ID').CASE_ID.nunique()
		#distinct_wafer_count[distinct_count < 23].index
		eventlog = eventlog[eventlog['ROOT_LOT_ID'].isin(distinct_wafer_count[distinct_wafer_count >= user_defined_wafer_count].index)]
		print("result: {}".format(len(eventlog)))
		return eventlog





	def remove_incomplete_flow(self, eventlog, num_activities):
		print("##Remove diff_step_flow: {}".format(len(eventlog)))

		distinct_case_activity = eventlog.groupby('CASE_ID').ACTIVITY.apply(list)
		removes = []
		for case in distinct_case_activity.index:
			if len(distinct_case_activity[case]) != num_activities:
				removes.append(case)
		#print(len(removes))
		eventlog = eventlog.loc[~eventlog['CASE_ID'].isin(removes), :]
		print("result: {}".format(len(eventlog)))
		return eventlog

	def remove_diff_flow(self, eventlog):
		print("##Remove_diff_flow: {}".format(len(eventlog)))
		activities_in_case = eventlog.groupby('CASE_ID').ACTIVITY.apply(list)
		removes = []
		for index, row in activities_in_case.iteritems():

			if len(row) > len(set(row)):
				removes.append(index)

		eventlog = eventlog.loc[~eventlog['CASE_ID'].isin(removes), :]
		print("result: {}".format(len(eventlog)))
		return eventlog



