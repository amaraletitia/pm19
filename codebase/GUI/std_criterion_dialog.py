# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'std_criterion_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(309, 203)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 46, 211, 101))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.std_criterion_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.std_criterion_label.setObjectName("std_criterion_label")
        self.verticalLayout.addWidget(self.std_criterion_label, 0, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.std_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.std_lineEdit.setText("")
        self.std_lineEdit.setObjectName("std_lineEdit")
        self.horizontalLayout.addWidget(self.std_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.std_push = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.std_push.setObjectName("std_push")
        self.verticalLayout.addWidget(self.std_push)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.std_criterion_label.setText(_translate("Dialog", "수율 표준편차 기준"))
        self.std_lineEdit.setPlaceholderText(_translate("Dialog", "기준"))
        self.std_push.setText(_translate("Dialog", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

