# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'value_criterion_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 201)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 60, 310, 101))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.value_criterion_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.value_criterion_label.setObjectName("value_criterion_label")
        self.verticalLayout.addWidget(self.value_criterion_label, 0, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.value_BOB_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.value_BOB_lineEdit.setObjectName("value_BOB_lineEdit")
        self.horizontalLayout.addWidget(self.value_BOB_lineEdit)
        self.value_WOW_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.value_WOW_lineEdit.setText("")
        self.value_WOW_lineEdit.setObjectName("value_WOW_lineEdit")
        self.horizontalLayout.addWidget(self.value_WOW_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.value_push = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.value_push.setObjectName("value_push")
        self.verticalLayout.addWidget(self.value_push)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.value_criterion_label.setText(_translate("Dialog", "수율 기준"))
        self.value_BOB_lineEdit.setPlaceholderText(_translate("Dialog", "BOB 기준"))
        self.value_WOW_lineEdit.setPlaceholderText(_translate("Dialog", "WOW 기준"))
        self.value_push.setText(_translate("Dialog", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

