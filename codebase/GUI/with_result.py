from PyQt5 import QtGui  # Import the PyQt4 module we'll need
from PyQt5 import QtWidgets, QtCore
import sys  # We need sys so that we can pass argv to QApplication
import result_input
from visualization_widget import Visualization
from result_visualization import Result_Visualization

import sys, signal, os  # For listing directory methods

sys.path.append('C:/Users/ProDesk/Desktop/LAB/SAMSUNG_PROJECT/IMPLE/codebase')
from Model import Model
from diagrams import Graph

import pandas as pd
import sqlite3

class With_Result(QtWidgets.QWidget, result_input.Ui_Form):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.con = sqlite3.connect('PREPROCESSING.db')
		result = pd.read_sql_query("SELECT * from result;",self.con)
		
		self.result_tableWidget.setColumnCount(len(result.columns))
		self.result_tableWidget.setRowCount(len(result.index))
		self.result_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
		self.result_tableWidget.setHorizontalHeaderLabels(list(result.columns))
		for i in range(len(result.index)):
		    for j in range(len(result.columns)):
		        self.result_tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(result.iat[i, j])))
		self.result_tableWidget.itemSelectionChanged.connect(self.get_same_row_cell)
		self.result_push.clicked.connect(self.forward_visualization_tab)



	def get_same_row_cell(self):
		row = self.result_tableWidget.currentItem().row()
		#col = self.result_tableWidget.currentItem().column()
		"""
		#loop through headers and find column number for given column name
		headercount = self.result_tableWidget.columnCount()
		for x in range(0,headercount,1):
		    headertext = self.result_tableWidget.horizontalHeaderItem(x).text()
		    if columnname == headertext:
		        matchcol = x
		        break
		#print(row,matchcol)
		"""
		  # get cell at row, col
		self.svg_name = self.result_tableWidget.item(row, 30).text()


	def show_visualization(self):
		self.visualization_window = Result_Visualization(self.svg_name, self)
		self.visualization_window.closed.connect(self.show)
		self.visualization_window.show()
		self.hide()

	def forward_visualization_tab(self):
		self.show_visualization()
		#app = QtWidgets.QApplication(sys.argv)
		
		#window.show()

		#for path in app.arguments()[1:]:
		#window.load('../result/state_svg.svg');

		#This is a hack to let the interperter run once every 1/2 second to catch sigint
		#timer = QtCore.QTimer()
		#timer.start(500)  
		#timer.timeout.connect(lambda: None)
		#signal.signal(signal.SIGINT, handleIntSignal)

		#sys.exit(app.exec_())