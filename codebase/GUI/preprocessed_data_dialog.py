# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preprocessed_data_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(630, 407)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.data_tableWidget = QtWidgets.QTableWidget(Dialog)
        self.data_tableWidget.setObjectName("data_tableWidget")
        self.data_tableWidget.setColumnCount(0)
        self.data_tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.data_tableWidget)
        self.preprocessed_data_dialog_push = QtWidgets.QPushButton(Dialog)
        self.preprocessed_data_dialog_push.setObjectName("preprocessed_data_dialog_push")
        self.verticalLayout.addWidget(self.preprocessed_data_dialog_push)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "전처리 후 데이터 List"))
        self.preprocessed_data_dialog_push.setText(_translate("Dialog", "분석 시작"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

