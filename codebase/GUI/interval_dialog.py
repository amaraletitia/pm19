# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interval_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(383, 191)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(70, 50, 246, 81))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.start_step_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.start_step_lineEdit.setText("")
        self.start_step_lineEdit.setObjectName("start_step_lineEdit")
        self.horizontalLayout_12.addWidget(self.start_step_lineEdit)
        self.end_step_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.end_step_lineEdit.setText("")
        self.end_step_lineEdit.setObjectName("end_step_lineEdit")
        self.horizontalLayout_12.addWidget(self.end_step_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.interval_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.interval_label.setObjectName("interval_label")
        self.horizontalLayout.addWidget(self.interval_label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.days_lineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.days_lineEdit.sizePolicy().hasHeightForWidth())
        self.days_lineEdit.setSizePolicy(sizePolicy)
        self.days_lineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.days_lineEdit.setObjectName("days_lineEdit")
        self.horizontalLayout.addWidget(self.days_lineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.interval_push = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.interval_push.sizePolicy().hasHeightForWidth())
        self.interval_push.setSizePolicy(sizePolicy)
        self.interval_push.setObjectName("interval_push")
        self.verticalLayout.addWidget(self.interval_push)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.start_step_lineEdit.setPlaceholderText(_translate("Dialog", "Start(e.g. S001)"))
        self.end_step_lineEdit.setPlaceholderText(_translate("Dialog", "End(e.g. S075)"))
        self.interval_label.setText(_translate("Dialog", "Interval"))
        self.days_lineEdit.setPlaceholderText(_translate("Dialog", "(days)"))
        self.interval_push.setText(_translate("Dialog", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

