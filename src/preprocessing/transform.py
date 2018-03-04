

class Transform(object):
	def __init__(object):
		pass

	def produce_wafer_data(self, eventlog):
		#eventlog.loc[:,'S_E_CHAMBER_ID'] = eventlog['STEP_SEQ'] + '_' + eventlog['EQP_ID'] + '_' + eventlog['CHAMBER_ID']

		wafer_data = eventlog[['CASE_ID', 'ACTIVITY', 'RESOURCE', 'VALUE', 'TKIN_TIME']]

		wafer_data.sort_values(by=['CASE_ID', 'ACTIVITY'], inplace = True)
		wafer_data.reset_index(inplace = True)
		del wafer_data['index']

		return wafer_data