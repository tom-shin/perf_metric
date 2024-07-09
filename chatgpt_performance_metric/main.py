import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import time
import threading
import json
import easygui
import pandas as pd

from sentence_transformers import SentenceTransformer, util
from datasets import Dataset
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, \
    answer_similarity, answer_correctness
from ragas import evaluate

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog

pd.set_option('display.max_rows', None)  # 모든 행을 출력
pd.set_option('display.max_columns', None)  # 모든 열을 출력
pd.set_option('display.width', None)  # 출력 너비를 제한하지 않음
pd.set_option('display.max_colwidth', None)  # 각 열의 최대 너비를 제한하지 않음

os.environ["OPENAI_API_KEY"] = ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "scenario", "version.txt")
with open(file_path, "r") as file_:
    Version_ = file_.readline()


def load_module_func(module_name):
    mod = __import__(f"{module_name}", fromlist=[module_name])
    return mod


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass


class ProgressDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.label = None
        self.progressBar = None
        self.setupUi()

    def setupUi(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 30, 251, 16))
        self.label.setObjectName("label")
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setGeometry(QtCore.QRect(40, 60, 611, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Loading Scenarios"))
        self.label.setText(_translate("Dialog", "Loading Scenario ..."))

        QtCore.QMetaObject.connectSlotsByName(self)

        # """ Remove '?' 'X' marks in QDialog box """
        # self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        # self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    def setProgressBarMaximum(self, max_value):
        self.progressBar.setMaximum(max_value)

    def onProgressChanged(self, progress):
        self.label.setText(progress)

    def onCountChanged(self, value):
        self.progressBar.setValue(value)

    def showModal(self):
        super().exec_()

    def showModaless(self):
        super().show()


class load_scenario(QThread):
    send_scenario_data_sig = pyqtSignal(dict)
    send_read_scenario_progress_sig = pyqtSignal(int)
    send_max_scenario_count = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        scenario_path = os.path.join(BASE_DIR, "scenario", "scenarios.json")
        # Load the JSON data from the file
        with open(scenario_path, 'r') as file:
            scenarios = json.load(file)

        cell_data = {}

        max_count = len(scenarios) + 1
        self.send_max_scenario_count.emit(max_count)

        for num_scenario, scenario in enumerate(scenarios):
            question_data = scenario["question"]

            contexts = g_context_split.join(scenario["contexts"][0])
            # contexts = g_context_split.join(
            #     [context for sublist in scenario["contexts"] for context in sublist])  # Flatten and join contexts

            answer = scenario["answer"]
            ground_truth = scenario["ground_truth"]

            self.send_read_scenario_progress_sig.emit(num_scenario % 100)

            # new /n, /r/n 와 같은 new line도 입력 그대로 넣음
            cell_data[num_scenario] = {
                "question": question_data,
                "contexts": contexts,
                "ground_truth": ground_truth,
                "answer": answer
            }

        self.send_read_scenario_progress_sig.emit(max_count)
        self.send_scenario_data_sig.emit(cell_data)

    def stop(self):
        self.quit()
        self.wait(3000)


class Cal_Model_Score:
    def __init__(self, question, context, answer, ground_truth, model):
        self.question = question
        self.context = context.split(g_context_split)  # contexts는 <split>로 구분하도록 했음. 상황에 맞혀 변경이 필요할 수 도...
        self.answer = answer
        self.ground_truth = ground_truth
        self.model = model

    def Ragas_ALG(self):
        # ragas에서 인식할 수 있는 format으로 변경 
        data_samples = {
            'question': [self.question],
            'contexts': [self.context],
            'answer': [self.answer],
            'ground_truth': [self.ground_truth]
        }

        print(data_samples)
        print("\n")

        dataset = Dataset.from_dict(data_samples)

        if view_only_ragas:
            metric = [faithfulness, answer_correctness]
        else:
            metric = [faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall,
                      answer_similarity, answer_correctness]

        score = evaluate(dataset, metrics=metric)

        if view_only_ragas:
            result = {
                "faithfulness": str(round(score["faithfulness"], 5)),
                "answer_correctness": str(round(score["answer_correctness"], 5))
            }
        else:
            result = {
                "faithfulness": str(round(score["faithfulness"], 5)),
                "answer_relevancy": str(round(score["answer_relevancy"], 5)),
                "context_precision": str(round(score["context_precision"], 5)),
                "context_recall": str(round(score["context_recall"], 5)),
                "context_entity_recall": str(round(score["context_entity_recall"], 5)),
                "answer_similarity": str(round(score["answer_similarity"], 5)),
                "answer_correctness": str(round(score["answer_correctness"], 5))
            }

        return result

    def LLM_MODEL_ALG(self):
        local_model_dir = os.path.join(BASE_DIR, "local_models", self.model)
        model = SentenceTransformer(local_model_dir)

        # 문장 임베딩 생성
        embedding1 = model.encode(self.answer, convert_to_tensor=True)
        embedding2 = model.encode(self.ground_truth, convert_to_tensor=True)

        # 코사인 유사도 계산
        cosine_score = util.pytorch_cos_sim(embedding1, embedding2)
        # cosine_score = util.cos_sim(embedding1, embedding2)

        result = {
            "model": str(self.model),
            "score": str(round(cosine_score.item(), 5))
        }

        return result


class Chatbot_MainWindow(QtWidgets.QMainWindow):
    signal_reset_score = pyqtSignal()
    signal_send_score = pyqtSignal(object, dict, str)
    signal_send_save_finished = pyqtSignal()

    signal_send_save_status = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        """ for main frame & widget """
        self.mainFrame_ui = None
        self.widget_ui = None

        "main frame에 평가할 models의 갯수"
        self.const_num_total_algo = 7

        "기타 일반 변수"
        self.scenario_data = None
        self.store_inserted_widget = []
        self.received_sig_cnt = 0
        self.progress = None
        self.save_thread = None
        self.cal_thread = None
        # widget별로 thread를 돌리려고함. 어떤 widget를 thread로 돌리는지 확인하고자 아래 변수 사용
        self.widget_thread = []

        self.setupUi()

    def setupUi(self):
        # Load the main window's UI module
        rt = load_module_func(module_name="ui_designer.main_frame")
        self.mainFrame_ui = rt.Ui_MainWindow()
        self.mainFrame_ui.setupUi(self)

        """ default golden data path """
        local_path_ = os.path.join(BASE_DIR, "scenario", "scenarios.json")
        self.mainFrame_ui.golden_lineEdit.setText(local_path_)
        self.mainFrame_ui.golden_lineEdit.setReadOnly(True)

        self.setWindowTitle(Version_)

        if view_only_ragas:
            for i in range(1, 7):  # 여러개 다른 llm 모델 hide
                label_name = f"alg_checkBox_{i}"
                label = getattr(self.mainFrame_ui, label_name, None)
                if label is not None:
                    label.hide()
            self.mainFrame_ui.allcheck_pushButton.hide()  # all check 버턴 숨기기
            self.mainFrame_ui.alluncheck_pushButton.hide()  # all uncheck 버턴 숨기기
            self.mainFrame_ui.alg_checkBox_7.setChecked(True)  # ragas default로 check

    def closeEvent(self, event):
        answer = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit?\nAll data will be lost.",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if answer == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def connectSlotSignal(self):
        """ sys.stdout redirection """
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.mainFrame_ui.log_clear_pushButton.clicked.connect(self.cleanLogBrowser)

        self.mainFrame_ui.allcheck_pushButton.clicked.connect(self.algorithm_select)
        self.mainFrame_ui.alluncheck_pushButton.clicked.connect(self.algorithm_select)

        "시나리오 기반으로 시나리오 갯수만큼 sub widget 삽입"
        self.mainFrame_ui.refresh_pushButton.clicked.connect(self.update_all_sub_widget)
        self.mainFrame_ui.analyze_pushButton.clicked.connect(self.perform_analyze)
        self.mainFrame_ui.save_pushButton.clicked.connect(self.save_analyze_data)

        self.mainFrame_ui.scenario_allcheck_pushButton.clicked.connect(self.select_scenario_to)
        self.mainFrame_ui.scenario_alluncheck_pushButton.clicked.connect(self.select_scenario_to)

        self.signal_reset_score.connect(self.calculate_score)
        self.signal_send_score.connect(self.update_model_score)
        self.signal_send_save_finished.connect(self.save_finished)
        self.signal_send_save_status.connect(self.progress_save_status)

    def cleanLogBrowser(self):
        self.mainFrame_ui.logtextbrowser.clear()

    def normalOutputWritten(self, text):
        cursor = self.mainFrame_ui.logtextbrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        if " **" in text and "[" in text and "]" in text:
            endposition = cursor.position()
            startcursor = self.self.mainFrame_ui.logtextbrowser.textCursor()
            startcursor.movePosition(QtGui.QTextCursor.End)
            startcursor.movePosition(QtGui.QTextCursor.StartOfLine)
            startcursor.movePosition(QtGui.QTextCursor.Left)
            startposition = startcursor.position()

            diff = endposition - startposition
            for i in range(diff):
                startcursor.deleteChar()
        cursor.movePosition(QtGui.QTextCursor.End)

        color_format = cursor.charFormat()
        if 'score' in text.lower() or 'not clicked' in text.lower() or 'Image Info' in text or 'Set Verification' in text or "Failed" in text:
            color_format.setForeground(QtCore.Qt.red)
        elif "Test Start" in text or "Simulation Start" in text:
            color_format.setForeground(QtCore.Qt.blue)
        elif "Iter." in text:
            color_format.setForeground(QtCore.Qt.darkCyan)
        else:
            color_format.setForeground(QtCore.Qt.black)
        cursor.setCharFormat(color_format)

        if '*' in text:
            for t in text:
                if t == '*':
                    color_format.setForeground(QtCore.Qt.blue)
                else:
                    color_format.setForeground(QtCore.Qt.darkCyan)
                cursor.setCharFormat(color_format)
                cursor.insertText(t)
        else:
            cursor.insertText(text)

        self.mainFrame_ui.logtextbrowser.setTextCursor(cursor)
        self.mainFrame_ui.logtextbrowser.ensureCursorVisible()

    def main_frame_button_ctrl_disabled(self, flag=False):
        if flag:
            self.mainFrame_ui.analyze_pushButton.setEnabled(False)
            self.mainFrame_ui.refresh_pushButton.setEnabled(False)
        else:
            self.mainFrame_ui.analyze_pushButton.setEnabled(True)
            self.mainFrame_ui.refresh_pushButton.setEnabled(True)

    def select_scenario_to(self):
        if len(self.store_inserted_widget) == 0:
            return

        sender = self.sender()
        check = False

        if sender:
            if sender.objectName() == "scenario_allcheck_pushButton":
                check = True
            elif sender.objectName() == "scenario_alluncheck_pushButton":
                check = False

        for widget in self.store_inserted_widget:
            widget.scenario_checkBox.setChecked(check)

    def algorithm_select(self):
        sender = self.sender()
        check = False

        if sender:
            if sender.objectName() == "allcheck_pushButton":
                check = True
            elif sender.objectName() == "alluncheck_pushButton":
                check = False

        for num in range(self.const_num_total_algo):
            algo_checkbox = getattr(self.mainFrame_ui, f"alg_checkBox_{num + 1}")
            algo_checkbox.setChecked(check)

    def remove_all_widget_in_mainFrame(self):
        while self.mainFrame_ui.formLayout.count():
            item = self.mainFrame_ui.formLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def received_all_scenario(self, all_scenario_data):
        self.remove_all_widget_in_mainFrame()
        self.insert_all_sub_widget_to_main_frame(widget_contents=all_scenario_data)

        # 모든 시나리오를 읽어와 widget 구성 완료
        if self.progress is not None:
            self.progress.close()

    def insert_all_sub_widget_to_main_frame(self, widget_contents):
        # main frame에 시나리오 기반으로 sub widget을 insert
        self.store_inserted_widget = []

        # Load and insert widget
        for idx in range(len(widget_contents.keys())):
            rt = load_module_func(module_name="ui_designer.main_widget")
            widget_ui = rt.Ui_Form()
            widget_instance = QtWidgets.QWidget()
            widget_ui.setupUi(widget_instance)

            widget_ui.scenario_checkBox.setText(rf"Test_Scenario_#{idx}")

            """ widget에 text 입력 하기 """
            widget_ui.question_plainTextEdit.setPlainText(widget_contents[idx]["question"])
            widget_ui.contexts_plainTextEdit.setPlainText(widget_contents[idx]["contexts"])
            widget_ui.answer_plainTextEdit.setPlainText(widget_contents[idx]["answer"])
            widget_ui.truth_plainTextEdit.setPlainText(widget_contents[idx]["ground_truth"])

            if view_only_ragas:
                for i in range(1, 7):  # 여러개 다른 llm 모델 hide
                    label_name = f"label_{i}"
                    score_name = f"score_lineEdit_{i}"
                    label = getattr(widget_ui, label_name, None)
                    score = getattr(widget_ui, score_name, None)

                    if label is not None:
                        label.hide()
                        score.hide()

                for i in range(8, 13):  # 여러개 다른 llm 모델 hide
                    label_name = f"label_{i + 1}"
                    score_name = f"score_lineEdit_{i}"
                    label = getattr(widget_ui, label_name, None)
                    score = getattr(widget_ui, score_name, None)

                    if label is not None:
                        label.hide()
                        score.hide()

            self.store_inserted_widget.append(widget_ui)

            # Add the widget to the main window's form layout
            self.mainFrame_ui.formLayout.setWidget(idx, QtWidgets.QFormLayout.FieldRole, widget_instance)

    def update_model_score(self, widget, model_score, model_name):
        self.received_sig_cnt += 1

        if model_name != "Ragas":
            model_score = model_score["score"]

        if model_name == "all-MiniLM-L6-v2":
            widget.score_lineEdit_1.setText(model_score)

        elif model_name == "all-mpnet-base-v2":
            widget.score_lineEdit_2.setText(model_score)

        elif model_name == "paraphrase-MiniLM-L6-v2":
            widget.score_lineEdit_3.setText(model_score)

        elif model_name == "distiluse-base-multilingual-cased-v2":
            widget.score_lineEdit_4.setText(model_score)

        elif model_name == "paraphrase-mpnet-base-v2":
            widget.score_lineEdit_5.setText(model_score)

        elif model_name == "all-distilroberta-v1":
            widget.score_lineEdit_6.setText(model_score)

        elif model_name == "Ragas":

            if view_only_ragas:
                widget.score_lineEdit_7.setText(model_score["faithfulness"])
                widget.score_lineEdit_13.setText(model_score["answer_correctness"])
            else:
                widget.score_lineEdit_7.setText(model_score["faithfulness"])
                widget.score_lineEdit_8.setText(model_score["answer_relevancy"])
                widget.score_lineEdit_9.setText(model_score["context_precision"])
                widget.score_lineEdit_10.setText(model_score["context_recall"])
                widget.score_lineEdit_11.setText(model_score["context_entity_recall"])
                widget.score_lineEdit_12.setText(model_score["answer_similarity"])
                widget.score_lineEdit_13.setText(model_score["answer_correctness"])

        if self.received_sig_cnt == len(self.widget_thread):
            if self.progress is not None:
                self.progress.close()

            self.main_frame_button_ctrl_disabled(flag=False)

            answer = QtWidgets.QMessageBox.information(self,
                                                       "Verification",
                                                       "All Test Done !       ",
                                                       QtWidgets.QMessageBox.Ok)
        else:
            self.progress.onCountChanged(value=self.received_sig_cnt)
            self.progress.label.setText("Analyzing...Wait until all test done")

    def model_for_score_cal(self, widget, test_model):

        question = widget.question_plainTextEdit.toPlainText()
        context = widget.contexts_plainTextEdit.toPlainText()
        answer = widget.answer_plainTextEdit.toPlainText()
        ground_truth = widget.truth_plainTextEdit.toPlainText()

        # constructor
        selected_model = Cal_Model_Score(question=question, context=context, answer=answer, ground_truth=ground_truth,
                                         model=test_model)

        score = None
        if "Ragas" in test_model:
            score = selected_model.Ragas_ALG()

        else:
            score = selected_model.LLM_MODEL_ALG()

        self.signal_send_score.emit(widget, score, test_model)

    def cal_score_thread(self):

        print("[Start Cal Score]")
        self.widget_thread = []

        for widget in self.store_inserted_widget:
            if not widget.scenario_checkBox.isChecked():
                continue

            for idx in range(self.const_num_total_algo):
                checked_algo = getattr(self.mainFrame_ui, f"alg_checkBox_{idx + 1}")
                if checked_algo.isChecked():
                    _thread = threading.Thread(target=self.model_for_score_cal, args=(widget, checked_algo.text(),),
                                               daemon=True)
                    self.widget_thread.append(_thread)

        if len(self.widget_thread) != 0:
            self.main_frame_button_ctrl_disabled(flag=True)

        self.received_sig_cnt = 0

        self.progress.setProgressBarMaximum(max_value=len(self.widget_thread) + 1)
        for idx, thread_ in enumerate(self.widget_thread):
            thread_.start()
            thread_.join()

        self.progress.setProgressBarMaximum(max_value=len(self.widget_thread))

    def check_scenario_to_test(self):

        if len(self.store_inserted_widget) == 0:
            answer = QtWidgets.QMessageBox.warning(self,
                                                   "Scenario Check",
                                                   "No scenarios to analyze.",
                                                   QtWidgets.QMessageBox.Ok)

            if answer == QtWidgets.QMessageBox.Ok:
                return False

        else:
            exist = False
            for widget in self.store_inserted_widget:
                if widget.scenario_checkBox.isChecked():
                    exist = True
                    break

            if not exist:
                answer = QtWidgets.QMessageBox.warning(self,
                                                       "Scenario Check",
                                                       "Select Test Scenario",
                                                       QtWidgets.QMessageBox.Ok)

                if answer == QtWidgets.QMessageBox.Ok:
                    return False

            exist = False
            for idx in range(self.const_num_total_algo):
                checked_algo = getattr(self.mainFrame_ui, f"alg_checkBox_{idx + 1}")
                if checked_algo.isChecked():
                    exist = True
                    break

            if not exist:
                answer = QtWidgets.QMessageBox.warning(self,
                                                       "Model Check",
                                                       "Select Test Model",
                                                       QtWidgets.QMessageBox.Ok)

                if answer == QtWidgets.QMessageBox.Ok:
                    return False

        return True

    def calculate_score(self):

        if not self.check_scenario_to_test():
            return

        self.progress = ProgressDialog()
        self.progress.setWindowTitle("Analyze")
        self.progress.label.setText("Initializing for analysis. Wait...")

        self.cal_thread = threading.Thread(target=self.cal_score_thread, daemon=True)

        self.cal_thread.start()

        self.progress.showModal()

    def remove_previous_score(self):
        if not self.check_scenario_to_test():
            return

        include_ragas = 6  # ragas는 7개 sub 항목이 있어 아래처럼 전체를 지우기 위해서는 total algo + 6개 추가 필요 (최적화 나중에..)
        for widget in self.store_inserted_widget:
            for idx in range(self.const_num_total_algo + include_ragas):
                score = getattr(widget, f"score_lineEdit_{idx + 1}")
                score.setText("")

        self.signal_reset_score.emit()

    def perform_analyze(self):
        self.remove_previous_score()

    def update_all_sub_widget(self):
        # progress bar 시작
        self.progress = ProgressDialog()

        self.scenario_data = load_scenario()
        self.scenario_data.send_scenario_data_sig.connect(self.received_all_scenario)
        self.scenario_data.send_read_scenario_progress_sig.connect(self.progress.onCountChanged)
        self.scenario_data.send_max_scenario_count.connect(self.progress.setProgressBarMaximum)

        self.scenario_data.start()

        self.progress.showModal()

    def start_save_analyze_data(self):
        if len(self.store_inserted_widget) == 0:
            return

        # 파일 저장 대화 상자를 열고 .json 파일만 선택할 수 있도록 합니다.
        file_path = easygui.filesavebox(
            msg="Want to Save File?",
            title="Saving File",
            default="*.json",
            filetypes=["*.json"]
        )

        if not file_path:
            return

        if not file_path.endswith(".json"):
            file_path += ".json"

        output_data = {}
        num = 0
        for widget in self.store_inserted_widget:
            num += 1

            if self.progress is not None:
                self.signal_send_save_status.emit(num % 99)

            split_context = widget.contexts_plainTextEdit.toPlainText().split(g_context_split)

            # # Initialize the global_context list
            # global_context = []
            #
            # # Add each split string as a sublist to the global_context list
            # for s in split_context:
            #     global_context.append([s])

            if view_only_ragas:
                output_data[widget.scenario_checkBox.text()] = {
                    "question": widget.question_plainTextEdit.toPlainText(),
                    # "contexts": global_context,
                    "contexts": split_context,
                    "answer": widget.answer_plainTextEdit.toPlainText(),
                    "ground_truth": widget.truth_plainTextEdit.toPlainText(),

                    "Ragas": {
                        "faithfulness": widget.score_lineEdit_7.text(),
                        "answer_correctness": widget.score_lineEdit_13.text()
                    }
                }
            else:
                output_data[widget.scenario_checkBox.text()] = {
                    "question": widget.question_plainTextEdit.toPlainText(),
                    # "contexts": global_context,
                    "contexts": split_context,
                    "answer": widget.answer_plainTextEdit.toPlainText(),
                    "ground_truth": widget.truth_plainTextEdit.toPlainText(),

                    "all-MiniLM-L6-v2": widget.score_lineEdit_1.text(),
                    "all-mpnet-base-v2": widget.score_lineEdit_2.text(),
                    "paraphrase-MiniLM-L6-v2": widget.score_lineEdit_3.text(),
                    "distiluse-base-multilingual-cased-v2": widget.score_lineEdit_4.text(),
                    "paraphrase-mpnet-base-v2": widget.score_lineEdit_5.text(),
                    "all-distilroberta-v1": widget.score_lineEdit_6.text(),
                    "Ragas": {
                        "faithfulness": widget.score_lineEdit_7.text(),
                        "answer_relevancy": widget.score_lineEdit_8.text(),
                        "context_precision": widget.score_lineEdit_9.text(),
                        "context_recall": widget.score_lineEdit_10.text(),
                        "context_entity_recall": widget.score_lineEdit_11.text(),
                        "answer_similarity": widget.score_lineEdit_12.text(),
                        "answer_correctness": widget.score_lineEdit_13.text()
                    }
                }

        # JSON 데이터를 파일에 저장
        with open(file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)

        self.signal_send_save_finished.emit()

    def progress_save_status(self, num):
        if self.progress is not None:
            self.progress.onCountChanged(num)

    def save_finished(self):
        if self.progress is not None:
            self.progress.onCountChanged(value=100)
            app.processEvents()
            time.sleep(1)

            self.progress.close()

    def save_analyze_data(self):
        if len(self.store_inserted_widget) == 0:
            return

        self.progress = ProgressDialog()
        self.progress.setWindowTitle("Saving Scenario Output")
        self.progress.label.setText("Saving Scenario Output ...")

        self.save_thread = threading.Thread(target=self.start_save_analyze_data, daemon=True)
        self.save_thread.start()

        self.progress.showModal()


if __name__ == "__main__":
    import sys

    g_context_split = "<split>"
    view_only_ragas = True

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = Chatbot_MainWindow()
    ui.showMaximized()
    ui.connectSlotSignal()

    sys.exit(app.exec_())
