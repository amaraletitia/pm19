from svg_widget import Visualization
from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import sys

class DotVisualization(Visualization):
	"""docstring for DotVisualization"""
	def __init__(self, parent = None):
		super(DotVisualization, self).__init__(parent)
		app = QtWidgets.QApplication(sys.argv)
		Visualization.__init__(self)
		#app = QtWidgets.QApplication(sys.argv)

		#parser = ArgumentParser(description="Display SVG files.")
		#parser.add_argument("-v", "--version", help="show version information", default=False, action='store_const', const=True);
		#parser.add_argument("documents", nargs='*')


		#opt_parser.add_option("-q", dest="quickly", action="store_true",
		#    help="Do it quickly (default=False)")
		#(options, args) = opt_

		#parser.parse_args(map(str, app.arguments()))

		"""
		if  '-h' in app.arguments()[1:] or '--help' in app.arguments()[1:]:
		    print "Usage: svg_view.py <path_to_svg_file>?"
		    exit
		"""
		#Visualization.show()
		#Visualization.load('../result/state_svg.svg')
		#sys.exit(app.exec_())
		"""
		window = Visualization()
		window.show()

		#for path in app.arguments()[1:]:
		window.load('../result/state_svg.svg');

		sys.exit(app.exec_())
		"""