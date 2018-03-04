from PyQt5 import QtGui  # Import the PyQt4 module we'll need
from PyQt5 import QtWidgets, QtCore
import sys  # We need sys so that we can pass argv to QApplication

import mainwindow  # This file holds our MainWindow and all design related things
import data_input
from after_preprocessing import After_Preprocessing
from with_result import With_Result
import interval_dialog
import mean_criterion_dialog, std_criterion_dialog, value_criterion_dialog, stat_parameters_dialog, user_defined_analysis_dialog, progress_dialog
# it also keeps events etc that we defined in Qt Designer
import sys, signal, os  # For listing directory methods

sys.path.append('../')
from Preprocessing import Preprocessing
from Classifier import Classifier
from LOT_Classifier import LOT_Classifier
from Dummy import Analysis
from LOT_Dummy import LOT_Analysis
from Model import Model
from diagrams import Graph
import sqlite3
from visualization_widget import Visualization
import time
import numpy as np
class Main(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.raw_analysis_push.clicked.connect(self.handle_raw_analysis_push)
        self.data_input_window = None
        self.preprocessed_analysis_push.clicked.connect(self.handle_preprocessed_analysis_push)
        self.after_preprocessing_window = None
        self.result_push.clicked.connect(self.handle_result_push)
        #self.btnBrowse.clicked.connect(self.browse_folder)  # When the button is pressed
        # Execute browse_folder function

    def handle_raw_analysis_push(self):
    	#if self.data_input_window is None:
    	self.data_input_window = Data_Input()
    	self.data_input_window.show()

    def handle_preprocessed_analysis_push(self):
    	self.after_preprocessing_window = After_Preprocessing()
    	self.after_preprocessing_window.show()

    def handle_result_push(self):
    	self.with_reuslt_window = With_Result()
    	self.with_reuslt_window.show()

class Data_Input(QtWidgets.QWidget, data_input.Ui_Form):
	def __init__(self, parent=None):
		super(self.__class__, self).__init__(parent)
		self.setupUi(self)

		#Data input
		self.file_push.clicked.connect(self.selectFile)
		self.user_defined_input_name = None
		self.input_lineEdit.textChanged.connect(self.handle_inputname_lineEdit)
		self.user_defined_user_name = 'User_'+''.join(str(e) for e in list(time.localtime()))
		self.username_lineEdit.textChanged.connect(self.handle_username_lineEdit)
		self.user_defined_user_info = None
		self.userinfo_lineEdit.textChanged.connect(self.handle_userinfo_lineEdit)
		self.user_defined_analysis = 'Wafer-based Analysis'
		self.analysis_combobox.activated.connect(self.handle_analysis_combobox)
		self.next_push.clicked.connect(self.forward_input_tab)

		#Preprocessing 1
		self.Incomplete = False
		self.minimum_wafer = False
		self.user_defined_start_step= None
		self.user_defined_end_step= None
		self.Incomplete_checkbox.stateChanged.connect(self.handle_Incomplete_checkbox)
		#self.user_defined_start_step = 'S001'
		#self.user_defined_end_step = 'S075'
		self.start_lineEdit.textChanged.connect(self.handle_start_lineEdit)
		self.end_lineEdit.textChanged.connect(self.handle_end_lineEdit)
		self.minimum_wafer_checkbox.stateChanged.connect(self.handle_minimum_wafer_checkbox)
		self.user_defined_min_num = 23
		self.min_num_lineEdit.textChanged.connect(self.handle_min_num_lineEdit)
		self.next_push_2.clicked.connect(self.forward_preprocess1_tab)

		#Preprocessing 2
		self.period = False
		self.main = False
		self.start_end_optimal_period_check.stateChanged.connect(self.handle_start_end_optimal_period_check)
		self.period_text = None
		self.step_criterion = 80
		self.step_criterion_lineEdit.textChanged.connect(self.handle_step_criterion_lineEdit)
		#self.period_text ="S001, 2016-11-19, 2016-12-03; S041, 2017-01-17, 2017-01-27; S048, 2017-01-24, 2017-02-06; S065, 2017-02-03, 2017-02-17; S075, 2017-02-14, 2017-02-28"
		#S000038; S000039; S000040; S000041; S000042; S000043; S000044; S000047; S000048;
		self.period_lineEdit.textChanged.connect(self.handle_period_lineEdit)
		self.period_checkbox.stateChanged.connect(self.handle_period_checkbox)
		self.main_text = None
		self.main_lineEdit.textChanged.connect(self.handle_main_lineEdit)
		#self.main_text = "S038; S039; S040; S041; S042; S043; S044; S047; S048; S049; S050; S051; S052; S053; S054; S055; S057; S059; S061; S062; S063; S064; S065; S066; S069; S070; S074; S075"
		self.main_checkbox.stateChanged.connect(self.handle_main_checkbox)
		self.user_defined_user_info = None
		self.next_push_3.clicked.connect(self.forward_preprocess2_tab)

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
		self.machine_weight = None
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

		

	def selectFile(self):
		self.filename = QtWidgets.QFileDialog.getOpenFileName()[0]
		self.filename_lineEdit.setText(self.filename)

	def handle_inputname_lineEdit(self):
		self.user_defined_input_name = self.input_lineEdit.text()

	def handle_username_lineEdit(self):
		self.user_defined_user_name = self.username_lineEdit.text()

	def handle_userinfo_lineEdit(self):
		self.user_defined_user_info = self.userinfo_lineEdit.text()

	def handle_analysis_combobox(self):
		self.user_defined_analysis = str(self.analysis_combobox.currentText())
		print(self.user_defined_analysis)
		

	def forward_input_tab(self):
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
		self.preprocessing = Preprocessing(self.filename)
		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def backward(self):
		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()-1)

	def handle_Incomplete_checkbox(self):
		if self.Incomplete_checkbox.isChecked():
			self.Incomplete = True
		else:
			self.Incomplete = False

	def handle_start_lineEdit(self):
		self.user_defined_start_step = self.start_lineEdit.text()

	def handle_end_lineEdit(self):
		self.user_defined_end_step = self.end_lineEdit.text()

	def handle_minimum_wafer_checkbox(self):
		if self.minimum_wafer_checkbox.isChecked():
			self.minimum_wafer = True
		else:
			self.minimum_wafer = False
			

	def handle_min_num_lineEdit(self):
		self.user_defined_min_num = int(self.min_num_lineEdit.text())

	def forward_preprocess1_tab(self):
		if self.Incomplete == True:
			try:
				self.preprocessing.Incomplete_wafer(self.preprocessing.data, self.user_defined_start_step, self.user_defined_end_step)
			except AttributeError:
				pass
		if self.minimum_wafer == True:
			try:
				self.preprocessing.wafer_count(self.preprocessing.data, self.user_defined_min_num)
			except AttributeError:
				pass
		"""
		if self.Incomplete == True & hasattr(self, 'user_defined_start_step') & hasattr(self, 'user_defined_end_step'):
			self.preprocessing.Incomplete_wafer(self.preprocessing.data, self.user_defined_start_step, self.user_defined_end_step)
		if self.minimum_wafer == True & hasattr(self, 'user_defined_min_num'):
			self.preprocessing.wafer_count(self.preprocessing.data, self.user_defined_min_num)
		"""
		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_step_criterion_lineEdit(self):
		try:
			self.step_criterion = int(self.step_criterion_lineEdit.text())
		except ValueError:
			pass

	def handle_start_end_optimal_period_check(self):
		if self.start_end_optimal_period_check.isChecked():
			self.interval_dialog_window = Interval_Dialog()
			#self.interval_dialog_window.show()
			#self.interval_dialog_window.get_inc_days()
			if self.interval_dialog_window.exec_():
				inc_days = self.interval_dialog_window.inc_days
				start_step = self.interval_dialog_window.start_step
				end_step = self.interval_dialog_window.end_step
			start_b, start_f, end_b, end_f = self.preprocessing.recommend_period(self.preprocessing.data, start_step, end_step, inc_days)
			self.period_lineEdit.setText("{}, {}, {}; {}, {}, {};".format(start_step, start_b, start_f, end_step, end_b, end_f))
		else:
			self.period_lineEdit.setText("")

	def handle_period_checkbox(self):
		if self.period_checkbox.isChecked():
			self.period = True
		else:
			self.period = False

	def handle_main_checkbox(self):
		if self.main_checkbox.isChecked():
			self.main = True
		else:
			self.main = False

	def handle_period_lineEdit(self):
		self.period_text = self.period_lineEdit.text()

	def handle_main_lineEdit(self):
		self.main_text = self.main_lineEdit.text()

	def forward_preprocess2_tab(self):
		if self.period == True:
			try:
				steps = self.period_text.split(';')
				periods = {}
				for step in steps:
				    if step != "":
				        step_list = [x.strip() for x in step.split(',')]
				        periods[step_list[0]] = [step_list[1], step_list[2]]
				
				self.preprocessing.period(self.preprocessing.data, periods = periods)
			except AttributeError:
				pass
		if self.main == True:
			try:
				main_steps = [x.strip() for x in self.main_text.split(';')]
				
				self.preprocessing.main(self.preprocessing.data, steps = main_steps)
			except AttributeError:
				pass
		if self.user_defined_analysis == 'Lot-based Analysis':
			self.preprocessing.diff_step_flow(self.preprocessing.data)
			self.preprocessing.diff_eqp_flow(self.preprocessing.data)
		self.preprocessing.data.to_sql("preprocessed_data", self.preprocessing.con, if_exists="replace")
		self.preprocessing_con = self.preprocessing.con


		def add_to_preprocess_db():
			connect_to_db()
			create_preprocessed_table()
			
			with self.con:
				row = (self.user_defined_input_name, self.user_defined_user_name,self.user_defined_user_info, self.user_defined_analysis, '{}:{}'.format(self.user_defined_start_step, self.user_defined_end_step), self.user_defined_min_num, self.step_criterion, self.period_text, self.main_text, self.preprocessing.TARGET_FILE)
				insert_value(row)


		def connect_to_db():
			self.BASE_DIR   =  os.path.abspath('.')
			#self.TARGET_FILE = '{}.db'.format('DB_' + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
			db_name = 'PREPROCESSING'
			self.TARGET_FILE = '{}.db'.format(db_name)
			self.TARGET_FILE_FULL_PATH = os.path.join(self.BASE_DIR, self.TARGET_FILE)
			self.con = sqlite3.connect(self.TARGET_FILE_FULL_PATH)

		def create_preprocessed_table():
			drop_table_sql = """
				DROP TABLE IF EXISTS processed_dataset;
			"""
			create_table_sql = """
			CREATE TABLE IF NOT EXISTS processed_dataset (
				Raw_data_name text,
				User_name text,
				Spec text,
				Analysis text,
				Incomplete_wafer text,
				Wafer_count integer,
				Step_criterion integer,
				Period text,
				Main text,
				DB_name text
				);
			"""
			c = self.con.cursor()
			#c.execute(drop_table_sql)
			c.execute(create_table_sql)

		def insert_value(row):
			sql = """
				INSERT INTO processed_dataset(Raw_data_name, User_name, Spec, Analysis, Incomplete_wafer, Wafer_count, Step_criterion,Period, Main, DB_name)
				VALUES(?,?,?,?,?,?,?,?,?,?)
			"""
			cur = self.con.cursor()
			cur.execute(sql, row)
			print("CREATED!")
			return cur.lastrowid

		add_to_preprocess_db()
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
			self.classifier = Classifier(self.preprocessing.data)
			self.classifier.create_wafer_data(user_defined_ratio=self.step_criterion*0.01, horizon = int(self.user_defined_horizon_option))
			self.classifier.wafer_data.to_sql("wafer_data", self.preprocessing.con, if_exists="replace")

		elif self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			self.classifier = Classifier(self.preprocessing.data)

			self.classifier.create_raw_lot_data()

		elif self.user_defined_analysis == 'Lot-based Analysis':
			self.classifier = LOT_Classifier(self.preprocessing.data)

			self.classifier.create_raw_lot_data()
			self.classifier.create_lot_data(horizon=int(self.user_defined_horizon_option))
			self.classifier.lot_data.to_sql("lot_data", self.preprocessing.con, if_exists="replace", index = False)

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
				self.classifier.absolute_value_mean_criterion(BOB_mean_abs_criterion = self.value_BOB_criterion, WOW_mean_abs_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.value_BOB_criterion, WOW_n = self.value_WOW_criterion)
			self.classifier.create_wafer_BOB_WOW_group()
			self.classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", self.preprocessing.con, if_exists="replace")
			self.classifier.create_chamber_perf()
			self.classifier.chamber_perf.to_sql("chamber_perf", self.preprocessing.con, if_exists="replace")

		elif self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			if self.user_defined_std_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_std_criterion(std_rela_criteiron = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Absolute Value':
				self.classifier.absolute_value_std_criterion(std_abs_criterion = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Rank-based':
				self.classifier.rank_based_std_criterion(self, n = self.std_criterion)
			self.classifier.extract_deviated_lot()

			self.classifier.create_wafer_data(user_defined_ratio=self.step_criterion*0.01, horizon = int(self.user_defined_horizon_option))
			self.classifier.wafer_data.to_sql("wafer_data", self.preprocessing.con, if_exists="replace")

			if self.user_defined_value_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = self.value_BOB_criterion, WOW_mean_rela_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Absolute Value':
				self.classifier.absolute_value_mean_criterion(BOB_mean_abs_criterion = self.value_BOB_criterion, WOW_mean_abs_criterion = self.value_WOW_criterion)
			elif self.user_defined_value_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.value_BOB_criterion, WOW_n = self.value_WOW_criterion)

			self.classifier.create_wafer_BOB_WOW_group()
			self.classifier.wafer_BOB_WOW_Group.to_sql("wafer_BOB_WOW_Group", self.preprocessing.con, if_exists="replace")

			self.classifier.create_chamber_perf()
			self.classifier.chamber_perf.to_sql("chamber_perf", self.preprocessing.con, if_exists="replace")

		elif self.user_defined_analysis == 'Lot-based Analysis':

			if self.user_defined_std_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_std_criterion(std_rela_criteiron = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Absolute Value':
				self.classifier.absolute_value_std_criterion(std_abs_criterion = self.std_criterion)
			elif self.user_defined_std_criterion_option == 'Rank-based':
				self.classifier.rank_based_std_criterion(self, n = self.std_criterion)

			if self.user_defined_mean_criterion_option == 'Relative Ratio':
				self.classifier.relative_ratio_mean_criterion(BOB_mean_rela_criterion = self.mean_BOB_criterion, WOW_mean_rela_criterion = self.mean_WOW_criterion)
			elif self.user_defined_mean_criterion_option == 'Absolute Value':
				self.classifier.absolute_value_mean_criterion(BOB_mean_abs_criterion = self.mean_BOB_criterion, WOW_mean_abs_criterion = self.mean_WOW_criterion)
			elif self.user_defined_mean_criterion_option == 'Rank-based':
				self.classifier.rank_based_mean_criterion(BOB_n = self.mean_BOB_criterion, WOW_n = self.mean_WOW_criterion)
			
			self.classifier.create_lot_BOB_WOW_group()
			self.classifier.lot_BOB_WOW_Group.to_sql("lot_BOB_WOW_Group", self.preprocessing.con, if_exists="replace", index = False)

			self.classifier.create_eqp_perf()
			self.classifier.eqp_perf.to_sql("eqp_perf", self.preprocessing.con, if_exists="replace")
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
				except AttributeError:
					pass
				try:
					self.WOW_prop = float(self.user_defined_analysis_dialog_window.WOW_prop)
				except AttributeError:
					pass
				self.step_weight = float(self.user_defined_analysis_dialog_window.step_weight)
				self.machine_weight = float(self.user_defined_analysis_dialog_window.machine_weight)
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
			self.machine_weight = None
			self.mode = None

	def handle_and_checkbox(self):
		if self.and_check.isChecked():
			self.analysis_mode = 'and'
		else:
			self.analysis_mode = 'or'

	def forward_high_low_tab(self):
		if self.user_defined_analysis == 'Wafer-based Analysis' or self.user_defined_analysis == 'Wafer-based Analysis on specific Lot':
			self.analyzer = Analysis(self.preprocessing.con)
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
				#if all([self.BOB_avg != None, self.WOW_avg != None, self.BOB_prop != None, self.WOW_prop != None, self.machine_weight != None, self.step_weight != None, self.mode != None]):
					self.analyzer.create_user_defined_analysis(self.BOB_avg, self.WOW_avg, self.BOB_prop, self.WOW_prop, self.machine_weight, self.step_weight, self.mode)
			except AttributeError as e:
				print(e)
			self.analyzer.create_chamber_info()
		elif self.user_defined_analysis == 'Lot-based Analysis':
			self.analyzer = LOT_Analysis(self.preprocessing.con)
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
				#if all([self.BOB_avg != None, self.WOW_avg != None, self.BOB_prop != None, self.WOW_prop != None, self.machine_weight != None, self.step_weight != None, self.mode != None]):
					self.analyzer.create_user_defined_analysis(self.BOB_avg, self.WOW_avg, self.BOB_prop, self.WOW_prop, self.machine_weight, self.step_weight, self.mode)
			except AttributeError as e:
				print(e)
			self.analyzer.create_eqp_info()

		self.tabWidget.setCurrentIndex(self.tabWidget.currentIndex()+1)

	def handle_dummy_combobox(self):
		self.dummy_option = str(self.dummy_combobox.currentIndex())

	def show_visualization(self):
		self.model.states 


		self.visualization_window = Visualization(self.svg_name, self.model.states, self.model.transitions, self)
		self.visualization_window.closed.connect(self.show)
		self.visualization_window.show()
		self.hide()

	def forward_visualization_tab(self):
		self.model = Model(analysis = self.user_defined_analysis, con = self.preprocessing.con)


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
				row = (self.user_defined_input_name, self.user_defined_user_name,self.user_defined_user_info, self.user_defined_analysis, '{}:{}'.format(self.user_defined_start_step, self.user_defined_end_step), self.user_defined_min_num, self.step_criterion, self.period_text, self.main_text, self.user_defined_representation_option, self.user_defined_type_option, self.user_defined_horizon_option, self.user_defined_filter_option, '{}: {},{}'.format(self.user_defined_mean_criterion_option, self.mean_BOB_criterion, self.mean_WOW_criterion), '{}: {}'.format(self.user_defined_std_criterion_option, self.std_criterion), '{}: {},{}'.format(self.user_defined_value_criterion_option, self.value_BOB_criterion, self.value_WOW_criterion), self.KS_alpha, self.ANOVA_alpha, self.KRUSKAL_alpha, self.LC_alpha, self.NLC_alpha, self.MT_alpha, self.UT_alpha, self.BOB_avg, self.WOW_avg, self.BOB_prop,self.WOW_prop, self.machine_weight, self.step_weight, self.mode, self.svg_name)
				insert_value(row)

		add_to_preprocess_db()
		self.show_visualization()




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



def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = Main()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function