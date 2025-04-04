# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(831, 852)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scenario_checkBox = QtWidgets.QCheckBox(Form)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.scenario_checkBox.setFont(font)
        self.scenario_checkBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.scenario_checkBox.setAutoFillBackground(False)
        self.scenario_checkBox.setObjectName("scenario_checkBox")
        self.verticalLayout_4.addWidget(self.scenario_checkBox)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.questioin_groupBox = QtWidgets.QGroupBox(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.questioin_groupBox.setFont(font)
        self.questioin_groupBox.setObjectName("questioin_groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.questioin_groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.userinpput_plainTextEdit = QtWidgets.QPlainTextEdit(self.questioin_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.userinpput_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.userinpput_plainTextEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.userinpput_plainTextEdit.setFont(font)
        self.userinpput_plainTextEdit.setReadOnly(False)
        self.userinpput_plainTextEdit.setObjectName("userinpput_plainTextEdit")
        self.verticalLayout_2.addWidget(self.userinpput_plainTextEdit)
        self.verticalLayout_5.addWidget(self.questioin_groupBox)
        self.ground_truth_groupBox = QtWidgets.QGroupBox(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ground_truth_groupBox.setFont(font)
        self.ground_truth_groupBox.setObjectName("ground_truth_groupBox")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.ground_truth_groupBox)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.reference_context_plainTextEdit = QtWidgets.QPlainTextEdit(self.ground_truth_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reference_context_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.reference_context_plainTextEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.reference_context_plainTextEdit.setFont(font)
        self.reference_context_plainTextEdit.setReadOnly(False)
        self.reference_context_plainTextEdit.setObjectName("reference_context_plainTextEdit")
        self.verticalLayout_7.addWidget(self.reference_context_plainTextEdit)
        self.verticalLayout_5.addWidget(self.ground_truth_groupBox)
        self.groupBox = QtWidgets.QGroupBox(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.reference_plainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.reference_plainTextEdit.setFont(font)
        self.reference_plainTextEdit.setReadOnly(False)
        self.reference_plainTextEdit.setObjectName("reference_plainTextEdit")
        self.verticalLayout_8.addWidget(self.reference_plainTextEdit)
        self.verticalLayout_5.addWidget(self.groupBox)
        self.contexts_groupBox = QtWidgets.QGroupBox(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.contexts_groupBox.setFont(font)
        self.contexts_groupBox.setObjectName("contexts_groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.contexts_groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.retrieved_context_plainTextEdit = QtWidgets.QPlainTextEdit(self.contexts_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.retrieved_context_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.retrieved_context_plainTextEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.retrieved_context_plainTextEdit.setFont(font)
        self.retrieved_context_plainTextEdit.setReadOnly(False)
        self.retrieved_context_plainTextEdit.setObjectName("retrieved_context_plainTextEdit")
        self.verticalLayout.addWidget(self.retrieved_context_plainTextEdit)
        self.verticalLayout_5.addWidget(self.contexts_groupBox)
        self.answer_groupBox = QtWidgets.QGroupBox(self.frame)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.answer_groupBox.setFont(font)
        self.answer_groupBox.setObjectName("answer_groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.answer_groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.response_plainTextEdit = QtWidgets.QPlainTextEdit(self.answer_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.response_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.response_plainTextEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.response_plainTextEdit.setFont(font)
        self.response_plainTextEdit.setReadOnly(False)
        self.response_plainTextEdit.setObjectName("response_plainTextEdit")
        self.horizontalLayout_3.addWidget(self.response_plainTextEdit)
        self.verticalLayout_5.addWidget(self.answer_groupBox)
        self.horizontalLayout.addWidget(self.frame)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.verticalLayout_6.addLayout(self.formLayout)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.line = QtWidgets.QFrame(Form)
        self.line.setMidLineWidth(4)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.scenario_checkBox.setText(_translate("Form", "CheckBox"))
        self.questioin_groupBox.setTitle(_translate("Form", "User Input (Question)"))
        self.ground_truth_groupBox.setTitle(_translate("Form", "Reference_Contexts(from OPEN AI - 문서로 질문, 답변 만들 때, Golden Contexts --> Test Set)"))
        self.groupBox.setTitle(_translate("Form", "Reference(from OPEN AI - 문서로 질문, 답변 만들 때, Golden Data --> Test Set)"))
        self.contexts_groupBox.setTitle(_translate("Form", "Retrived_Contexts(James 만든 툴에서 추출)"))
        self.answer_groupBox.setTitle(_translate("Form", "Response(James 만든 툴에서 추출 또는 chatbot에서 추출한 답변 - \"use chatbot Answer check box에서 선택할 수 있음)"))
        self.groupBox_2.setTitle(_translate("Form", "Score"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
