

class Filter(object):
	def __init__(object):
		pass

	def filter_activity(self, eventlog, activities):
		print("##complete activity filter: {}".format(len(eventlog)))
		eventlog = eventlog.loc[eventlog['ACTIVITY'].isin(activities)]
		print("##complete activity filter: {}".format(len(eventlog)))
		return eventlog

	def filter_eqp(self, eventlog, chamber_variety_count=20):
		print("##Execute chamber_variety, count: {}".format(chamber_variety_count))
		#설비의 CHAMBER 종류가 20개 이상인 경우 CHAMBER는 NULL 처리
		distinct_chamber_count = eventlog.groupby('EQP_ID')['CHAMBER_ID'].nunique()

		eventlog.loc[eventlog['EQP_ID'].isin(distinct_chamber_count[distinct_chamber_count >= chamber_variety_count].index), 'CHAMBER_ID']='NULL'

		print("result: {}".format(len(eventlog)))
		return eventlog