from PyQt5 import QtGui  # Import the PyQt4 module we'll need
from PyQt5 import QtWidgets, QtCore
import sys  # We need sys so that we can pass argv to QApplication
import preprocessed_data_input
from visualization_widget import Visualization
import interval_dialog
import mean_criterion_dialog, std_criterion_dialog, value_criterion_dialog, stat_parameters_dialog, user_defined_analysis_dialog, progress_dialog

import sys, signal, os  # For listing directory methods

sys.path.append('../')
from Preprocessing import Preprocessing
from Classifier import Classifier
from LOT_Classifier import LOT_Classifier
from Dummy import Analysis
from LOT_Dummy import LOT_Analysis
from Model import Model
from diagrams import Graph

import pandas as pd
import sqlite3
import time
import numpy as np

class After_Preprocessing(QtWidgets.QWidget, preprocessed_data_input.Ui_Form):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.con = sqlite3.connect('PREPROCESSING.db')
		self.processed_dataset = pd.read_sql_query("SELECT * from processed_dataset;",self.con)
		
		self.data_tableWidget.setColumnCount(len(self.processed_dataset.columns))
		self.data_tableWidget.setRowCount(len(self.processed_dataset.index))
		self.data_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
		self.data_tableWidget.setHorizontalHeaderLabels(list(self.processed_dataset.columns))
		for i in range(len(self.processed_dataset.index)):
		    for j in range(len(self.processed_dataset.columns)):
		        self.data_tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(self.processed_dataset.iat[i, j])))
		self.data_tableWidget.itemSelectionChanged.connect(self.get_same_row_cell)

		self.actionDelete = QtWidgets.QAction(self)
		self.actionDelete.setShortcuts(QtGui.QKeySequence("Backspace"))
		self.data_tableWidget.addAction(self.actionDelete)
		self.actionDelete.triggered.connect(self.delete_rows)

		self.preprocessed_data_dialog_push.clicked.connect(self.forward_data_selection_tab)

		#FSM_model
		self.user_defined_representation_option = 'sequence'
		self.representation_combobox.activated.connect(self.handle_representation_combobox)
		self.user_defined_type_option = 'prefix'
		self.type_combobox.activated.connect(self.handle_type_combobox)
		self.user_defined_horizon_option = '1'
		self.horizon_lineEdit.textChanged.connect(self.handle_horizon_lineEdit)
		self.user_defined_filter_option = None
		self.filter_combobox.activated.connect(self.handle_filter_combobox)
		self.next_push_4.clicked.connect(self.forward_fsm_model_tab)
	
		#Machine Path
		self.user_defined_mean_criterion_option = 'Relative Ratio'
		self.mean_BOB_criterion = None
		self.mean_WOW_criterion = None
		self.user_defined_std_criterion_option = 'Relative Ratio'
		self.user_defined_std_criterion_option = None
		self.std_criterion = None
		self.user_defined_value_criterion_option = 'Relative Ratio'
		self.value_BOB_criterion = None
		self.value_WOW_criterion = None
		self.KS_alpha = None
		self.ANOVA_alpha = None
		self.KRUSKAL_alpha = None
		self.LC_alpha = None
		self.NLC_alpha = None
		self.MT_alpha = None
		self.UT_alpha = None
		self.BOB_avg = None
		self.WOW_avg = None
		self.BOB_prop = None
		self.WOW_prop = None
		self.chamber_weight = None
		self.step_weight = None
		self.mode = None
		self.mean_combobox.activated.connect(self.handle_mean_combobox)
		self.mean_BOB_lineEdit.textChanged.connect(self.handle_mean_BOB_lineEdit)
		self.mean_WOW_lineEdit.textChanged.connect(self.handle_mean_WOW_lineEdit)
		self.lot_convert_push.clicked.connect(self.handle_lot_convert_push)
		self.std_combobox.activated.connect(self.handle_std_combobox)
		self.std_Over_lineEdit.textChanged.connect(self.handle_std_Over_lineEdit)
		self.std_Under_lineEdit.textChanged.connect(self.handle_std_Under_lineEdit)
		self.value_criterion_combobox.activated.connect(self.handle_value_criterion_combobox)
		self.value_BOB_lineEdit.textChanged.connect(self.handle_value_BOB_lineEdit)
		self.value_WOW_lineEdit.textChanged.connect(self.handle_value_WOW_lineEdit)
		self.convert_push.clicked.connect(self.handle_convert_push)
		self.next_push_5.clicked.connect(self.forward_machine_path_tab)


		#HIGH/LOW
		self.statistical_analysis_check.stateChanged.connect(self.handle_statistical_analysis_checkbox)
		self.user_defined_analysis_check.stateChanged.connect(self.handle_user_defined_analysis_checkbox)
		self.analysis_mode = 'or'
		self.and_check.stateChanged.connect(self.handle_and_checkbox)
		self.next_push_6.clicked.connect(self.forward_high_low_tab)

		#Model Simplification
		self.dummy_option = 0
		self.dummy_combobox.activated.connect(self.handle_dummy_combobox)
		self.edge_threshold = 50
		self.visualization_push.clicked.connect(self.forward_visualization_tab)


	def get_same_row_cell(self, columnname='DB_name'):
		try:
			row = self.data_tableWidget.currentItem().row()
		except AttributeError:
			pass
		#col = self.data_tableWidget.currentItem().column()
		"""
		#loop through headers and find column number for given column name
		headercount = self.data_tableWidget.columnCount()
		for x in range(0,headercount,1):
		    headertext = self.data_tableWidget.horizontalHeaderItem(x).text()
		    if columnname == headertext:
		        matchcol = x
		        break
		#print(row,matchcol)
		"""
		  # get cell at row, col
		headercount = self.data_tableWidget.columnCount()
		self.user_defined_input_name = self.data_tableWidget.item(row,0).text()
		self.user_defined_user_name = self.data_tableWidget.item(row,1).text()
		self.user_defined_user_info = self.data_tableWidget.item(row,2).text()
		self.user_defined_analysis =  self.data_tableWidget.item(row,3).text()
		self.user_defined_Incomplete_wafer = self.data_tableWidget.item(row,4).text()
		self.user_defined_min_num = self.data_tableWidget.item(row,5).text()
		self.step_criterion = self.data_tableWidget.item(row,6).text()
		self.step_criterion = int(self.step_criterion)
		self.period_text = self.data_tableWidget.item(row,7).text()
		self.main_text = self.data_tableWidget.item(row,8).text()
		self.db_name = self.data_tableWidget.item(row,9).text()

	def delete_rows(self):
		#on the screen
		index_list = []                                                          
		for model_index in self.data_tableWidget.selectionModel().selectedRows():
			index = QtCore.QPersistentModelIndex(model_index)
			index_list.append(index)                                             
		count = 0
		for index in index_list:
			start_row = int(index.row())
			count+=1
			#print(index.row())
			self.data_tableWidget.removeRow(index.row()) 
		print("start row: {}".format(start_row))
		print("count: {}".format(count))

		#files
		for i in range(count):
			db_name = self.processed_dataset['DB_name'][start_row+i]
			try:
				os.remove("./DB/{}".format(db_name))
				print("delete {}".format(db_name))
			except FileNotFoundError as e:
				print(e)

		#on the processed_dataset
		for i in range(count):
			try:
				self.processed_dataset.drop(self.processed_dataset.index[start_row + i], inplace=True)
				print("delete {}_th row from processed_datasets".format(i+start_row))
			except IndexError as e:
				print(e)
		self.processed_dataset.reset_index(drop = True, inplace = True)
		#self.processed_dataset.drop('level_0', axis=1, inplace=True)
		#self.processed_dataset.drop('index', axis=1, inplace=True)
		self.processed_dataset.to_sql("processed_dataset", self.con, if_exists="replace", index=False)


	def forward_data_selection_tab(self):
		def connect_to_db():
			self.BASE_DIR   =  os.path.abspath('.')
			self.TARGET_DIR =  os.path.join(self.BASE_DIR, "DB")
			#self.TARGET_FILE = '{}.db'.format('DB_' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
			self.TARGET_FILE = '{}'.format(self.db_name)
			self.TARGET_FILE_FULL_PATH = os.path.join(self.TARGET_DIR, self.TARGET_FILE)
			self.preprocessing_con = sqlite3.connect(self.TARGET_FILE_FULL_PATH)
		connect_to_db()
		print(self.TARGET_FILE_FULL_PATH)
		with self.preprocessing_con:
			cur = self.preprocessing_con.cursor()
			cur.execute(' select name from sqlite_master where type="table"')
			print(cur.fetchall())
		self.preprocessing_data = pd.read_sql_query("select * from preprocessed_data;", self.preprocessing_con)

		if self.user_defined_analysis == 'Wafer-based Analysis':
			self.value_criterion_combobox.setEnabled(True)
			self.value_BOB_lineEdit.setEnabled(True)
			self.value_WOW_lineEdit.setEnabled(True)
			self.convert_push.setEnabled(True)
		elif self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			self.value_criterion_combobox.setEnabled(True)
			self.std_combobox.setEnabled(True)
			self.value_BOB_lineEdit.setEnabled(True)
			self.value_WOW_lineEdit.setEnabled(True)
			self.std_Over_lineEdit.setEnabled(True)
			self.convert_push.setEnabled(True)
		elif self.user_defined_analysis == 'Lot-based Analysis':
			self.mean_combobox.setEnabled(True)
			self.std_combobox.setEnabled(True)
			self.mean_BOB_lineEdit.setEnabled(True)
			self.mean_WOW_lineEdit.setEnabled(True)
			self.std_Under_lineEdit.setEnabled(True)
			self.lot_convert_push.setEnabled(True)

		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_representation_combobox(self):
		self.user_defined_representation_option = str(self.representation_combobox.currentText())

	def handle_type_combobox(self):
		self.user_defined_type_option = str(self.type_combobox.currentText())

	def handle_horizon_lineEdit(self):
		self.user_defined_horizon_option = self.horizon_lineEdit.text()

	def handle_filter_combobox(self):
		self.user_defined_filter_option = str(self.filter_combobox.currentText())

	def forward_fsm_model_tab(self):

		if self.user_defined_analysis == 'Wafer-based Analysis':
			self.classifier = Classifier(self.preprocessing_data)
			self.classifier.create_wafer_data(user_defined_ratio=self.step_criterion*0.01, horizon = int(self.user_defined_horizon_option))
			self.classifier.wafer_data.to_sql("wafer_data", self.preprocessing_con, if_exists="replace")


		elif self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			self.classifier = Classifier(self.preprocessing_data)

			self.classifier.create_raw_lot_data()

		elif self.user_defined_analysis == 'Lot-based Analysis':
			self.classifier = LOT_Classifier(self.preprocessing_data)

			self.classifier.create_raw_lot_data()
			self.classifier.create_lot_data(horizon=int(self.user_defined_horizon_option))
			self.classifier.lot_data.to_sql("lot_data", self.preprocessing_con, if_exists="replace", index = False)


		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_mean_combobox(self):
		self.user_defined_mean_criterion_option = str(self.mean_combobox.currentText())
		if self.user_defined_mean_criterion_option == 'Relative Ratio':
			self.lot_convert_push.setEnabled(True)
		else:
			self.lot_convert_push.setEnabled(False)
		print("select mean criterion: {}".format(self.user_defined_mean_criterion_option))

	def handle_mean_BOB_lineEdit(self):
		self.mean_BOB_criterion = int(self.mean_BOB_lineEdit.text())
		
	def handle_mean_WOW_lineEdit(self):
		self.mean_WOW_criterion = int(self.mean_WOW_lineEdit.text())

	def handle_lot_convert_push(self):
		self.classifier.raw_lot_data_temp = self.classifier.raw_lot_data.groupby('ROOT_LOT_ID').agg([np.mean, np.std])
		mean = self.classifier.raw_lot_data_temp['VALUE', 'mean']
		BOB_mean_criterion = np.percentile(mean, self.mean_BOB_criterion)
		WOW_mean_criterion = np.percentile(mean, self.mean_WOW_criterion)

		self.BOB_mean.setText(str(BOB_mean_criterion))
		self.WOW_mean.setText(str(WOW_mean_criterion))

	def handle_std_combobox(self):
		self.user_defined_std_criterion_option = str(self.std_combobox.currentText())
		print("select std criterion: {}".format(self.user_defined_std_criterion_option))

	def handle_std_Under_lineEdit(self):
		try:
			self.std_criterion = int(self.std_Under_lineEdit.text())
		except AttributeError:
			pass
	def handle_std_Over_lineEdit(self):
		try:
			self.std_criterion = int(self.std_Over_lineEdit.text())
		except AttributeError:
			pass

	def handle_value_criterion_combobox(self):
		self.user_defined_value_criterion_option = str(self.value_criterion_combobox.currentText())
		if self.user_defined_value_criterion_option == 'Relative Ratio':
			self.convert_push.setEnabled(True)
		else:
			self.convert_push.setEnabled(False)
		print("select value criterion: {}".format(self.user_defined_value_criterion_option))

	def handle_value_BOB_lineEdit(self):
		self.value_BOB_criterion = int(self.value_BOB_lineEdit.text())
		
	def handle_value_WOW_lineEdit(self):
		self.value_WOW_criterion = int(self.value_WOW_lineEdit.text())

	def handle_convert_push(self):
		self.classifier.wafer_data_temp = self.classifier.wafer_data.groupby('CASE_ID').agg([np.mean, np.std])
		mean = self.classifier.wafer_data_temp['VALUE', 'mean']
		value_BOB_criterion = np.percentile(mean, self.value_BOB_criterion)
		value_WOW_criterion = np.percentile(mean, self.value_WOW_criterion)

		self.BOB_value.setText(str(value_BOB_criterion))
		self.WOW_value.setText(str(value_WOW_criterion))


	def forward_machine_path_tab(self):
		if self.user_defined_analysis == 'Wafer-based Analysis':
			if self.user_defined_value_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = self.value_BOB_criterion, WOW_mean_rela_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Absolute Value':
				self.classifier.absoulte_value_mean_criterion(BOB_mean_abs_criterion = self.value_BOB_criterion, WOW_mean_abs_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.value_BOB_criterion, WOW_n = self.value_WOW_criterion)
			self.classifier.create_wafer_BOB_WOW_group()
			self.classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", self.preprocessing_con, if_exists="replace")
			self.classifier.create_chamber_perf()
			self.classifier.chamber_perf.to_sql("chamber_perf", self.preprocessing_con, if_exists="replace")

		elif self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			if self.user_defined_std_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_std_criterion(std_rela_criteiron = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Absolute Value':
				self.classifier.absoulte_value_std_criterion(std_abs_criterion = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Rank-based':
				self.classifier.rank_based_std_criterion(self, n = self.std_criterion)
			self.classifier.extract_deviated_lot()

			self.classifier.create_wafer_data(user_defined_ratio=self.step_criterion*0.01, horizon = int(self.user_defined_horizon_option))
			self.classifier.wafer_data.to_sql("wafer_data", self.preprocessing_con, if_exists="replace")

			if self.user_defined_value_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = self.value_BOB_criterion, WOW_mean_rela_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Absolute Value':
				self.classifier.absoulte_value_mean_criterion(BOB_mean_abs_criterion = self.value_BOB_criterion, WOW_mean_abs_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.value_BOB_criterion, WOW_n = self.value_WOW_criterion)

			self.classifier.create_wafer_BOB_WOW_group()
			self.classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", self.preprocessing_con, if_exists="replace")

			self.classifier.create_chamber_perf()
			self.classifier.chamber_perf.to_sql("chamber_perf", self.preprocessing_con, if_exists="replace")

		elif self.user_defined_analysis == 'Lot-based Analysis':
			if self.user_defined_std_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_std_criterion(std_rela_criteiron = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Absolute Value':
				self.classifier.absoulte_value_std_criterion(std_abs_criterion = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Rank-based':
				self.classifier.rank_based_std_criterion(self, n = self.std_criterion)

			if self.user_defined_mean_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = self.mean_BOB_criterion, WOW_mean_rela_criterion = self.mean_WOW_criterion)
			elif self.user_defined_mean_criterion_option == 'Absolute Value':
				self.classifier.absoulte_value_mean_criterion(BOB_mean_abs_criterion = self.mean_BOB_criterion, WOW_mean_abs_criterion = self.mean_WOW_criterion)
			elif self.user_defined_mean_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.mean_BOB_criterion, WOW_n = self.mean_WOW_criterion)
			
			self.classifier.create_lot_BOB_WOW_group()
			self.classifier.lot_BOB_WOW_Group.to_sql("lot_BOB_WOW_Group", self.preprocessing_con, if_exists="replace", index = False)

			self.classifier.create_eqp_perf()
			self.classifier.eqp_perf.to_sql("eqp_perf", self.preprocessing_con, if_exists="replace")
			self.classifier.eqp_perf.to_csv('../result/eqp_perf.csv', sep=',')

		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_statistical_analysis_checkbox(self):
		if self.statistical_analysis_check.isChecked():
			self.stat_parameters_dialog_window = Stat_Parameters_Dialog()
			if self.stat_parameters_dialog_window.exec_():
				self.KS_alpha = float(self.stat_parameters_dialog_window.KS_alpha)
				self.ANOVA_alpha = float(self.stat_parameters_dialog_window.ANOVA_alpha)
				self.KRUSKAL_alpha = float(self.stat_parameters_dialog_window.KRUSKAL_alpha)
				self.LC_alpha = float(self.stat_parameters_dialog_window.LC_alpha)
				self.NLC_alpha = float(self.stat_parameters_dialog_window.NLC_alpha)
				self.MT_alpha = float(self.stat_parameters_dialog_window.MT_alpha)
				self.UT_alpha = float(self.stat_parameters_dialog_window.UT_alpha)
		else:
			self.KS_alpha = None
			self.ANOVA_alpha = None
			self.KRUSKAL_alpha = None
			self.LC_alpha = None
			self.NLC_alpha = None
			self.MT_alpha = None
			self.UT_alpha = None

	def handle_user_defined_analysis_checkbox(self):
		if self.user_defined_analysis_check.isChecked():
			self.user_defined_analysis_dialog_window = User_Defined_Analysis_Dialog()
			if self.user_defined_analysis_dialog_window.exec_():
				try:
					self.BOB_avg = float(self.user_defined_analysis_dialog_window.BOB_avg)
					self.WOW_avg = float(self.user_defined_analysis_dialog_window.WOW_avg)
				except AttributeError:
					pass
				try:
					self.BOB_prop = float(self.user_defined_analysis_dialog_window.BOB_prop)
					self.WOW_prop = float(self.user_defined_analysis_dialog_window.WOW_prop)
				except AttributeError:
					pass
				self.step_weight = float(self.user_defined_analysis_dialog_window.step_weight)
				self.chamber_weight = float(self.user_defined_analysis_dialog_window.machine_weight)
				try:
					self.mode = str(self.user_defined_analysis_dialog_window.mode)
				except AttributeError:
					pass
		else:
			self.BOB_avg = None
			self.WOW_avg = None
			self.BOB_prop = None
			self.WOW_prop = None
			self.step_weight = None
			self.chamber_weight = None
			self.mode = None

	def handle_and_checkbox(self):
		if self.and_check.isChecked():
			self.analysis_mode = 'and'
		else:
			self.analysis_mode = 'or'


	def forward_high_low_tab(self):
		if self.user_defined_analysis == 'Wafer-based Analysis' or self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			self.analyzer = Analysis(self.preprocessing_con)
			try:
				if all([self.KS_alpha != None, self.ANOVA_alpha != None, self.KRUSKAL_alpha != None]):
					self.analyzer.create_KS_test(alpha_normality=self.KS_alpha)
					self.analyzer.create_ANOVA(alpha_ANOVA = self.ANOVA_alpha, alpha_KRUSKAL=self.KRUSKAL_alpha)
					#self.analyzer.create_Kruskal(alpha_KRUSKAL=self.KRUSKAL_alpha)

					if all([self.LC_alpha != None, self.NLC_alpha != None]):
						self.analyzer.create_stat_analysis(alpha_LC = self.LC_alpha, alpha_NLC = self.NLC_alpha)

					#if all([self.MT_alpha != None, self.UT_alpha !=None]):
						#self.analyzer.create_mt_stat_test(alpha_tt = 0.01, alpha_ut = 0.01)
			
			except AttributeError:
				pass
			
			try:
				if self.user_defined_analysis_check.isChecked():
				#if all([self.BOB_avg != None, self.WOW_avg != None, self.BOB_prop != None, self.WOW_prop != None, self.chamber_weight != None, self.step_weight != None, self.mode != None]):
					self.analyzer.create_user_defined_analysis(self.BOB_avg, self.WOW_avg, self.BOB_prop, self.WOW_prop, self.chamber_weight, self.step_weight, self.mode)
			except AttributeError as e:
				print(e)
			self.analyzer.create_chamber_info()
		elif self.user_defined_analysis == 'Lot-based Analysis':
			self.analyzer = LOT_Analysis(self.preprocessing_con)
			try:
				if all([self.KS_alpha != None, self.ANOVA_alpha != None, self.KRUSKAL_alpha != None]):
					self.analyzer.create_KS_test(alpha_normality=self.KS_alpha)
					self.analyzer.create_ANOVA(alpha_ANOVA = self.ANOVA_alpha, alpha_KRUSKAL=self.KRUSKAL_alpha)
					#self.analyzer.create_Kruskal(alpha_KRUSKAL=self.KRUSKAL_alpha)

					if all([self.LC_alpha != None, self.NLC_alpha != None]):
						self.analyzer.create_stat_analysis(alpha_LC = self.LC_alpha, alpha_NLC = self.NLC_alpha)

					#if all([self.MT_alpha != None, self.UT_alpha !=None]):
						#self.analyzer.create_mt_stat_test(alpha_tt = 0.01, alpha_ut = 0.01)
			
			except AttributeError:
				pass

			try:
				if self.user_defined_analysis_check.isChecked():
				#if all([self.BOB_avg != None, self.WOW_avg != None, self.BOB_prop != None, self.WOW_prop != None, self.chamber_weight != None, self.step_weight != None, self.mode != None]):
					self.analyzer.create_user_defined_analysis(self.BOB_avg, self.WOW_avg, self.BOB_prop, self.WOW_prop, self.chamber_weight, self.step_weight, self.mode)
			except AttributeError:
				pass
			self.analyzer.create_eqp_info()

		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_dummy_combobox(self):
		self.dummy_option = str(self.dummy_combobox.currentIndex())

	def show_visualization(self):
		self.visualization_window = Visualization(self.svg_name, self.model.states, self.model.transitions, self)
		self.visualization_window.closed.connect(self.show)
		self.visualization_window.show()
		self.hide()

	def forward_visualization_tab(self):
		self.model = Model(analysis = self.user_defined_analysis, con=self.preprocessing_con)


		if int(self.dummy_option) == 0:
			self.model.create_prod_info_all_dummy(representation = self.user_defined_representation_option, type = self.user_defined_type_option, mode = self.analysis_mode)
			self.model.create_transitions_and_states(mode = self.analysis_mode)
			print("option 1")

		if int(self.dummy_option) == 1:
			self.model.create_prod_info_from_dummy(representation = self.user_defined_representation_option, type = self.user_defined_type_option, mode = self.analysis_mode)
			self.model.create_transitions_and_states(mode = self.analysis_mode)
			print("option 2")
		if int(self.dummy_option) == 2:
			self.model.create_prod_info_to_dummy(representation = self.user_defined_representation_option, type = self.user_defined_type_option, mode = self.analysis_mode)
			self.model.create_transitions_and_states(mode = self.analysis_mode)
			print("option 3")

		machine = Graph(self.model.num_wafer_chamber_step, states=self.model.states, transitions=self.model.transitions)
		self.svg_name = 'svg_' + str(time.time())
		machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')

		def create_result_table():
			drop_table_sql = """
				DROP TABLE IF EXISTS result;
			"""
			#
			create_table_sql = """
			CREATE TABLE IF NOT EXISTS result (
				Raw_data_name text,
				User_name text,
				Spec text,
				Analysis text,
				Incomplete_wafer text,
				Wafer_count integer,
				Step_criterion integer,
				Period text,
				Main text,
				Representation text,
				Type text,
				horizon integer,
				Filter text,
				Mean_criterion text,
				Std_criterion text,
				Value_criterion text,
				KS_alpha integer,
				ANOVA_alpha integer,
				KRUSKAL_alpha integer,
				LC_alpha integer,
				NLC_alpha integer,
				MT_alpha integer,
				MU_alpha integer,
				BOB_avg integer,
				WOW_avg integer,
				BOB_prop integer,
				WOW_prop integer,
				Machine_weight integer,
				Step_weight integer,
				UD_mode text,
				SVG_name text

				);
			"""
			c = self.con.cursor()
			#c.execute(drop_table_sql)
			c.execute(create_table_sql)

		def insert_value(row):
			sql = """
				INSERT INTO result(Raw_data_name, User_name, Spec, Analysis, Incomplete_wafer, Wafer_count, Step_criterion, Period, Main, Representation, Type, horizon, Filter, Mean_criterion, Std_criterion,Value_criterion, KS_alpha, ANOVA_alpha, KRUSKAL_alpha, LC_alpha, NLC_alpha, MT_alpha, MU_alpha, BOB_avg, WOW_avg, BOB_prop, WOW_prop, Machine_weight, Step_weight, UD_mode, SVG_name)
				VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
			"""
			cur = self.con.cursor()
			cur.execute(sql, row)
			print("CREATED!")
			return cur.lastrowid

		def add_to_preprocess_db():
			create_result_table()
			
			with self.con:
				row = (self.user_defined_input_name, self.user_defined_user_name,self.user_defined_user_info, self.user_defined_analysis, self.user_defined_Incomplete_wafer, self.user_defined_min_num, self.step_criterion, self.period_text, self.main_text, self.user_defined_representation_option, self.user_defined_type_option, self.user_defined_horizon_option, self.user_defined_filter_option, '{}: {},{}'.format(self.user_defined_mean_criterion_option, self.mean_BOB_criterion, self.mean_WOW_criterion), '{}: {}'.format(self.user_defined_std_criterion_option, self.std_criterion), '{}: {},{}'.format(self.user_defined_value_criterion_option, self.value_BOB_criterion, self.value_WOW_criterion), self.KS_alpha, self.ANOVA_alpha, self.KRUSKAL_alpha, self.LC_alpha, self.NLC_alpha, self.MT_alpha, self.UT_alpha, self.BOB_avg, self.WOW_avg, self.BOB_prop,self.WOW_prop, self.chamber_weight, self.step_weight, self.mode, self.svg_name)
				insert_value(row)

		add_to_preprocess_db()
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




class Interval_Dialog(QtWidgets.QDialog, interval_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.days_lineEdit.textChanged.connect(self.get_inc_days)
		self.start_step_lineEdit.textChanged.connect(self.handle_start_step_lineEdit)
		self.end_step_lineEdit.textChanged.connect(self.handle_end_step_lineEdit)
		self.interval_push.clicked.connect(self.close_dialog)
	
	def get_inc_days(self):
		self.inc_days = int(self.days_lineEdit.text())

	def handle_start_step_lineEdit(self):
		self.start_step = self.start_step_lineEdit.text()

	def handle_end_step_lineEdit(self):
		self.end_step = self.end_step_lineEdit.text()

	def close_dialog(self):
		self.accept()

class Mean_Criterion_Dialog(QtWidgets.QDialog, mean_criterion_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.mean_BOB_lineEdit.textChanged.connect(self.handle_mean_BOB_lineEdit)
		self.mean_WOW_lineEdit.textChanged.connect(self.handle_mean_WOW_lineEdit)
		self.mean_push.clicked.connect(self.close_dialog)

	def handle_mean_BOB_lineEdit(self):
		self.mean_BOB_criterion = self.mean_BOB_lineEdit.text()

	def handle_mean_WOW_lineEdit(self):
		self.mean_WOW_criterion = self.mean_WOW_lineEdit.text()

	def close_dialog(self):
		self.accept()

class Std_Criterion_Dialog(QtWidgets.QDialog, std_criterion_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.std_lineEdit.textChanged.connect(self.handle_std_lineEdit)
		self.std_push.clicked.connect(self.close_dialog)

	def handle_std_lineEdit(self):
		self.std_criterion = self.std_lineEdit.text()

	def close_dialog(self):
		self.accept()

class Value_Criterion_Dialog(QtWidgets.QDialog, value_criterion_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.value_BOB_lineEdit.textChanged.connect(self.handle_value_BOB_lineEdit)
		self.value_WOW_lineEdit.textChanged.connect(self.handle_value_WOW_lineEdit)
		self.value_push.clicked.connect(self.close_dialog)

	def handle_value_BOB_lineEdit(self):
		self.value_BOB_criterion = self.value_BOB_lineEdit.text()

	def handle_value_WOW_lineEdit(self):
		self.value_WOW_criterion = self.value_WOW_lineEdit.text()

	def close_dialog(self):
		self.accept()

class Stat_Parameters_Dialog(QtWidgets.QDialog, stat_parameters_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.KS_alpha = 0.05
		self.ANOVA_alpha = 0.05
		self.KRUSKAL_alpha = 0.05
		self.LC_alpha = 0.05
		self.NLC_alpha = 0.05
		self.MT_alpha = 0.05
		self.UT_alpha = 0.05
		self.KS_alpha_lineEdit.textChanged.connect(self.handle_KS_alpha_lineEdit)
		self.ANOVA_alpha_lineEdit.textChanged.connect(self.handle_ANOVA_alpha_lineEdit)
		self.KRUSKAL_alpha_lineEdit.textChanged.connect(self.handle_KRUSKAL_alpha_lineEdit)
		self.LC_alpha_lineEdit.textChanged.connect(self.handle_LC_alpha_lineEdit)
		self.NLC_alpha_lineEdit.textChanged.connect(self.handle_NLC_alpha_lineEdit)
		self.MT_alpha_lineEdit.textChanged.connect(self.handle_MT_alpha_lineEdit)
		self.UT_alpha_lineEdit.textChanged.connect(self.handle_UT_alpha_lineEdit)
		self.stat_push.clicked.connect(self.close_dialog)

	def handle_KS_alpha_lineEdit(self):
		self.KS_alpha = self.KS_alpha_lineEdit.text()

	def handle_ANOVA_alpha_lineEdit(self):
		self.ANOVA_alpha = self.ANOVA_alpha_lineEdit.text()

	def handle_KRUSKAL_alpha_lineEdit(self):
		self.KRUSKAL_alpha = self.KRUSKAL_alpha_lineEdit.text()

	def handle_LC_alpha_lineEdit(self):
		self.LC_alpha = self.LC_alpha_lineEdit.text()

	def handle_NLC_alpha_lineEdit(self):
		self.NLC_alpha = self.NLC_alpha_lineEdit.text()

	def handle_MT_alpha_lineEdit(self):
		self.MT_alpha = self.MT_alpha_lineEdit.text()

	def handle_UT_alpha_lineEdit(self):
		self.UT_alpha = self.UT_alpha_lineEdit.text()

	def close_dialog(self):
		self.accept()

class User_Defined_Analysis_Dialog(QtWidgets.QDialog, user_defined_analysis_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)
		self.show()
		self.machine_weight = 0.5
		self.step_weight = 0.5
		self.BOB_avg_lineEdit.textChanged.connect(self.handle_BOB_avg_lineEdit)
		self.WOW_avg_lineEdit.textChanged.connect(self.handle_WOW_avg_lineEdit)
		self.BOB_prop_lineEdit.textChanged.connect(self.handle_BOB_prop_lineEdit)
		self.WOW_prop_lineEdit.textChanged.connect(self.handle_WOW_prop_lineEdit)
		self.machine_weight_lineEdit.textChanged.connect(self.handle_machine_weight_lineEdit)
		self.step_weight_lineEdit.textChanged.connect(self.handle_step_weight_lineEdit)
		self.mode_lineEdit.textChanged.connect(self.handle_mode_lineEdit)
		self.UDA_push.clicked.connect(self.close_dialog)

	def handle_BOB_avg_lineEdit(self):
		self.BOB_avg = self.BOB_avg_lineEdit.text()

	def handle_WOW_avg_lineEdit(self):
		self.WOW_avg = self.WOW_avg_lineEdit.text()

	def handle_BOB_prop_lineEdit(self):
		self.BOB_prop = self.BOB_prop_lineEdit.text()

	def handle_WOW_prop_lineEdit(self):
		self.WOW_prop = self.WOW_prop_lineEdit.text()

	def handle_step_weight_lineEdit(self):
		self.step_weight = self.step_weight_lineEdit.text()

	def handle_machine_weight_lineEdit(self):
		self.machine_weight = self.machine_weight_lineEdit.text()

	def handle_mode_lineEdit(self):
		self.mode = self.mode_lineEdit.text()

	def close_dialog(self):
		self.accept()

class Progress_Dialog(QtWidgets.QDialog, progress_dialog.Ui_Dialog):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)