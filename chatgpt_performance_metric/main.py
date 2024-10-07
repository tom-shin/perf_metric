import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import logging
import json
import easygui
import threading
import csv

from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer, QProcess
from PyQt5 import QtWidgets, QtCore, QtGui

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QRadioButton, QWidget

import pandas as pd

# 모든 행과 열을 출력할 수 있도록 설정 변경
pd.set_option('display.max_rows', None)  # 모든 행을 출력
pd.set_option('display.max_columns', None)  # 모든 열을 출력
pd.set_option('display.width', None)  # 출력 폭을 제한하지 않음
pd.set_option('display.max_colwidth', None)  # 각 열의 최대 너비를 제한하지 않음

# user defined module
from configuration.model_config import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "scenario", "version.txt")
with open(file_path, "r") as file_:
    Version_ = file_.readline()

logging.basicConfig(level=logging.INFO)


def PRINT_(*args):
    logging.info(args)


def load_module_func(module_name):
    mod = __import__(f"{module_name}", fromlist=[module_name])
    return mod


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


class ModalLess_ProgressDialog(QWidget):  # popup 메뉴가 있어도 뒤 main gui의 제어가 가능 함
    send_user_close_event = pyqtSignal(bool)

    def __init__(self, message, show=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(message)

        self.resize(400, 100)  # 원하는 크기로 조절

        self.progress_bar = QProgressBar(self)
        self.label = QLabel("", self)
        self.close_button = QPushButton("Close", self)
        self.radio_button = QRadioButton("", self)

        # Create a horizontal layout for the close button and spacer
        h_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout.addSpacerItem(spacer)
        h_layout.addWidget(self.close_button)

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        layout.addWidget(self.radio_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        # Close 버튼 클릭 시 다이얼로그를 닫음
        self.close_button.clicked.connect(self.close)

        if show:
            self.close_button.show()
        else:
            self.close_button.hide()

        # Timer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_radio_button)
        self.timer.start(500)  # 500ms 간격으로 토글

        self.radio_state = False  # 깜빡임 상태 초기화

    def setProgressBarMaximum(self, max_value):
        self.progress_bar.setMaximum(int(max_value))

    def onCountChanged(self, value):
        self.progress_bar.setValue(int(value))

    def onProgressTextChanged(self, text):
        self.label.setText(text)

    def showModal_less(self):
        self.showModal()

    def showModal(self):
        self.show()

    def closeEvent(self, event):
        self.send_user_close_event.emit(True)
        event.accept()

    def toggle_radio_button(self):
        if self.radio_state:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: red;
                            border-radius: 5px;
                        }
                    """)
        else:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: blue;
                            border-radius: 5px;
                        }
                    """)
        self.radio_state = not self.radio_state


class Modal_ProgressDialog(QDialog):  # popup 메뉴가 있으면 뒤 main gui의 제어 불 가능 -> modal
    send_user_close_event = pyqtSignal(bool)

    def __init__(self, message, show=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(message)
        self.setModal(True)

        self.resize(400, 100)  # 원하는 크기로 조절

        self.progress_bar = QProgressBar(self)
        self.label = QLabel("", self)
        self.close_button = QPushButton("Close", self)
        self.radio_button = QRadioButton("", self)

        # Create a horizontal layout for the close button and spacer
        h_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout.addSpacerItem(spacer)
        h_layout.addWidget(self.close_button)

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        layout.addWidget(self.radio_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        # Close 버튼 클릭 시 다이얼로그를 닫음
        self.close_button.clicked.connect(self.close)

        if show:
            self.close_button.show()
        else:
            self.close_button.hide()

        # Timer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_radio_button)
        self.timer.start(500)  # 500ms 간격으로 토글

        self.radio_state = False  # 깜빡임 상태 초기화

    def setProgressBarMaximum(self, max_value):
        self.progress_bar.setMaximum(int(max_value))

    def onCountChanged(self, value):
        self.progress_bar.setValue(int(value))

    def onProgressTextChanged(self, text):
        self.label.setText(text)

    def showModal(self):
        super().exec_()

    def showModal_less(self):
        super().show()

    def closeEvent(self, event):
        self.send_user_close_event.emit(True)
        event.accept()

    def toggle_radio_button(self):
        if self.radio_state:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: red;
                            border-radius: 5px;
                        }
                    """)
        else:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: blue;
                            border-radius: 5px;
                        }
                    """)
        self.radio_state = not self.radio_state


class Load_test_scenario_thread(QtCore.QThread):
    send_scenario_update_ui_sig = QtCore.pyqtSignal(int, dict)
    send_max_scenario_cnt_sig = QtCore.pyqtSignal(int)
    send_finish_scenario_update_ui_sig = QtCore.pyqtSignal()

    def __init__(self, base_dir, context_split):
        super().__init__()
        self.base_dir = base_dir
        self.context_split = context_split

    def run(self):
        # scenario_path = os.path.join(self.base_dir, "scenario", "scenarios.json")
        scenario_path = self.base_dir
        with open(scenario_path, 'r') as file:
            scenarios = json.load(file)

        #############################################
        """
        comment: 초기 평가 툴 구현 할 때 contexts 구조는 아래처럼 2차원 리스트 타입으로 가정하고 설계를 했음.
                 그런데 ts_rag_tool에서 data set을 만들 때 1차원 리스트로 만들어 주고 있음.
                 그래서 아래처럼 1차원 리스트 구조를 2차원 리스트를 갖는 구조로 임시 파일을 만들어 해당 파일
                 기준으로 data 추출하고 이렇게 임시로 만들어 놓은 파일은 곧바로 삭제함으로써 기존 구조를 변경하지
                 않고 ts-rag-tool에서 만든 구조를 그대로 사용할 수 있음: 20240927 수정  
        {
        "question": "",
        "contexts": [[]],
        "ground_truth": "",   
        "answer": ""
        }
        """

        # 각 데이터의 "contexts"를 [[]] 타입으로 변경
        for item in scenarios:
            if isinstance(item.get("contexts"), list):
                # 기존 contexts가 리스트일 경우, 그 내부를 [[]] 형식으로 감싸기
                item["contexts"] = [item["contexts"]]

        # 변경된 데이터를 새로운 파일로 저장
        # scenario_path = os.path.join(self.base_dir, "scenario", "temp_scenarios.json")

        folder_path, file_name = os.path.split(self.base_dir)
        scenario_path = os.path.join(folder_path, "temp_scenarios.json")

        with open(scenario_path, 'w', encoding='utf-8') as file:
            json.dump(scenarios, file, indent=4)

        with open(scenario_path, 'r') as file:
            scenarios = json.load(file)

        os.remove(scenario_path)
        #############################################

        self.send_max_scenario_cnt_sig.emit(len(scenarios) + 1)

        for idx, scenario in enumerate(scenarios):
            question_data = scenario["question"]
            contexts = self.context_split.join(scenario["contexts"][0])
            # contexts = self.context_split.join(scenario["contexts"])
            answer = scenario["answer"]
            ground_truth = scenario["ground_truth"]

            scenario_data = {
                "question": question_data,
                "contexts": contexts,
                "answer": answer,
                "ground_truth": ground_truth,
                "idx": idx
            }

            self.send_scenario_update_ui_sig.emit(idx, scenario_data)

        self.send_finish_scenario_update_ui_sig.emit()


#######################################################################################
def call_metric_function(model, scenario_data, max_iter, measuring_method, thread):
    score = 0

    if "ragas" not in model.lower():
        score = common_llm_model(model=model, scenario_data=scenario_data, max_iter=max_iter, method=measuring_method,
                                 thread=thread)

    elif "ragas" in model.lower():
        score = common_ragas_metric_model(model=model, scenario_data=scenario_data, max_iter=max_iter,
                                          method=measuring_method, thread=thread)

    else:
        print("Warning: No Supported Metric Model")
    return model, score


def evaluate_model(args):
    scenario_data, model, metrics, idx, cnt, max_iter, measuring_method, thread = args
    model_name, score = call_metric_function(model=model, scenario_data=scenario_data, max_iter=max_iter,
                                             measuring_method=measuring_method, thread=thread)
    result = {
        "model": str(model_name),
        "metric": None,
        "score": str(score),
        "idx": idx,
        "cnt": cnt
    }
    return result


class Metric_Evaluation_Thread(QThread):
    send_progress_status = pyqtSignal(list)
    send_network_error_sig = pyqtSignal(str)

    def __init__(self, max_cnt, sub_widget, model, parent, main_frame, openai_model):
        super().__init__()
        self.working = True
        self.max_cnt = max_cnt
        self.sub_widget = sub_widget
        self.model = model
        self.openai_model = openai_model
        self.parent = parent
        self.progress = 0
        self.method = None

        if main_frame.iqr_median_radioButton.isChecked():
            self.method = "IQR-MEDIAN"
        elif main_frame.iqr_mean_radioButton.isChecked():
            self.method = "IQR-MEAN"
        elif main_frame.mean_radioButton.isChecked():
            self.method = "MEAN"

    def run(self):
        self.progress = 0

        for idx, (widget_ui, widget_ui_instance) in enumerate(self.sub_widget):
            if not self.working:
                break

            if widget_ui.scenario_checkBox.isChecked():
                scenario_data = {
                    "question": widget_ui.question_plainTextEdit.toPlainText(),
                    "contexts": widget_ui.contexts_plainTextEdit.toPlainText(),
                    "answer": widget_ui.answer_plainTextEdit.toPlainText(),
                    "ground_truth": widget_ui.truth_plainTextEdit.toPlainText()
                }
                # print("===============================================")
                # print(scenario_data)
                # print("===============================================")

                for cnt, (model, metrics) in enumerate(self.model.items()):
                    if not self.working:
                        break

                    checkbox = self.parent.findChild(QtWidgets.QCheckBox, f"metric_{model}_{cnt}")
                    if checkbox.isChecked():
                        try:
                            result = evaluate_model(
                                (scenario_data, model, metrics, idx, cnt, self.parent.max_iter, self.method, self))

                            result['widget_ui'] = widget_ui
                            result['widget_ui_instance'] = widget_ui_instance
                            self.progress += 1
                            self.send_progress_status.emit([self.progress, self.max_cnt, result, model])

                        except Exception as e:
                            self.send_network_error_sig.emit(
                                f"Error in common_ragas_metric_model for model {model}: {e}")

    def stop(self):
        # print("Evaluation Stop")
        self.working = False
        self.quit()
        self.wait(3000)


class Performance_metrics_MainWindow(QtWidgets.QMainWindow):
    send_sig_delete_all_sub_widget = pyqtSignal()
    send_save_finished_sig = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.directory = None
        self.start_evaluation_time = None
        self.end_evaluation_time = None
        self.added_scenario_widgets = None
        self.update_thread = None
        self.update_evaluation_progress = None
        self.update_sub_widget_progress = None
        self.eval_thread = None
        self.save_thread = None
        self.save_progress = None
        self.max_iter = None
        self.openai_model = None
        self.create_testset_thread = None
        self.create_testset_progress = None
        self.openaikey = None
        self.open_scenario_file = None

        """ for main frame & widget """
        self.mainFrame_ui = None
        self.widget_ui = None

        self.setupUi()

        # QProcess 객체 생성
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

    def handle_stdout(self):
        output = self.process.readAllStandardOutput().data().decode()
        print(output)

    def handle_stderr(self):
        error = self.process.readAllStandardError().data().decode()
        if len(error) != 0:
            print(f"Error: {error}")

    def setupUi(self):
        # Load the main window's UI module
        rt = load_module_func(module_name="ui_designer.main_frame")
        self.mainFrame_ui = rt.Ui_MainWindow()
        self.mainFrame_ui.setupUi(self)

        self.main_frame_init_ui()

        self.setWindowTitle(Version_)

    def get_OpenAIKey(self):
        self.openaikey = self.mainFrame_ui.opeanaikey1.text() + self.mainFrame_ui.opeanaikey2.text()
        return self.openaikey

    def main_frame_init_ui(self):
        for idx, (model, metric) in enumerate(Models.items()):
            checkbox = QtWidgets.QCheckBox(self)
            checkbox.setObjectName(f"metric_{model}_{idx}")
            checkbox.setText(model)
            self.mainFrame_ui.verticalLayout_5.addWidget(checkbox)

        # s_path = os.path.join(BASE_DIR, "scenario", "scenarios.json")
        # self.mainFrame_ui.scenario_path_lineedit.setText(s_path)
        # self.mainFrame_ui.scenario_path_lineedit.setReadOnly(True)

    def closeEvent(self, event):
        answer = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit?\nAll data will be lost.",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if answer == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def normalOutputWritten(self, text):
        cursor = self.mainFrame_ui.logtextbrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        color_format = cursor.charFormat()
        if "><" in text:
            color_format.setForeground(QtCore.Qt.red)
        else:
            color_format.setForeground(QtCore.Qt.black)

        cursor.setCharFormat(color_format)
        cursor.insertText(text)

        self.mainFrame_ui.logtextbrowser.setTextCursor(cursor)
        self.mainFrame_ui.logtextbrowser.ensureCursorVisible()

    def cleanLogBrowser(self):
        self.mainFrame_ui.logtextbrowser.clear()

    def connectSlotSignal(self):
        """ sys.stdout redirection """
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.mainFrame_ui.log_clear_pushButton.clicked.connect(self.cleanLogBrowser)

        self.mainFrame_ui.all_check_model.clicked.connect(self.model_check)
        self.mainFrame_ui.all_uncheck_model.clicked.connect(self.model_check)

        self.mainFrame_ui.open_pushButton.clicked.connect(self.open_test_set)
        self.mainFrame_ui.refresh_pushButton.clicked.connect(self.remove_all_sub_widget)
        self.send_sig_delete_all_sub_widget.connect(self.update_all_sub_widget)

        self.mainFrame_ui.all_check_scenario.clicked.connect(self.select_all_scenario)
        self.mainFrame_ui.all_uncheck_scenario.clicked.connect(self.select_all_scenario)

        self.mainFrame_ui.analyze_pushButton.clicked.connect(self.t_start_evaluation)
        self.mainFrame_ui.save_pushButton.clicked.connect(self.save_analyze_data)
        self.mainFrame_ui.reset_score_pushButton.clicked.connect(self.reset_all_score)

        self.send_save_finished_sig.connect(self.finished_all_test_result_save)

        self.mainFrame_ui.dirpushButton.clicked.connect(self.open_dir)
        self.mainFrame_ui.gengenpushButton.clicked.connect(self.test_set_creation)
        self.mainFrame_ui.gensavepushButton.hide()  # clicked.connect(self.save_gen)

    def open_dir(self):
        self.directory = easygui.diropenbox()

        # Print the selected directory
        if self.directory is None:
            return

        self.mainFrame_ui.dirlineEdit.setText(self.directory)

    def test_set_creation(self):
        if self.directory is None:
            answer = QtWidgets.QMessageBox.warning(self,
                                                   "Directory Check...",
                                                   "Choose a directory for test-set",
                                                   QtWidgets.QMessageBox.Yes)
            print("Empty Directory")
            return

        self.start_test_set_creation()

    def start_test_set_creation(self):
        # Fetch all .md files from the current directory and subdirectories
        test_size_ = int(self.mainFrame_ui.n_lineEdit.text())
        simple_ = float(self.mainFrame_ui.simplelineEdit.text())
        reasoning_ = float(self.mainFrame_ui.reasonlineEdit.text())
        multi_context_ = float(self.mainFrame_ui.multilineEdit.text())

        if self.mainFrame_ui.creation_gpt4o_radioButton.isChecked():
            model = "gpt-4o"
            print("creation model", model)
        elif self.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
            model = "gpt-4o-mini"
            print("creation model", model)
        else:
            model = "gpt-3.5-turbo-16k"
            print("creation model", model)

        # 실행할 파이썬 파일 경로와 전달할 인자들
        script_path = 'cli_test_set_creator.py'  # test_set_Creator.py 경로

        # 다른 변수들도 문자열로 변환
        source_dir = str(self.directory)
        test_size_str = str(test_size_)
        simple_str = str(simple_)
        reasoning_str = str(reasoning_)
        multi_context_str = str(multi_context_)
        model_str = str(model)

        # 인자로 넘길 리스트 (모두 문자열이어야 함)
        arguments = [script_path, source_dir, test_size_str, simple_str, reasoning_str, multi_context_str, model_str,
                     self.get_OpenAIKey()]

        # QProcess로 파이썬 스크립트를 인자와 함께 실행
        self.process.start(sys.executable, arguments)

    def select_all_scenario(self):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        sender = self.sender()
        check = False

        if sender:
            if sender.objectName() == "all_check_scenario":
                check = True
            elif sender.objectName() == "all_uncheck_scenario":
                check = False

        for scenario_widget, scenario_widget_instance in self.added_scenario_widgets:
            scenario_widget.scenario_checkBox.setChecked(check)

    def model_check(self):
        PRINT_("model check")
        sender = self.sender()
        check = False

        if sender:
            if sender.objectName() == "all_check_model":
                check = True
            elif sender.objectName() == "all_uncheck_model":
                check = False

        for idx, (model, metric) in enumerate(Models.items()):
            checkbox = self.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")
            if checkbox:
                checkbox.setChecked(check)

    def open_test_set(self):
        file_path = easygui.fileopenbox(
            msg="Select Test Set Scenario",
            title="Test Set Selection",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            return

        self.open_scenario_file = file_path
        self.mainFrame_ui.scenario_path_lineedit.setText(self.open_scenario_file)
        # self.mainFrame_ui.scenario_path_lineedit.setReadOnly(True)
        # print(self.open_scenario_file)
        self.remove_all_sub_widget()  # remove all widget and update with new imported scenario

    def remove_all_sub_widget(self):
        if self.open_scenario_file is None or len(self.mainFrame_ui.scenario_path_lineedit.text()) == 0:
            return

        while self.mainFrame_ui.formLayout.count():
            item = self.mainFrame_ui.formLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.send_sig_delete_all_sub_widget.emit()

    def add_scenario_widget(self, idx, scenario_data):
        rt = load_module_func(module_name="ui_designer.main_widget")
        widget_ui = rt.Ui_Form()
        widget_instance = QtWidgets.QWidget()
        widget_ui.setupUi(widget_instance)

        widget_ui.scenario_checkBox.setText(f"scenario_{idx + 1}")
        widget_ui.question_plainTextEdit.setPlainText(scenario_data["question"])
        widget_ui.contexts_plainTextEdit.setPlainText(scenario_data["contexts"])
        widget_ui.answer_plainTextEdit.setPlainText(scenario_data["answer"])
        widget_ui.truth_plainTextEdit.setPlainText(scenario_data["ground_truth"])

        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)

        cnt = 0

        def draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name, is_sub=False):
            label = QtWidgets.QLabel(widget_ui.groupBox_2)
            label.setFont(font)
            label.setObjectName(f"label_{idx}_{cnt}")
            label.setText(obj_name)
            widget_ui.formLayout.setWidget(cnt, QtWidgets.QFormLayout.LabelRole, label)

            if not is_sub:
                score_line = QtWidgets.QLineEdit(widget_ui.groupBox_2)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(score_line.sizePolicy().hasHeightForWidth())
                score_line.setSizePolicy(sizePolicy)
                score_line.setMaximumSize(QtCore.QSize(75, 16777215))
                score_line.setFont(font)
                score_line.setObjectName(f"score_line_{idx}_{cnt}")
                widget_ui.formLayout.setWidget(cnt, QtWidgets.QFormLayout.FieldRole, score_line)

        for model, metrics in Models.items():
            if metrics is None:
                draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=model)
                cnt += 1
            else:
                draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=model, is_sub=True)
                cnt += 1
                for sub_metric in metrics:
                    draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=sub_metric)
                    cnt += 1

        self.added_scenario_widgets.append((widget_ui, widget_instance))
        self.mainFrame_ui.formLayout.setWidget(idx, QtWidgets.QFormLayout.FieldRole, widget_instance)

        if self.update_sub_widget_progress is not None:
            self.update_sub_widget_progress.onCountChanged(idx)

    def set_max_progressbar_cnt(self, value):
        if self.update_sub_widget_progress is not None:
            # PRINT_("max value", value)
            self.update_sub_widget_progress.setProgressBarMaximum(max_value=value)

    def finished_add_scenario_widget(self):
        if self.update_sub_widget_progress is not None:
            # PRINT_("finished_add_scenario_widget")
            self.update_sub_widget_progress.close()

    def start_save_analyze_data(self):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        file_path = easygui.filesavebox(
            msg="Want to Save File?",
            title="Saving File",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            self.send_save_finished_sig.emit()
            return

        if not file_path.endswith(".json"):
            file_path += ".json"

        output_data = []
        progress = 0

        for idx, (widget_ui, widget_ui_instance) in enumerate(self.added_scenario_widgets):
            progress += 1
            self.save_progress.onCountChanged(progress % 99)

            result_out = {}

            result_out = {"question": widget_ui.question_plainTextEdit.toPlainText(),
                          "contexts": widget_ui.contexts_plainTextEdit.toPlainText().split(g_context_split),
                          "ground_truth": widget_ui.truth_plainTextEdit.toPlainText(),
                          "answer": widget_ui.answer_plainTextEdit.toPlainText(),
                          "score": ""
                          }

            score_dict = {}
            for cnt, (model, metric) in enumerate(Models.items()):
                score_line = widget_ui_instance.findChild(QtWidgets.QLineEdit, f"score_line_{idx}_{cnt}")
                if score_line and score_line.text() != "":
                    score_dict[Rag_Models_Metric[model].name] = float(score_line.text())
                    # result_out[model] = score_line.text()

            result_out["score"] = score_dict
            output_data.append(result_out)

        self.save_progress.onCountChanged(100)
        QThread.sleep(1)

        with open(file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)

        # self.converter_json2csv(file_path)

        self.send_save_finished_sig.emit()

    @staticmethod
    def converter_json2csv(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # CSV 파일 저장
        # 첫 번째 항목에서 key들을 자동으로 가져옴
        for cnt in range(0, len(data)):
            if len(list(data[cnt].keys())) == 0:
                continue
            csv_columns = list(data[cnt].keys())
            break

        csv_columns.remove("score")  # score는 제거
        # score에 있는 key를 가져와 추가
        score_keys = list(data[0]["score"].keys())
        csv_columns.extend(score_keys)

        csv_file = file_path.replace("json", "csv")

        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()

                for entry in data:
                    # contexts 리스트를 문자열로 변환
                    entry["contexts"] = "\n".join(entry["contexts"])

                    # score를 개별 필드로 분리
                    for key in score_keys:
                        entry[key] = entry["score"].get(key)

                    # score 필드 자체는 제거
                    del entry["score"]

                    writer.writerow(entry)

            print(f"CSV 파일이 성공적으로 저장되었습니다: {csv_file}")

        except IOError:
            print("CSV 파일 저장 중 오류가 발생했습니다.")

    def finished_all_test_result_save(self):
        if self.save_progress is not None:
            self.save_progress.close()

    def save_analyze_data(self):
        PRINT_("save_analyze_data")

        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        if self.mainFrame_ui.popctrl_radioButton.isChecked():
            self.save_progress = ModalLess_ProgressDialog(message="Saving Result ...")
        else:
            self.save_progress = Modal_ProgressDialog(message="Saving Result ...")

        self.save_thread = threading.Thread(target=self.start_save_analyze_data, daemon=True)
        self.save_thread.start()

        self.save_progress.showModal_less()

    def update_all_sub_widget(self):
        # PRINT_("add_scenario_in_subwidget")

        if self.mainFrame_ui.popctrl_radioButton.isChecked():
            self.update_sub_widget_progress = ModalLess_ProgressDialog(message="Loading Scenario")
        else:
            self.update_sub_widget_progress = Modal_ProgressDialog(message="Loading Scenario")

        self.added_scenario_widgets = []
        # self.update_thread = Load_test_scenario_thread(BASE_DIR, g_context_split)
        self.update_thread = Load_test_scenario_thread(self.open_scenario_file, g_context_split)
        self.update_thread.send_scenario_update_ui_sig.connect(self.add_scenario_widget)
        self.update_thread.send_max_scenario_cnt_sig.connect(self.set_max_progressbar_cnt)
        self.update_thread.send_finish_scenario_update_ui_sig.connect(self.finished_add_scenario_widget)

        self.update_thread.start()

        self.update_sub_widget_progress.showModal_less()

    def check_warning_message(self):
        if self.added_scenario_widgets is None:
            return

        scenario_exist = False
        for widget, widget_instance in self.added_scenario_widgets:
            if widget.scenario_checkBox.isChecked():
                scenario_exist = True
                break

        if not scenario_exist:
            answer = QtWidgets.QMessageBox.warning(self,
                                                   "Warning",
                                                   "Select scenario",
                                                   QtWidgets.QMessageBox.Ok)
            return False

        metric_exist = False
        for idx, (model, metric) in enumerate(Models.items()):

            checkbox = self.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")

            if checkbox.isChecked():
                metric_exist = True
                break

        if not metric_exist:
            answer = QtWidgets.QMessageBox.warning(self,
                                                   "Warning",
                                                   "Select metric",
                                                   QtWidgets.QMessageBox.Ok)
            return False

        return True

    def reset_all_score(self):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        for widget_ui, widget_ui_instance in self.added_scenario_widgets:
            # Find all QLineEdit widgets within the current scenario widget
            line_edits = widget_ui_instance.findChildren(QtWidgets.QLineEdit)
            for line_edit in line_edits:
                line_edit.setText("")

    def total_test_cnt(self):
        selected_scenario_cnt = 0
        for scenario_widget, scenario_widget_instance in self.added_scenario_widgets:
            if scenario_widget.scenario_checkBox.isChecked():
                selected_scenario_cnt += 1

        selected_metric_cnt = 0
        for idx, (model, metric) in enumerate(Models.items()):
            checkbox = self.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")
            if checkbox.isChecked():
                if metric is None:
                    selected_metric_cnt += 1
                else:
                    selected_metric_cnt += len(metric)

        # PRINT_(selected_scenario_cnt, selected_metric_cnt, selected_metric_cnt * selected_scenario_cnt)

        return selected_metric_cnt * selected_scenario_cnt

    def evaluation_error(self, event):
        if self.eval_thread is not None:
            self.eval_thread.stop()

        if self.update_evaluation_progress is not None:
            self.update_evaluation_progress.close()

        answer = QtWidgets.QMessageBox.warning(self,
                                               "Evaluation Error - Network Error",
                                               f"{event}",
                                               QtWidgets.QMessageBox.Ok)

    def update_evaluation_progress_status(self, event):
        if self.eval_thread is not None:
            # print(event[0], event[1], event[2])

            # 결과 업데이트
            result = event[2]
            widget_ui = result["widget_ui"]
            widget_ui_instance = result["widget_ui_instance"]
            score = result["score"]
            idx = result["idx"]
            cnt = result["cnt"]

            score_line = widget_ui_instance.findChild(QtWidgets.QLineEdit, f"score_line_{idx}_{cnt}")

            if score_line:
                score_line.setText(score)

            # 프로그래스 바 업데이트
            if int(event[0]) != int(event[1]):
                if self.update_evaluation_progress is not None:
                    self.update_evaluation_progress.onCountChanged(value=str(event[0]))
                    self.update_evaluation_progress.onProgressTextChanged(
                        text=f"\nScenario: {widget_ui.scenario_checkBox.text()}\nModel: {event[3]}\nProgress: {event[0]}/{event[1]}")

            else:
                self.end_evaluation_time = time.time()
                elapsed_time = self.end_evaluation_time - self.start_evaluation_time
                days = elapsed_time // (24 * 3600)
                remaining_secs = elapsed_time % (24 * 3600)
                hours = remaining_secs // 3600
                remaining_secs %= 3600
                minutes = remaining_secs // 60
                seconds = remaining_secs % 60

                total_time = f"{int(days)}day {int(hours)}h {int(minutes)}m {int(seconds)}s"

                self.eval_thread.stop()
                self.update_evaluation_progress.close()

                answer = QtWidgets.QMessageBox.information(self,
                                                           "Metric Evaluation",
                                                           f"All Test Done !       \nElapsed time: {total_time}",
                                                           QtWidgets.QMessageBox.Ok)

    def t_start_evaluation(self):
        if not self.check_warning_message():
            return

        self.max_iter = int(self.mainFrame_ui.max_iter_spinBox.text())
        max_cnt = self.total_test_cnt()

        if self.mainFrame_ui.gpt4o_radioButton.isChecked():
            self.openai_model = "gpt-4o"
        elif self.mainFrame_ui.gpt4omini_radioButton.isChecked():
            self.openai_model = "gpt-4o-mini"
        else:
            self.openai_model = "gpt-3.5-turbo-16k"

        self.reset_all_score()

        if self.mainFrame_ui.popctrl_radioButton.isChecked():
            self.update_evaluation_progress = ModalLess_ProgressDialog(message="Evaluation ...", show=True)
        else:
            self.update_evaluation_progress = Modal_ProgressDialog(message="Evaluation ...", show=True)

        self.update_evaluation_progress.setProgressBarMaximum(max_value=max_cnt)

        self.eval_thread = Metric_Evaluation_Thread(max_cnt=max_cnt, sub_widget=self.added_scenario_widgets,
                                                    model=Models, parent=self, main_frame=self.mainFrame_ui,
                                                    openai_model=self.openai_model)

        self.eval_thread.send_progress_status.connect(self.update_evaluation_progress_status)
        self.eval_thread.send_network_error_sig.connect(self.evaluation_error)

        # eval 중 사용자가 취소하고 싶을 때
        self.update_evaluation_progress.send_user_close_event.connect(self.eval_thread.stop)

        self.eval_thread.start()

        self.start_evaluation_time = time.time()

        self.update_evaluation_progress.showModal_less()


if __name__ == "__main__":
    import sys

    g_context_split = ""
    g_context_split = "<split>"
    # view_only_ragas = False

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = Performance_metrics_MainWindow()
    ui.showMaximized()
    ui.connectSlotSignal()

    os.environ["OPENAI_API_KEY"] = ui.get_OpenAIKey()

    sys.exit(app.exec_())
