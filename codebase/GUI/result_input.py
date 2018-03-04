# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'result_input.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(917, 720)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(50, 40, 721, 461))
        self.tabWidget.setObjectName("tabWidget")
        self.data_selection_tab = QtWidgets.QWidget()
        self.data_selection_tab.setObjectName("data_selection_tab")
        self.result_label = QtWidgets.QLabel(self.data_selection_tab)
        self.result_label.setGeometry(QtCore.QRect(60, 24, 612, 12))
        self.result_label.setObjectName("result_label")
        self.result_tableWidget = QtWidgets.QTableWidget(self.data_selection_tab)
        self.result_tableWidget.setGeometry(QtCore.QRect(60, 42, 612, 342))
        self.result_tableWidget.setObjectName("result_tableWidget")
        self.result_tableWidget.setColumnCount(0)
        self.result_tableWidget.setRowCount(0)
        self.result_push = QtWidgets.QPushButton(self.data_selection_tab)
        self.result_push.setGeometry(QtCore.QRect(60, 390, 612, 23))
        self.result_push.setObjectName("result_push")
        self.tabWidget.addTab(self.data_selection_tab, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.result_label.setText(_translate("Form", "분석 결과 List"))
        self.result_push.setText(_translate("Form", "시각화"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.data_selection_tab), _translate("Form", "분석 결과 선택"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

