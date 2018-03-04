from PyQt5 import QtSvg,QtCore,QtGui,Qt,QtWidgets

import time
import sys, signal, os
sys.path.append('../')
from diagrams import Graph
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

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


class Ui_Form(object):
    """default range slider form"""
    
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("SliderWidget"))
        Form.resize(300, 30)
        Form.setStyleSheet(_fromUtf8(DEFAULT_CSS))
        """
        self.gridLayout = QtWidgets.QGridLayout(Form)
        #self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self._splitter = QtWidgets.QSplitter(Form)
        self._splitter.setMinimumSize(QtCore.QSize(0, 0))
        self._splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self._splitter.setOrientation(QtCore.Qt.Horizontal)
        self._splitter.setObjectName(_fromUtf8("splitter"))
        self._head = QtWidgets.QGroupBox(self._splitter)
        self._head.setTitle(_fromUtf8(""))
        self._head.setObjectName(_fromUtf8("Head"))
        self._handle = QtWidgets.QGroupBox(self._splitter)
        self._handle.setTitle(_fromUtf8(""))
        self._handle.setObjectName(_fromUtf8("Span"))
        self._tail = QtWidgets.QGroupBox(self._splitter)
        self._tail.setTitle(_fromUtf8(""))
        self._tail.setObjectName(_fromUtf8("Tail"))
        self.gridLayout.addWidget(self._splitter, 0, 0, 1, 1)


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        """
class SliderWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(SliderWidget, self).__init__(parent)
        self.setupUi(self)
        self.init_ui()
        #self.states = parent.states
        #self.transitions = parent.transitions
        #self.median_edge_count = parent.median_edge_count
        #self.parent = parent

    def init_ui(self):
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setStyleSheet(self.stylesheet())
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        #self.slider.valueChanged.connect(self.handle_valueChanged)
        #self.slider.sliderReleased.connect(self.handle_sliderReleased)
        self.le = QtWidgets.QLineEdit()
        self.le.setAlignment(QtCore.Qt.AlignVCenter)

        self.lb = QtWidgets.QLabel()
        self.lb.setObjectName("Edge_Threshold")
        self.lb.setText("Edge Threshold")
        self.lb.setAlignment(QtCore.Qt.AlignCenter)

        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(self.lb)
        v_box.addWidget(self.slider)
        v_box.addWidget(self.le)
        self.setLayout(v_box)
        self.show()

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

    def handle_valueChanged(self):
        self.edge_threshold = self.slider.value()
        self.le.setText('show ' + str(100 - self.edge_threshold/2)+" % of edges")
        self.parent.edge_threshold = self.edge_threshold

    def handle_sliderReleased(self):

        self.edge_threshold = self.slider.value()
        
        #machine = Graph(self.edge_threshold*self.median_edge_count * 0.01, states=self.states, transitions=self.transitions)
        #self.svg_name = 'svg_' + str(time.time())
        #machine.get_graph().draw('../result/svg/{}.svg'.format(self.svg_name), format ='svg', prog='dot')
        #self.parent.load('../result/svg/{}.svg'.format(self.svg_name))
        #self.parent.tabs.removeTab(self.parent.tabs.currentIndex()-1)

#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    s = SliderWidget()
    s.show()
    
    #rs.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
    #rs.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
    app.exec_()

