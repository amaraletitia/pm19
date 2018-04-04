

class Filter(object):
	def __init__(object):
		pass

	def remove_duplicate(self, eventlog):
		print("##remove duplicates, {}".format(len(eventlog)))
		print("# cases: {}".format(eventlog.count_case()))
		eventlog = eventlog.drop_duplicates()
		eventlog = eventlog.reset_index(drop=True)
		print("result: {}".format(len(eventlog)))
		print("# cases: {}".format(eventlog.count_case()))
		return eventlog

