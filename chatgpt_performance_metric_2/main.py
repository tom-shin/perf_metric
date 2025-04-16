#!/usr/bin/env python3
import os.path

from PyQt5.QtCore import QThread
from PyQt5.QtGui import QBrush, QColor
from source.head import *
from source.source_files.TestSetCreationDir.testSetCreation import TestSetCreation
from source.source_files.ContextGenerationDir.contextGeneration import ContextGeneration_with_Trex_Ai_Chatbot_tools
from source.source_files.RagEvaluationDir.dataSetEvaluation import DataSetEvaluation

if getattr(sys, 'frozen', False):  # PyInstaller로 패키징된 경우
    BASE_DIR = os.path.dirname(sys.executable)  # 실행 파일이 있는 폴더
    RESOURCE_DIR = sys._MEIPASS  # 임시 폴더(내부 리소스 저장됨)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = BASE_DIR  # 개발 환경에서는 현재 폴더 사용


class LoadFiles(FileManager, QThread):
    LoadFiles_finished_file_list_signal = pyqtSignal(list)

    def __init__(self, dirpath, file_filter=None):
        super().__init__()
        self.dirpath = dirpath

        if file_filter is None:
            self.filter = []
        else:
            self.filter = file_filter

    def run(self):
        log_info("info", "File Loading ...")
        file_list = self.search_files(directory=self.dirpath, file_filter=self.filter)

        self.LoadFiles_finished_file_list_signal.emit(file_list)

    def stop(self):
        self.quit()
        self.wait(3000)


class LoadQuestion(FileManager, QThread):
    LoadQuestion_finished_list_signal = pyqtSignal(list)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        log_info("info", "Question Loading ...")
        _, data = self.load_json(file_path=self.filepath, use_encoding=False)

        question_list = [item["user_input"] for item in data if "user_input" in item]

        self.LoadQuestion_finished_list_signal.emit(question_list)

    def stop(self):
        self.quit()
        self.wait(3000)


class ProjectMainWindow(FileManager, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.testset_creation_file_list = None
        self.set_creation_prev_index = None
        self.context_gen_prev_index = None
        self.eval_prev_index = None

        # self.file_list = None
        self.mainFrame_ui = None
        self.widget_ui = None
        self.progress_dialog = None
        self.threadList = []
        self.finished_flag = False

        control_parameter_path = os.path.join(BASE_DIR, "control_parameter.json")

        # 만약 실행 폴더에 control_parameter.json이 없으면, 임시 폴더에서 복사
        if not os.path.exists(control_parameter_path):
            original_path = os.path.join(RESOURCE_DIR, "source", "control_parameter.json")
            shutil.copyfile(original_path, control_parameter_path)

        _, self.CONFIG_PARAMS = self.load_json(control_parameter_path, use_encoding=False)

        # 기존 UI 로드
        rt = load_module_func(module_name="source.ui_designer.main_frame")
        self.mainFrame_ui = rt.Ui_MainWindow()
        self.mainFrame_ui.setupUi(self)

        self.mainFrameInitialize()
        os.environ["OPENAI_API_KEY"] = "".join(self.CONFIG_PARAMS["openai"]["key"])

    def mainFrameInitialize(self):
        self.mainFrame_ui.n_lineEdit.setText(str(self.CONFIG_PARAMS["test_set_creation"]["test_size"]))
        self.mainFrame_ui.servercomboBox.addItems(self.CONFIG_PARAMS["context_generation"]["chatbot_server"])

        self.mainFrame_ui.clear_pushButton.hide()
        self.mainFrame_ui.iqr_mean_radioButton.hide()
        self.mainFrame_ui.iqr_median_radioButton.hide()
        self.mainFrame_ui.file_list_5.hide()
        self.mainFrame_ui.iter_spinBox.setValue(2)

    def closeEvent(self, event):
        answer = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if answer == QtWidgets.QMessageBox.Yes:
            for s_thread in self.threadList:
                s_thread.stop()

            event.accept()
        else:
            event.ignore()

    def ctrl_log_browser(self):
        """Show 또는 Hide 액션에 따라 QGroupBox 상태 변경"""
        sender = self.sender()  # 어떤 QAction이 호출되었는지 확인
        if sender.text() == "Show":
            self.mainFrame_ui.loggroupBox.show()
        else:
            self.mainFrame_ui.loggroupBox.hide()

    def normalOutputWritten(self, text):
        cursor = self.mainFrame_ui.logtextbrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        # 기본 글자 색상 설정
        color_format = cursor.charFormat()
        if "><" in text:
            color_format.setForeground(QtCore.Qt.red)
        else:
            color_format.setForeground(QtCore.Qt.black)

        cursor.setCharFormat(color_format)
        cursor.insertText(text)

        # 커서를 최신 위치로 업데이트
        self.mainFrame_ui.logtextbrowser.setTextCursor(cursor)
        self.mainFrame_ui.logtextbrowser.ensureCursorVisible()

    def cleanLogBrowser(self):
        self.mainFrame_ui.logtextbrowser.clear()

    def connectSlotSignal(self):
        """ sys.stdout redirection """
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.mainFrame_ui.log_clear_pushButton.clicked.connect(self.cleanLogBrowser)
        self.mainFrame_ui.gengenpushButton.clicked.connect(self.testSetCreation_job)
        self.mainFrame_ui.dirpushButton.clicked.connect(self.testSetCreation_doc_selection)
        # self.mainFrame_ui.clear_pushButton.clicked.connect(self.testSetCreation_erase_file_list)

        self.mainFrame_ui.contextgen_filepushButton.clicked.connect(self.contextGeneration_file_selection)
        self.mainFrame_ui.responsegenpushButton.clicked.connect(self.generateContext_job)

        self.mainFrame_ui.eval_filepushButton.clicked.connect(self.ragas_evaluation_file_selection)
        self.mainFrame_ui.eval_genpushButton.clicked.connect(self.ragas_evaluation_job)

        self.mainFrame_ui.actionShow.triggered.connect(self.ctrl_log_browser)
        self.mainFrame_ui.actionHide.triggered.connect(self.ctrl_log_browser)

    def testSetCreation_erase_file_list(self):
        self.mainFrame_ui.filelistlistWidget.clear()
        self.mainFrame_ui.creation_fail_filelistlistWidget.clear()
        self.mainFrame_ui.creation_fail_filenumlineEdit.clear()

    def color_ContextGeneration_list_widget_item(self, index):
        if self.context_gen_prev_index is not None:
            # 이전에 선택된 아이템 스타일 초기화
            prev_item = self.mainFrame_ui.questionlistlistWidget.item(self.context_gen_prev_index)
            if prev_item:
                prev_item.setBackground(QBrush(QColor("white")))  # 원래 색상으로 복원

            # 현재 인덱스 아이템 강조
        item = self.mainFrame_ui.questionlistlistWidget.item(index)
        if item:
            item.setBackground(QBrush(QColor("yellow")))  # 노란색 하이라이트 적용
            self.context_gen_prev_index = index  # 현재 선택된 인덱스를 저장

    def color_TestSetCreation_list_widget_item(self, index):
        if self.set_creation_prev_index is not None:
            # 이전에 선택된 아이템 스타일 초기화
            prev_item = self.mainFrame_ui.filelistlistWidget.item(self.set_creation_prev_index)
            if prev_item:
                prev_item.setBackground(QBrush(QColor("white")))  # 원래 색상으로 복원

            # 현재 인덱스 아이템 강조
        item = self.mainFrame_ui.filelistlistWidget.item(index)
        if item:
            item.setBackground(QBrush(QColor("yellow")))  # 노란색 하이라이트 적용
            self.set_creation_prev_index = index  # 현재 선택된 인덱스를 저장

    def update_TestSetCreation_Fail_list(self, fail_file, cnt):
        self.mainFrame_ui.creation_fail_filelistlistWidget.addItem(fail_file)
        self.mainFrame_ui.creation_fail_filenumlineEdit.setText(str(cnt))

    def finished_WorkThread(self):
        log_info("info", "finished_WorkThread")
        # self.mainFrame_ui.filelistlistWidget.clear()
        # self.mainFrame_ui.creation_fail_filelistlistWidget.clear()

        if self.progress_dialog is not None:
            self.progress_dialog.close()
            self.progress_dialog = None

        for thread in self.threadList:
            thread.stop()

    def testSetCreation_gui_set(self, file_list):
        log_info("info", "File Loading Done.")
        self.testset_creation_file_list = file_list
        self.mainFrame_ui.filelistlistWidget.addItems(file_list)
        self.mainFrame_ui.filenumlineEdit.setText(str(len(file_list)))

    def contextGeneration_gui_set(self, question_list):
        log_info("info", "Question Loading Done.")
        # self.file_list = question_list
        self.mainFrame_ui.questionlistlistWidget.addItems(question_list)
        self.mainFrame_ui.questionfilenumlineEdit.setText(str(len(question_list)))

    def testSetCreation_doc_selection(self):
        m_dir = QFileDialog.getExistingDirectory(self, "Select Directory")

        if not m_dir:
            return

        self.testSetCreation_erase_file_list()

        load_file_instance = LoadFiles(dirpath=m_dir, file_filter=self.CONFIG_PARAMS["filter"]["include"])
        load_file_instance.LoadFiles_finished_file_list_signal.connect(self.testSetCreation_gui_set)
        load_file_instance.start()

        self.threadList.append(load_file_instance)

        self.mainFrame_ui.dirlineEdit.setText(os.path.normpath(m_dir))

    def testSetCreation_job(self):
        if not self.mainFrame_ui.dirlineEdit.text().strip():
            print("Select Directory for TestSetCreation.")
            return

        self.progress_dialog = ProgressDialog(message="TestSet Creation", show_close_button=True, modal=self.mainFrame_ui.popctrl_radioButton.isChecked())
        self.progress_dialog.progress_stop_signal.connect(self.finished_WorkThread)

        test_size = self.CONFIG_PARAMS["test_set_creation"]["test_size"]

        if self.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
            gpt_model = "gpt-4o-mini"
        else:
            gpt_model = "gpt-4o"

        user = self.mainFrame_ui.userlineEdit.text().strip()

        ctrl_parm = {"file_list": self.testset_creation_file_list, "gpt_model": gpt_model, "test_size": test_size,
                     "user": user, "file_extension": self.CONFIG_PARAMS["filter"]["include"]}

        thread = TestSetCreation(ctrl_parm=ctrl_parm)
        thread.TestSetCreation_finished_thread_signal.connect(self.finished_WorkThread)
        thread.TestSetCreation_progress_signal.connect(self.progress_dialog.update_progress)
        thread.TestSetCreation_text_update_signal.connect(self.progress_dialog.update_text)
        thread.TestSetCreation_total_files_cnt_signal.connect(self.progress_dialog.set_progress_max)
        thread.TestSetCreation_creation_fail_file_signal.connect(self.update_TestSetCreation_Fail_list)
        thread.TestSetCreation_creation_update_list_widget_signal.connect(self.color_TestSetCreation_list_widget_item)

        thread.start()

        self.threadList.append(thread)

        self.progress_dialog.show_progress()

    def contextGeneration_erase_question_list(self):
        self.mainFrame_ui.questionlistlistWidget.clear()
        self.mainFrame_ui.response_fail_filelistlistWidget.clear()
        self.mainFrame_ui.response_fail_filenumlineEdit.clear()

    def contextGeneration_file_selection(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Question File Selection", "", "JSON File (*.json)")

        if not file_path:
            return

        self.CONFIG_PARAMS["context_file_path"] = file_path
        self.contextGeneration_erase_question_list()

        load_question_instance = LoadQuestion(filepath=file_path)
        load_question_instance.LoadQuestion_finished_list_signal.connect(self.contextGeneration_gui_set)
        load_question_instance.start()

        self.threadList.append(load_question_instance)

        self.mainFrame_ui.referencefilelineEdit.setText(os.path.normpath(file_path))

    def generateContext_job(self):
        if not self.mainFrame_ui.referencefilelineEdit.text().strip():
            print("Select File for ContextGeneration.")
            return

        if self.mainFrame_ui.trexradioButton.isChecked():
            self.progress_dialog = ProgressDialog(message="Context Generation", show_close_button=True, modal=self.mainFrame_ui.popctrl_radioButton.isChecked())
            self.progress_dialog.progress_stop_signal.connect(self.finished_WorkThread)

            if self.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
                gpt_model = "gpt-4o-mini"
            else:
                gpt_model = "gpt-4o"

            ctrl_parm = {"context_file_path": self.CONFIG_PARAMS["context_file_path"], "gpt_model": gpt_model}

            thread = ContextGeneration_with_Trex_Ai_Chatbot_tools(ctrl_parm=ctrl_parm)
            thread.ContextGeneration_total_files_cnt_signal.connect(self.progress_dialog.set_progress_max)
            thread.ContextGeneration_progress_signal.connect(self.progress_dialog.update_progress)
            thread.ContextGeneration_finished_thread_signal.connect(self.finished_WorkThread)
            thread.ContextGeneration_text_update_signal.connect(self.progress_dialog.update_text)

            # thread.TestSetCreation_creation_fail_file_signal.connect(self.update_TestSetCreation_Fail_list)
            thread.ContextGeneration_creation_update_list_widget_signal.connect(
                self.color_ContextGeneration_list_widget_item)

            thread.start()

            self.threadList.append(thread)

            self.progress_dialog.show_progress()
        else:
            print("Chatbot Response is under Construction")

    def ragas_evaluation_gui_set(self, question_list):
        log_info("info", "Question Loading Done.")
        # self.file_list = question_list
        self.mainFrame_ui.questionlistlistWidget_2.addItems(question_list)
        self.mainFrame_ui.questionfilenumlineEdit_2.setText(str(len(question_list)))

    def ragas_evaluation_erase_question_list(self):
        self.mainFrame_ui.questionlistlistWidget_2.clear()
        self.mainFrame_ui.evaluation_resultlistWidget.clear()

    def ragas_evaluation_file_selection(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ragas Evaluation File Selection", "", "JSON File (*.json)")

        if not file_path:
            return

        self.CONFIG_PARAMS["evaluation_file_path"] = file_path

        self.ragas_evaluation_erase_question_list()

        load_eval_instance = LoadQuestion(filepath=file_path)
        load_eval_instance.LoadQuestion_finished_list_signal.connect(self.ragas_evaluation_gui_set)
        load_eval_instance.start()

        self.threadList.append(load_eval_instance)

        self.mainFrame_ui.evalfilelineEdit.setText(os.path.normpath(file_path))

    def color_EvaluationDataset_list_widget_item(self, index):
        if self.eval_prev_index is not None:
            # 이전에 선택된 아이템 스타일 초기화
            prev_item = self.mainFrame_ui.questionlistlistWidget_2.item(self.eval_prev_index)
            if prev_item:
                prev_item.setBackground(QBrush(QColor("white")))  # 원래 색상으로 복원

            # 현재 인덱스 아이템 강조
        item = self.mainFrame_ui.questionlistlistWidget_2.item(index)
        if item:
            item.setBackground(QBrush(QColor("yellow")))  # 노란색 하이라이트 적용
            self.eval_prev_index = index  # 현재 선택된 인덱스를 저장

    def ragas_evaluation_job(self):
        # print("ragas_evaluation_job")
        if not self.mainFrame_ui.evalfilelineEdit.text().strip():
            print("Select File for Evaluation.")
            return

        self.progress_dialog = ProgressDialog(message="Evaluation Dataset", show_close_button=True, modal=self.mainFrame_ui.popctrl_radioButton.isChecked())
        self.progress_dialog.progress_stop_signal.connect(self.finished_WorkThread)

        eval_metric = {
            "Faithfulness": self.mainFrame_ui.faithfullnesscheckBox.isChecked(),
            "LLMContextRecall": self.mainFrame_ui.llmcontextrecallcheckBox.isChecked(),
            "FactualCorrectness": self.mainFrame_ui.factualcorrectnesscheckBox.isChecked(),
            "SemanticSimilarity": self.mainFrame_ui.similaritycheckBox.isChecked()
        }

        if self.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
            gpt_model = "gpt-4o-mini"
        else:
            gpt_model = "gpt-4o"

        ctrl_parm = {
            "evaluation_file_path": self.CONFIG_PARAMS["evaluation_file_path"],
            "gpt_model": gpt_model,
            "eval_iter": self.mainFrame_ui.iter_spinBox.value(),
            "eval_metric": eval_metric
        }

        thread = DataSetEvaluation(ctrl_parm=ctrl_parm)
        thread.EvaluationDataset_total_sets_cnt_signal.connect(self.progress_dialog.set_progress_max)
        thread.EvaluationDataset_progress_signal.connect(self.progress_dialog.update_progress)
        thread.EvaluationDataset_finished_thread_signal.connect(self.finished_WorkThread)
        thread.EvaluationDataset_text_update_signal.connect(self.progress_dialog.update_text)
        #
        #     # thread.TestSetCreation_creation_fail_file_signal.connect(self.update_TestSetCreation_Fail_list)
        thread.EvaluationDataset_update_list_widget_signal.connect(
            self.color_EvaluationDataset_list_widget_item)

        thread.start()
        self.threadList.append(thread)
        self.progress_dialog.show_progress()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)  # QApplication 생성 (필수)

    app.setStyle("Fusion")
    ui = ProjectMainWindow()
    ui.showMaximized()
    ui.connectSlotSignal()

    sys.exit(app.exec_())
