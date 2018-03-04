

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets
import sys, signal, os
from argparse import ArgumentParser
from random import uniform
import time
sys.path.append('../')
from diagrams import Graph, Single_path_Graph
from qrangeslider import QRangeSlider
import pandas as pd
import numpy as np
s=1.0/1.0e10

def m(i):
    return float(i)*s+uniform(-1,1)


DEFAULT_CSS = """
QSlider * {
    border: 0px;
    padding: 0px;
}
QSlider #Head {
    background: #222;
}
QSlider #Span {
    background: #393;
}
QSlider #Span:active {
    background: #282;
}
QSlider #Tail {
    background: #222;
}
QSlider > QSplitter::handle {
    background: #393;
}
QSlider > QSplitter::handle:vertical {
    height: 4px;
}
QSlider > QSplitter::handle:pressed {
    background: #ca5;
}

"""


class SvgWidget(QtSvg.QSvgWidget):
    location_changed = QtCore.pyqtSignal(QtCore.QPointF)
    
    def updateViewBox(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QtCore.QRectF(self.center_x - w/2, self.center_y - h/2,
                         w, h)
        self.renderer().setViewBox(r)
        
    def center(self):
        self.scale=max(float(self.defViewBox.width())/self.width(),
                       float(self.defViewBox.height())/self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center() .y()
        self.updateViewBox(self.size())
        self.repaint()
        
    def reload(self, path=None):
        QtSvg.QSvgWidget.load(self, self.path)
        self.defViewBox = self.renderer().viewBoxF()
        self.updateViewBox(self.size())
        
    def resizeEvent(self, evt):
        self.updateViewBox( evt.size())
        QtSvg.QSvgWidget.resizeEvent(self, evt)
        
    def __init__(self, path):
        QtSvg.QSvgWidget.__init__(self)
        self.path = path
        self.watch = QtCore.QFileSystemWatcher(self)
        self.watch.addPath(self.path)
        self.watch.fileChanged.connect(self.reload)

        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.setPalette( QtGui.QPalette( QtCore.Qt.white ) );
        self.setAutoFillBackground(True)
        QtSvg.QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()
        #self.setAcceptsHoverEvents(True)

    def updateLocation(self, pos):
        self.location_changed.emit(QtCore.QPointF(
                (pos.x() - self.width()/2)*self.scale + self.center_x, 
                (pos.y() - self.height()/2)*self.scale + self.center_y))

    def wheelEvent(self, evt):      
        dx = evt.pos().x() - self.width()/2
        dy = evt.pos().y() - self.height()/2
        center_x = self.center_x + dx*self.scale
        center_y = self.center_y + dy*self.scale
        self.scale = self.scale * 1.0025**(evt.angleDelta().y());
        self.center_x = center_x - dx*self.scale
        self.center_y = center_y - dy*self.scale
        
        
        self.updateViewBox(self.size())
        self.updateLocation(evt.pos())
        self.repaint()

    def mousePressEvent(self, evt):
        self.ds = evt.localPos()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y
        
    def mouseMoveEvent(self, evt):
        self.updateLocation(evt.localPos())
        if not self.ds: return
        dx = evt.localPos().x() - self.ds.x()
        dy = evt.localPos().y() - self.ds.y()
        self.center_x = self.start_center_x - dx*self.scale
        self.center_y = self.start_center_y - dy*self.scale
        self.updateViewBox(self.size())
        self.repaint()

    def mouseReleaseEvent(self, evt):
        self.mouseMoveEvent(evt)
        self.ds = None

def tr(s):
    return QtWidgets.QApplication.translate("SvgViewer", s, None, QtWidgets.QApplication.UnicodeUTF8)

class Visualization(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()
    def showLocation(self, point):
        self.statusbar.showMessage("%f %f"%(point.x(), point.y()))

    def load(self, path):
        view = SvgWidget(path)
        #view.location_changed.connect(self.showLocation)
        self.tabs.setCurrentIndex( self.tabs.addTab(view, os.path.basename("%s"%path)))
        
    def closeTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.removeTab(self.tabs.currentIndex())

    def center(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().center()

    def reload(self):
        if not self.tabs.currentWidget(): return
        self.tabs.currentWidget().reload()

    def nextTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() + 1)%self.tabs.count());
 
    def prevTab(self):
        if not self.tabs.currentWidget(): return
        self.tabs.setCurrentIndex( (self.tabs.currentIndex() - 1)%self.tabs.count());

    def open(self):
        path = QtGui.QFileDialog.getOpenFileName(
            self, "Open File", filter=tr("Svg documents (*.svg);;Any files (*.*)"))
        if path: self.load(path)

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

    def create_transitions_and_states(self, threshold):
        #Raw한 prod_temp는 계속 DB에 유지
        self.prod_temp = pd.read_sql_query("select * from prod_temp;", self.parent.preprocessing_con)
        print(self.step_perf)
        
        index = int(len(self.step_perf) * threshold * 0.01)
        print("index: {}".format(index))
        #프린트 해야함
        self.valid_step = list(self.step_perf.loc[:index,'STEP_SEQ_'])
        self.valid_step.append('START')
        self.valid_step.append('END')
        print("valid step: {}".format(self.valid_step))

        #threshold값이 100이면 only dummy step도 시각화
        if threshold != 100:
            dummy_step = self.step_perf.loc[self.step_perf['count'] == 1, 'machine']
            print("len of prod_temp before removing only dummy step: {}".format(len(self.prod_temp)))
            self.prod_temp = self.prod_temp.loc[np.logical_not(self.prod_temp.STEP_SEQ.isin(self.step_perf.loc[self.step_perf['count'] == 1, 'STEP_SEQ_'])), : ]
            print("len of prod_temp after removing only dummy step: {}".format(len(self.prod_temp)))

        print("len of prod_temp before applying threshold: {}".format(len(self.prod_temp)))
        self.prod_temp = self.prod_temp.loc[self.prod_temp.STEP_SEQ.isin(self.valid_step), : ]
        print("len of prod_temp after applying threshold: {}".format(len(self.prod_temp)))
        self.valid_step.remove('START')
        self.valid_step.remove('END')
        self.prod_temp.to_csv('../result/prod_temp.csv', sep = ',', index = False)
        case_id = 'nothing'
        to = 'nothing'
        for row in self.prod_temp.itertuples():
            if case_id == row.CASE_ID:
                if to != row.FROM:
                    self.prod_temp.set_value(row.Index,'FROM', to)
                    #row['FROM'] = to
                to = row.TO
            else:
                case_id = row.CASE_ID
                if row.FROM != 'START':
                    self.prod_temp.set_value(row.Index,'FROM', 'START')
                    #START는 BOB/WOW 값을 가지면 안됨
                    self.prod_temp.set_value(row.Index,'BOB', '0')
                    self.prod_temp.set_value(row.Index,'WOW', '0')
                    #row['FROM'] = 'START'
                to = row.TO
            #print(to)

        self.prod_trans = self.prod_temp.groupby(['FROM', 'TO']).agg([np.count_nonzero, np.mean, np.std])
        def extract_step(x):
            if x == 'END':
                return x
            else:
                return x.split("_")[0].strip()
        prod_trans_temp = self.prod_trans.copy()
        prod_trans_temp.reset_index(inplace=True)
        prod_trans_temp.columns = ['_'.join(col).strip() for col in prod_trans_temp.columns.values]
        prod_trans_temp['STEP_SEQ_'] = prod_trans_temp['TO_'].apply(extract_step)

        #step 내 설비별 wafer 빈도
        unique_steps = list(set(prod_trans_temp['STEP_SEQ_'].tolist()))

        num_wafer_chamber_step = {}
        for step in unique_steps:
            num_wafer = prod_trans_temp.loc[prod_trans_temp['STEP_SEQ_'] == step, "VALUE_count_nonzero"]
            num_wafer.sort_values(ascending = False, inplace = True)
            idx = (len(num_wafer)-1) * self.edge_threshold * 0.01
            idx = int(idx + 0.5)

            num_wafer_chamber_step[step] = num_wafer.iloc[idx]
        self.num_wafer_chamber_step = num_wafer_chamber_step

        self.transitions = []
        states = []
        for row in self.prod_trans.itertuples():
            source = row.Index[0]
            step = source.split("_")[0].strip()
            step_len = len(step)
            chamber = source[step_len:]
            source = step + "\n" + chamber

            dest = row.Index[1]
            step = dest.split("_")[0].strip()
            step_len = len(step)
            chamber = dest[step_len:]
            dest = step + "\n" + chamber
            d = {
                'status': 'None',
                'count': row._1,
                'BOB_count': row._4,
                'WOW_count': row._7,
                'attr': 'B/W',
                'trigger': str(row._1),
                'source': source,
                'dest': dest,
                'step': step
            }
            self.transitions.append(d)
            states.append(row.Index[0])
            states.append(row.Index[1])
        if 'LCresult' in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            print("HERE1")
            if self.parent.analysis_mode == 'or':
                #if and, high subset in case one of them is BOB
                self.high_subset = self.prod_group.loc[((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'DUMMY') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM"))), 'TO']
                self.low_subset = self.prod_group.loc[((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'DUMMY') & (~self.prod_group['TO'].str.contains("DM"))) | ((self.prod_group['LCresult'] == 'DUMMY') & (self.prod_group['UDresult'] == 'WOW') & (~self.prod_group['TO'].str.contains("DM"))), 'TO']
                print("high subset: {}".format(self.high_subset))
                print("low subset: {}".format(self.low_subset))
            if self.parent.analysis_mode == 'and':
                #if or, high subset in case both of them are dummy
                self.high_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'BOB') & (self.prod_group['UDresult'] == 'BOB')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
                self.low_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'WOW') & (self.prod_group['UDresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
        if 'LCresult' in self.prod_group.columns and 'UDresult' not in self.prod_group.columns:
            print("HERE2")
            self.high_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'BOB') & (~self.prod_group['TO'].str.contains("DM")), 'TO']
            self.low_subset = self.prod_group.loc[(self.prod_group['LCresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
        if 'LCresult' not in self.prod_group.columns and 'UDresult' in self.prod_group.columns:
            print("HERE3")
            self.high_subset = self.prod_group.loc[(self.prod_group['UDresult'] == 'BOB')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
            self.low_subset = self.prod_group.loc[(self.prod_group['UDresult'] == 'WOW')& (~self.prod_group['TO'].str.contains("DM")), 'TO']
        print(self.prod_group.columns)
        try:
            self.high_subset = list(set(self.high_subset))

            
            self.low_subset = list(set(self.low_subset))

            BOB_subset = self.prod_temp.loc[self.prod_temp['BOB'] == True, 'TO']
            BOB_subset = list(set(BOB_subset))
            WOW_subset = self.prod_temp.loc[self.prod_temp['WOW'] == True, 'TO']
            WOW_subset = list(set(WOW_subset))

            states = pd.Series(list((set(states))))
            states_group = pd.DataFrame()
            states_group['states'] = states

            states_group['{}'.format(self.parent.model.machine)] = '0'
            states_group['{}'.format(self.parent.model.machine)][states_group['states'].isin(self.high_subset)] = 'HIGH'
            states_group['{}'.format(self.parent.model.machine)][states_group['states'].isin(self.low_subset)] = 'LOW'
            states_group['{}'.format(self.parent.model.prod)] = '0'
            states_group['{}'.format(self.parent.model.prod)][(states_group['states'].isin(BOB_subset)) & (-states_group['states'].isin(WOW_subset))] = 'BOB'
            states_group['{}'.format(self.parent.model.prod)][(states_group['states'].isin(WOW_subset)) & (-states_group['states'].isin(BOB_subset))] = 'WOW'
            states_group['{}'.format(self.parent.model.prod)][(states_group['states'].isin(BOB_subset)) & (states_group['states'].isin(WOW_subset))] = 'B/W'
        except AttributeError as e:
            print(e)
        
        #update states (\n)
        states_modi = []
        for state in states:
            step = state.split("_")[0].strip()
            step_len = len(step)
            chamber = state[step_len:]
            state = step + "\n" + chamber
            states_modi.append(state)

        states_group['states'] = states_modi

        self.states = [tuple(x) for x in states_group[['states', '{}'.format(self.parent.model.machine), '{}'.format(self.parent.model.prod)]].values]
        
        self.prod_trans.to_csv('../result/prod_trans.csv', sep = ',')
        self.prod_trans.to_sql("prod_trans", self.parent.preprocessing_con, if_exists="replace")
        
        


        

    def get_BOB_wafer_cell(self):
        row = self.BOB_wafer_tableWidget.currentItem().row()
        self.BOB_wafer = self.BOB_wafer_tableWidget.item(row,0).text()
        print("BOB wafer: {}".format(self.BOB_wafer))

        BOB_path = self.prod_temp.loc[self.prod_temp.loc[:,'CASE_ID'] == self.BOB_wafer, ['FROM', 'TO']]
        subset = BOB_path[['FROM', 'TO']]
        for s in subset.values:
            if s[0] == 'START':
                s[0] = 'START\n'
            else:
                step = s[0].split("_")[0].strip()
                step_len = len(step)
                chamber = s[0][step_len:]
                s[0] = step + "\n" + chamber

            if s[1] == 'END':
                s[1] = 'END\n'
            else:
                step = s[1].split("_")[0].strip()
                step_len = len(step)
                chamber = s[1][step_len:]
                s[1] = step + "\n" + chamber
            print("subset: {}".format(s))

        tuples = [tuple(x) for x in subset.values]

        for transition in self.transitions:
            src_dest = (transition['source'], transition['dest'])
            if src_dest in tuples:
                transition['status'] = 'valid'
                transition['attr'] = 'BOB'
            else:
                transition['attr'] = 'B/W'

        machine = Single_path_Graph(self.num_wafer_chamber_step, states=self.states, transitions=self.transitions)
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.load('../result/svg/{}.svg'.format(self.svg_name))
        self.tabs.removeTab(self.tabs.currentIndex()-1)


    def get_WOW_wafer_cell(self):
        row = self.WOW_wafer_tableWidget.currentItem().row()
        self.WOW_wafer = self.WOW_wafer_tableWidget.item(row,0).text()
        print("WOW wafer: {}".format(self.WOW_wafer))
        WOW_path = self.prod_temp.loc[self.prod_temp.loc[:,'CASE_ID'] == self.WOW_wafer, ['FROM', 'TO']]
        subset = WOW_path[['FROM', 'TO']]
        for s in subset.values:
            if s[0] == 'START':
                s[0] = 'START\n'
            else:
                step = s[0].split("_")[0].strip()
                step_len = len(step)
                chamber = s[0][step_len:]
                s[0] = step + "\n" + chamber
                
            if s[1] == 'END':
                s[1] = 'END\n'
            else:
                step = s[1].split("_")[0].strip()
                step_len = len(step)
                chamber = s[1][step_len:]
                s[1] = step + "\n" + chamber
            print("subset: {}".format(s))
        tuples = [tuple(x) for x in subset.values]
        for transition in self.transitions:
            src_dest = (transition['source'], transition['dest'])
            if src_dest in tuples:
                transition['status'] = 'valid'
                transition['attr'] = 'WOW'
            else:
                transition['attr'] = 'B/W'



        machine = Single_path_Graph(self.num_wafer_chamber_step, states=self.states, transitions=self.transitions)
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.load('../result/svg/{}.svg'.format(self.svg_name))
        self.tabs.removeTab(self.tabs.currentIndex()-1)

    def set_machine(self):
        row = self.step_tableWidget.currentItem().row()
        step = self.step_tableWidget.item(row,0).text()
        print("step {} selected".format(step))
        machines = self.step_perf.loc[self.step_perf['STEP_SEQ_'] == step, 'machine']
        machines.reset_index(drop=True, inplace=True)
        machines = machines[0].split(', ')
        machines = list(set(machines))

        high_machines = [x for x in machines if x in self.parent.model.high_subset]
        low_machines = [x for x in machines if x in self.parent.model.low_subset]

        self.high_machine_tableWidget.setColumnCount(1)
        self.high_machine_tableWidget.setRowCount(len(high_machines))
        self.high_machine_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.high_machine_tableWidget.setHorizontalHeaderLabels(["High Quality"])
        header = self.high_machine_tableWidget.horizontalHeader()
        header.setStretchLastSection(True)

        for i in range(len(high_machines)):
            self.high_machine_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(high_machines[i]).split("_",1)[1]))
            self.high_machine_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)

        self.low_machine_tableWidget.setColumnCount(1)
        self.low_machine_tableWidget.setRowCount(len(low_machines))
        self.low_machine_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.low_machine_tableWidget.setHorizontalHeaderLabels(["Low Quality"])
        header = self.low_machine_tableWidget.horizontalHeader()
        header.setStretchLastSection(True)

        for i in range(len(low_machines)):
            self.low_machine_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(low_machines[i]).split("_",1)[1]))
            self.low_machine_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)

        

    def handle_start_value_changed(self):
        pass

    def set_default_step_machine(self):
        self.step_tableWidget.setColumnCount(1)
        self.step_tableWidget.setRowCount(len(self.valid_step))
        self.step_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.step_tableWidget.setHorizontalHeaderLabels(["Vaild Steps"])

        for i in range(len(self.valid_step)):
            self.step_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(self.valid_step[i])))
            self.step_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)
        self.step_tableWidget.itemSelectionChanged.connect(self.set_machine)
        header = self.step_tableWidget.horizontalHeader()
        header.setStretchLastSection(True)


    def handle_clear_push(self):
        machine = Graph(self.num_wafer_chamber_step, self.dummy_threshold, self.BOB_threshold, self.WOW_threshold, states=self.states, transitions=self.transitions)
        print("edge threshold: {}".format(str(self.edge_threshold)))
        print("dummy threshold: {}".format(str(self.dummy_threshold)))
        print("BOB threshold: {}".format(str(self.BOB_threshold)))
        print("WOW threshold: {}".format(str(self.WOW_threshold)))
        print("STEP threshold: {}".format(str(self.step_threshold)))
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.load('../result/svg/{}.svg'.format(self.svg_name))
        self.tabs.removeTab(self.tabs.currentIndex()-1)

    def __init__(self, svg, states, transitions, parent=None):
        print("Created Visualization")
        QtWidgets.QMainWindow.__init__(self, parent)

        #db에서 wafer 정보가져오기


        self.states = states
        self.transitions = transitions
        self.step_threshold = 100
        self.edge_threshold = 50
        self.dummy_threshold = 50
        self.BOB_threshold = 30
        self.WOW_threshold = 30

        hbox_main = QtWidgets.QHBoxLayout()
        hbox_slider = QtWidgets.QHBoxLayout()
        
        self.parent = parent
        self.num_wafer_chamber_step = self.parent.model.num_wafer_chamber_step

        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        hbox_main.addWidget(self.tabs)
        
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        #vbox_edge_step_slider
        vbox_edge_step_slider = QtWidgets.QVBoxLayout()


        #step slider
        self.step_slider_widget = Step_Slider_Widget(self)
        self.step_threshold = 50
        self.step_slider_widget.setMaximumSize(QtCore.QSize(600, 250))
        vbox_edge_step_slider.addWidget(self.step_slider_widget)
        #hbox_slider.addWidget(self.step_slider_widget)

        #edge slider
        self.slider_widget = Edge_Slider_Widget(self)
        self.slider_widget.setMaximumSize(QtCore.QSize(600, 250))
        vbox_edge_step_slider.addWidget(self.slider_widget)
        #hbox_slider.addWidget(self.slider_widget)

        hbox_slider.addLayout(vbox_edge_step_slider)

        

        #edge classifier
        vbox_classifying_slider = QtWidgets.QVBoxLayout()

        headerFont=QtGui.QFont()
        headerFont.setBold(True)

        self.edge_highlighting_label = QtWidgets.QLabel()
        self.edge_highlighting_label.setObjectName("Edge_Classifier")
        self.edge_highlighting_label.setText("Arc Highlighting")
        self.edge_highlighting_label.setAlignment(QtCore.Qt.AlignCenter)
        self.edge_highlighting_label.setFont(headerFont)
        
        vbox_classifying_slider.addWidget(self.edge_highlighting_label)

        #dummy slider
        self.dummy_slider_widget = Dummy_Slider_Widget(self)
        self.dummy_threshold = 50
        self.dummy_slider_widget.setMaximumSize(QtCore.QSize(600, 250))
        vbox_classifying_slider.addWidget(self.dummy_slider_widget)

        #classifyting slider label
        self.classifying_label = QtWidgets.QLabel()
        self.classifying_label.setObjectName("Edge_Coloring_label")
        self.classifying_label.setText("유의 Arc 대상 컬러 분류")
        self.classifying_label.setAlignment(QtCore.Qt.AlignCenter)

        #classifying slider
        self.classifying_slider_widget = QRangeSlider(self)
        self.classifying_slider_widget.setMaximumSize(QtCore.QSize(600, 250))
        self.classifying_slider_widget.setRange(30, 70)
        self.classifying_slider_widget.setHeadBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F8BBD0, stop:1 #F8BBD0);')
        self.classifying_slider_widget.setTailBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #BBDEFB, stop:1 #BBDEFB);')
        self.classifying_slider_widget.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #CFD8DC, stop:1 #CFD8DC);')
        
        vbox_classifying_slider.addWidget(self.classifying_label)
        vbox_classifying_slider.addWidget(self.classifying_slider_widget)


        hbox_slider.addLayout(vbox_classifying_slider)
        #self.classifying_slider_widget.startValueChanged.connect(handle_start_value_changed)

        #step_selection
        self.step_tableWidget = QtWidgets.QTableWidget(self)
        self.step_tableWidget.setMaximumSize(QtCore.QSize(200, 250))
        self.step_tableWidget.setObjectName("step_tableWidget")
        self.step_tableWidget.setColumnCount(0)
        self.step_tableWidget.setRowCount(0)

        self.step_selection_label = QtWidgets.QLabel()
        self.step_selection_label.setMinimumSize(QtCore.QSize(130, 50))
        self.step_selection_label.setMaximumSize(QtCore.QSize(130, 50))
        self.step_selection_label.setObjectName("Step_Selection")
        self.step_selection_label.setText("Step Selection")
        self.step_selection_label.setAlignment(QtCore.Qt.AlignCenter)
        headerFont=QtGui.QFont()
        headerFont.setBold(True)
        self.step_selection_label.setFont(headerFont)

        

        #HIGH machine list up
        self.high_machine_tableWidget = QtWidgets.QTableWidget(self)
        self.high_machine_tableWidget.setMaximumSize(QtCore.QSize(200, 250))
        self.high_machine_tableWidget.setObjectName("high_machine_tableWidget")
        self.high_machine_tableWidget.setColumnCount(0)
        self.high_machine_tableWidget.setRowCount(0)

        self.high_machine_label = QtWidgets.QLabel()
        self.high_machine_label.setMinimumSize(QtCore.QSize(130, 50))
        self.high_machine_label.setMaximumSize(QtCore.QSize(130, 50))
        self.high_machine_label.setObjectName("high_machine")
        self.high_machine_label.setText("Machines in Step")
        self.high_machine_label.setAlignment(QtCore.Qt.AlignCenter)

        #LOW machine list up
        self.low_machine_tableWidget = QtWidgets.QTableWidget(self)
        self.low_machine_tableWidget.setMaximumSize(QtCore.QSize(200, 250))
        self.low_machine_tableWidget.setObjectName("low_machine_tableWidget")
        self.low_machine_tableWidget.setColumnCount(0)
        self.low_machine_tableWidget.setRowCount(0)

        """
        self.low_machine_label = QtWidgets.QLabel()
        self.low_machine_label.setMinimumSize(QtCore.QSize(130, 50))
        self.low_machine_label.setMaximumSize(QtCore.QSize(130, 50))
        self.low_machine_label.setObjectName("low_machine")
        self.low_machine_label.setText("Low Machine")
        self.low_machine_label.setAlignment(QtCore.Qt.AlignCenter)
        """

        #BOB_wafer_selection
        self.BOB_wafer_tableWidget = QtWidgets.QTableWidget(self)
        self.BOB_wafer_tableWidget.setMaximumSize(QtCore.QSize(200, 250))
        #self.BOB_wafer_tableWidget.setGeometry(QtCore.QRect(60, 42, 200, 250))
        self.BOB_wafer_tableWidget.setObjectName("BOB_wafer_tableWidget")
        self.BOB_wafer_tableWidget.setColumnCount(0)
        self.BOB_wafer_tableWidget.setRowCount(0)

        #WOW_wafer_selection
        self.WOW_wafer_tableWidget = QtWidgets.QTableWidget(self)
        self.WOW_wafer_tableWidget.setMaximumSize(QtCore.QSize(200, 250))
        #self.WOW_wafer_tableWidget.setGeometry(QtCore.QRect(60, 42, 200, 250))
        self.WOW_wafer_tableWidget.setObjectName("WOW_wafer_tableWidget")
        self.WOW_wafer_tableWidget.setColumnCount(0)
        self.WOW_wafer_tableWidget.setRowCount(0)

        #wafer selection label
        headerFont=QtGui.QFont()
        headerFont.setBold(True)

        self.wafer_selection_label = QtWidgets.QLabel()
        self.wafer_selection_label.setMinimumSize(QtCore.QSize(130, 50))
        self.wafer_selection_label.setMaximumSize(QtCore.QSize(130, 50))
        self.wafer_selection_label.setObjectName("Wafer_Selection")
        self.wafer_selection_label.setText("Wafer Highlighting")
        self.wafer_selection_label.setAlignment(QtCore.Qt.AlignCenter)

        self.wafer_selection_label.setFont(headerFont)

        self.clear_push = QtWidgets.QPushButton()
        self.clear_push.setObjectName("clear_push")
        self.clear_push.setText("Clear")
        self.clear_push.clicked.connect(self.handle_clear_push)

        #connect DB
        with self.parent.preprocessing_con:
            cur = self.parent.preprocessing_con.cursor()
            cur.execute(' select name from sqlite_master where type="table"')
            print(cur.fetchall())
        self.prod_temp = pd.read_sql_query("select * from prod_temp;", self.parent.preprocessing_con)
        self.step_perf = pd.read_sql_query("select * from step_perf;", self.parent.preprocessing_con)
        self.valid_step = list(self.step_perf.loc[:,'STEP_SEQ_'])
        self.valid_step.sort()
        self.prod_group = pd.read_sql_query("select * from {}_info;".format(self.parent.model.machine), self.parent.preprocessing_con)
        if "('UDresult', '')" in self.prod_group.columns:
            self.prod_group = self.prod_group.rename(columns = {"('UDresult', '')":'UDresult'})
        self.prod_trans = pd.read_sql_query("select * from prod_trans;", self.parent.preprocessing_con)
        self.step_perf.sort_values('diff', ascending = False, inplace = True)
        self.step_perf.reset_index(drop=True, inplace=True)

        #set step_selection
        self.set_default_step_machine()

        #BOB_wafer
        self.BOB_wafer_tableWidget.setColumnCount(1)
        no_wafers = 10
        self.BOB_wafer_tableWidget.setRowCount(no_wafers)
        self.BOB_wafer_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.BOB_wafer_tableWidget.setHorizontalHeaderLabels(["BOB_wafer"])

        self.wafer_value = self.prod_temp.groupby('CASE_ID', as_index=False)['VALUE'].mean()
        self.wafer_value.sort_values('VALUE', ascending=False, inplace=True)

        for i in range(no_wafers):
            self.BOB_wafer_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(self.wafer_value['CASE_ID'].iat[i])))
            self.BOB_wafer_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)
        self.BOB_wafer_tableWidget.itemSelectionChanged.connect(self.get_BOB_wafer_cell)
        header = self.BOB_wafer_tableWidget.horizontalHeader()
        header.setStretchLastSection(True)

        #WOW_wafer
        self.WOW_wafer_tableWidget.setColumnCount(1)
        no_wafers = 10
        self.WOW_wafer_tableWidget.setRowCount(no_wafers)
        self.WOW_wafer_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.WOW_wafer_tableWidget.setHorizontalHeaderLabels(["WOW_wafer"])

        self.wafer_value.sort_values('VALUE', ascending=True, inplace=True)

        for i in range(no_wafers):
            self.WOW_wafer_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(self.wafer_value['CASE_ID'].iat[i])))
            self.WOW_wafer_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)
        self.WOW_wafer_tableWidget.itemSelectionChanged.connect(self.get_WOW_wafer_cell)
        header = self.WOW_wafer_tableWidget.horizontalHeader()
        header.setStretchLastSection(True)

        #wafer highlighting layout
        vbox_selection_wafer = QtWidgets.QVBoxLayout()
        vbox_selection_wafer.addWidget(self.wafer_selection_label)
        vbox_selection_wafer.addWidget(self.BOB_wafer_tableWidget)
        vbox_selection_wafer.addWidget(self.WOW_wafer_tableWidget)
        vbox_selection_wafer.addWidget(self.clear_push)
        hbox_slider.addLayout(vbox_selection_wafer)


        vbox_selection = QtWidgets.QVBoxLayout()
        
        vbox_selection.addWidget(self.step_selection_label)
        vbox_selection.addWidget(self.step_tableWidget)
        
        vbox_selection.addWidget(self.high_machine_label)
        vbox_selection.addWidget(self.high_machine_tableWidget)
        
        #vbox_selection.addWidget(self.low_machine_label)
        vbox_selection.addWidget(self.low_machine_tableWidget)
        
        
        

        #Layout



        hbox_main.addLayout(vbox_selection)
        
        vbox_main = QtWidgets.QVBoxLayout()
        vbox_main.addLayout(hbox_main)
        #vbox_main.addWidget(self.classifying_slider_label)
        vbox_main.addLayout(hbox_slider)

        

        new_widget = QtWidgets.QWidget()
        new_widget.setLayout(vbox_main)
        self.setCentralWidget(new_widget)

        self.resize(1600, 1000)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        
        self.actionOpen = QtWidgets.QAction(self)
        self.actionOpen.setShortcuts(QtGui.QKeySequence.Open);
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setShortcuts(QtGui.QKeySequence.Quit);
        self.actionClose = QtWidgets.QAction(self)
        self.actionClose.setShortcuts(QtGui.QKeySequence.Close)
        self.actionCenter = QtWidgets.QAction(self)
        self.actionCenter.setShortcuts(QtGui.QKeySequence("Space"));
        self.actionReload = QtWidgets.QAction(self)
        self.actionReload.setShortcuts(QtGui.QKeySequence("F5"));

        self.actionNext = QtWidgets.QAction(self)
        self.actionNext.setShortcuts(QtGui.QKeySequence("Page Down"));
        self.actionPrev = QtWidgets.QAction(self)
        self.actionPrev.setShortcuts(QtGui.QKeySequence("Page Up"));
 
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCenter)
        self.menuEdit.addAction(self.actionReload)
        self.menuEdit.addAction(self.actionNext)
        self.menuEdit.addAction(self.actionPrev)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.actionCenter.triggered.connect(self.center)
        self.actionReload.triggered.connect(self.reload)
        self.actionNext.triggered.connect(self.nextTab)
        self.actionPrev.triggered.connect(self.prevTab)
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.open)
        self.actionClose.triggered.connect(self.closeTab)

        self.setWindowTitle("Svg Viewer")
        self.menuFile.setTitle("&File")
        self.menuEdit.setTitle("&Edit")
        self.actionOpen.setText("&Open")
        self.actionClose.setText("&Close Tab")
        self.actionQuit.setText("&Quit")
        self.actionCenter.setText("&Center")
        self.actionReload.setText("&Reload")
        self.actionNext.setText("&Next Tab")
        self.actionPrev.setText("&Prev Tab")
        self.show()
        self.load('../result/svg/{}.svg'.format(svg))



class Edge_Slider_Widget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Edge_Slider_Widget, self).__init__(parent)
        self.init_ui()
        self.parent = parent

    def init_ui(self):
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        #self.slider.setStyleSheet(self.stylesheet())
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.handle_valueChanged)
        self.slider.sliderReleased.connect(self.handle_sliderReleased)
        self.le = QtWidgets.QLineEdit()
        self.le.setMaximumSize(QtCore.QSize(150, 16777215))
        self.le.setAlignment(QtCore.Qt.AlignCenter)

        self.lb = QtWidgets.QLabel()
        self.lb.setObjectName("Edge_Threshold")
        self.lb.setText("빈도수 기반 Arc 필터링")
        self.lb.setAlignment(QtCore.Qt.AlignCenter)

        h_box = QtWidgets.QHBoxLayout()
        v_box = QtWidgets.QVBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.le)
        
        v_box.addWidget(self.lb)
        v_box.addLayout(h_box)
        
        
        self.setLayout(v_box)
        self.show()

    def handle_valueChanged(self):
        self.edge_threshold = self.slider.value()
        self.le.setText('show ' + str(self.edge_threshold)+" % of edges")
        self.parent.edge_threshold = self.edge_threshold

    def handle_sliderReleased(self):

        self.edge_threshold = self.slider.value()
        def extract_step(x):
            if x == 'END':
                return x
            else:
                return x.split("_")[0].strip()
        self.prod_trans = pd.read_sql_query("select * from prod_trans;", self.parent.parent.preprocessing_con)
        prod_trans_temp = self.parent.prod_trans.copy()
        
        #prod_trans_temp.reset_index(inplace=True)
        #prod_trans_temp.columns = ['_'.join(col).strip() for col in prod_trans_temp.columns.values]
        try:
            prod_trans_temp['STEP_SEQ_'] = prod_trans_temp['TO'].apply(extract_step)
            unique_steps = list(set(prod_trans_temp['STEP_SEQ_'].tolist()))

            num_wafer_chamber_step = {}
            for step in unique_steps:
                num_wafer = prod_trans_temp.loc[prod_trans_temp['STEP_SEQ_'] == step, "('VALUE', 'count_nonzero')"]
                num_wafer.sort_values(ascending = False, inplace = True)
                idx = (len(num_wafer)-1) * self.edge_threshold * 0.01
                idx = int(idx + 0.5)

                num_wafer_chamber_step[step] = num_wafer.iloc[idx]
        except KeyError as e:
            prod_trans_temp.reset_index(inplace=True)
            prod_trans_temp.columns = ['_'.join(col).strip() for col in prod_trans_temp.columns.values]
            prod_trans_temp['STEP_SEQ_'] = prod_trans_temp['TO_'].apply(extract_step)
            unique_steps = list(set(prod_trans_temp['STEP_SEQ_'].tolist()))

            num_wafer_chamber_step = {}
            for step in unique_steps:
                num_wafer = prod_trans_temp.loc[prod_trans_temp['STEP_SEQ_'] == step, "VALUE_count_nonzero"]
                num_wafer.sort_values(ascending = False, inplace = True)
                idx = (len(num_wafer)-1) * self.edge_threshold * 0.01
                idx = int(idx + 0.5)

                num_wafer_chamber_step[step] = num_wafer.iloc[idx]
            print(e)
        print(prod_trans_temp)
        """
        unique_steps = list(set(prod_trans_temp['STEP_SEQ_'].tolist()))

        num_wafer_chamber_step = {}
        for step in unique_steps:
            num_wafer = prod_trans_temp.loc[prod_trans_temp['STEP_SEQ_'] == step, "('VALUE', 'count_nonzero')"]
            num_wafer.sort_values(ascending = False, inplace = True)
            idx = (len(num_wafer)-1) * self.edge_threshold * 0.01
            idx = int(idx + 0.5)

            num_wafer_chamber_step[step] = num_wafer.iloc[idx]
            #num_wafer_chamber_step[step] = np.percentile(num_wafer, self.edge_threshold)
        """
        print("edge criteria: {}".format(num_wafer_chamber_step))
        self.parent.num_wafer_chamber_step = num_wafer_chamber_step

        machine = Graph(self.parent.num_wafer_chamber_step, self.parent.dummy_threshold, self.parent.BOB_threshold, self.parent.WOW_threshold, states=self.parent.states, transitions=self.parent.transitions)
        print("edge threshold: {}".format(str(self.edge_threshold)))
        print("dummy threshold: {}".format(str(self.parent.dummy_threshold)))
        print("BOB threshold: {}".format(str(self.parent.BOB_threshold)))
        print("WOW threshold: {}".format(str(self.parent.WOW_threshold)))
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.parent.load('../result/svg/{}.svg'.format(self.svg_name))
        self.parent.tabs.removeTab(self.parent.tabs.currentIndex()-1)
        print(self.edge_threshold)

    def stylesheet(self):
        return """
            QSlider::groove:horizontal {
                background: #222;
                height: 40px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                    stop:0 #282, stop:1 #393);
                
                height: 40px;
            }

            QSlider::add-page:horizontal {
                'background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);'
                height: 40px;
            }

            QSlider::handle:horizontal {
                background: #393;
                border: 0px;
                width: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
                border-radius: 0px;
            }
        """

class Dummy_Slider_Widget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Dummy_Slider_Widget, self).__init__(parent)
        self.init_ui()
        self.parent = parent

    def init_ui(self):
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        #self.slider.setStyleSheet(self.stylesheet())
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.handle_valueChanged)
        self.slider.sliderReleased.connect(self.handle_sliderReleased)
        self.le = QtWidgets.QLineEdit()
        self.le.setMaximumSize(QtCore.QSize(200, 16777215))
        self.le.setAlignment(QtCore.Qt.AlignCenter)

        self.lb = QtWidgets.QLabel()
        self.lb.setObjectName("Dummy_Threshold")
        self.lb.setText("BW/T 비율 기반 유의 Arc 분류")
        self.lb.setAlignment(QtCore.Qt.AlignCenter)

        h_box = QtWidgets.QHBoxLayout()
        v_box = QtWidgets.QVBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.le)
        
        v_box.addWidget(self.lb)
        v_box.addLayout(h_box)
        
        
        self.setLayout(v_box)
        self.show()

    def handle_valueChanged(self):
        self.dummy_threshold = self.slider.value()
        self.le.setText('gray if BOB+WOW ratio < ' + str(100 - self.dummy_threshold) + "%")
        self.parent.dummy_threshold = self.dummy_threshold

    def handle_sliderReleased(self):

        self.dummy_threshold = self.slider.value()
        
        machine = Graph(self.parent.num_wafer_chamber_step, self.dummy_threshold, self.parent.BOB_threshold, self.parent.WOW_threshold, states=self.parent.states, transitions=self.parent.transitions)
        print("edge threshold: {}".format(str(self.parent.edge_threshold)))
        print("dummy threshold: {}".format(str(self.dummy_threshold)))
        print("BOB threshold: {}".format(str(self.parent.BOB_threshold)))
        print("WOW threshold: {}".format(str(self.parent.WOW_threshold)))
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.parent.load('../result/svg/{}.svg'.format(self.svg_name))
        self.parent.tabs.removeTab(self.parent.tabs.currentIndex()-1)

class Step_Slider_Widget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Step_Slider_Widget, self).__init__(parent)
        self.init_ui()
        self.parent = parent
        
        

    def init_ui(self):
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        #self.slider.setStyleSheet(self.stylesheet())
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.handle_valueChanged)
        self.slider.sliderReleased.connect(self.handle_sliderReleased)
        self.le = QtWidgets.QLineEdit()
        self.le.setMaximumSize(QtCore.QSize(150, 16777215))
        self.le.setAlignment(QtCore.Qt.AlignCenter)

        headerFont=QtGui.QFont()
        headerFont.setBold(True)
        

        self.filtering = QtWidgets.QLabel()
        self.filtering.setObjectName("Highliting")
        self.filtering.setText("Filtering")
        self.filtering.setAlignment(QtCore.Qt.AlignCenter)
        self.filtering.setFont(headerFont)

        self.lb = QtWidgets.QLabel()
        self.lb.setObjectName("Step_Threshold")
        self.lb.setText("수율 기반 주요 스텝 필터링")
        self.lb.setAlignment(QtCore.Qt.AlignCenter)

        h_box = QtWidgets.QHBoxLayout()
        v_box = QtWidgets.QVBoxLayout()
        h_box.addWidget(self.slider)
        h_box.addWidget(self.le)
        
        v_box.addWidget(self.filtering)
        v_box.addWidget(self.lb)
        v_box.addLayout(h_box)
        
        
        self.setLayout(v_box)
        self.show()

    def handle_valueChanged(self):
        self.step_threshold = self.slider.value()
        self.le.setText('show ' + str(self.step_threshold)+" % of steps")
        self.parent.step_threshold = self.step_threshold

    def handle_sliderReleased(self):
        self.step_threshold = self.slider.value()
        self.parent.create_transitions_and_states(self.step_threshold)

        
        
        machine = Graph(self.parent.num_wafer_chamber_step, self.parent.dummy_threshold, self.parent.BOB_threshold, self.parent.WOW_threshold, states=self.parent.states, transitions=self.parent.transitions)
        print("edge threshold: {}".format(str(self.parent.edge_threshold)))
        print("dummy threshold: {}".format(str(self.parent.dummy_threshold)))
        print("BOB threshold: {}".format(str(self.parent.BOB_threshold)))
        print("WOW threshold: {}".format(str(self.parent.WOW_threshold)))
        print("STEP threshold: {}".format(str(self.step_threshold)))
        self.svg_name = 'svg_' + str(time.time())
        machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        self.parent.load('../result/svg/{}.svg'.format(self.svg_name))
        self.parent.tabs.removeTab(self.parent.tabs.currentIndex()-1)


        self.parent.step_tableWidget.setColumnCount(1)
        self.parent.step_tableWidget.setRowCount(len(self.parent.valid_step))
        self.parent.step_tableWidget.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.parent.step_tableWidget.setHorizontalHeaderLabels(["Vaild Steps"])

        for i in range(len(self.parent.valid_step)):
            print(self.parent.valid_step[i])
            self.parent.step_tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(str(self.parent.valid_step[i])))
            self.parent.step_tableWidget.item(i,0).setTextAlignment(QtCore.Qt.AlignCenter)
        self.parent.step_tableWidget.itemSelectionChanged.connect(self.parent.set_machine)
        
def handleIntSignal(signum, frame):
    QtGui.qApp.closeAllWindows()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
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
    window = Visualization()
    window.show()

    #for path in app.arguments()[1:]:
    window.load('../../result/state_svg.svg');

    #This is a hack to let the interperter run once every 1/2 second to catch sigint
    timer = QtCore.QTimer()
    timer.start(500)  
    timer.timeout.connect(lambda: None)
    signal.signal(signal.SIGINT, handleIntSignal)
    
    sys.exit(app.exec_())
