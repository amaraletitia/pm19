from PyProM.src.preprocessing.remove import Remove
from PyProM.src.preprocessing.transform import Transform
from PyProM.src.preprocessing.filter import Filter


class Preprocess(object):
	def __call__(self, data):
		raise NotImplementedError("Subclasses need to implement __call__")


class Remover(Remove):

	def __init__(self):
		super(Remover, self).__init__()

class Transformer(Transform):

	def __init__(self):
		super(Transformer, self).__init__()

class Filtering(Filter):
	def __init__(self):
		super(Filtering, self).__init__()