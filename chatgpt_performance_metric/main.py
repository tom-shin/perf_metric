import subprocess
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import logging
import easygui
import site
import shutil
import ctypes

from PyQt5.QtCore import pyqtSignal, QObject, QProcess
from PyQt5 import QtWidgets, QtCore, QtGui

import pandas as pd

# 모든 행과 열을 출력할 수 있도록 설정 변경
pd.set_option('display.max_rows', None)  # 모든 행을 출력
pd.set_option('display.max_columns', None)  # 모든 열을 출력
pd.set_option('display.width', None)  # 출력 폭을 제한하지 않음
pd.set_option('display.max_colwidth', None)  # 각 열의 최대 너비를 제한하지 않음

# user defined module
from source.test_set_evaluation.configuration.model_config import *
from source.test_set_creation.test_set_context_answer_creator import generator_context_answer_class
from source.test_set_evaluation.set_metric_evaluator import performance_metric_evaluator_class

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "version.txt")
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


class Performance_metrics_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.context_ground = None
        self.directory = None
        self.openaikey = None
        self.embed_open_scenario_file = None

        """ for main frame & widget """
        self.mainFrame_ui = None
        self.widget_ui = None

        self.setupUi()

        # QProcess 객체 생성 
        self.process_ground_truth_ground_truth = QProcess(self)
        self.process_ground_truth_ground_truth.readyReadStandardOutput.connect(self.handle_stdout)
        self.process_ground_truth_ground_truth.readyReadStandardError.connect(self.handle_stderr)

        self.evaluation_ctrl = None

    def handle_stdout(self):
        output = self.process_ground_truth_ground_truth.readAllStandardOutput().data().decode()
        print(output)

    def handle_stderr(self):
        error = self.process_ground_truth_ground_truth.readAllStandardError().data().decode()
        if len(error) != 0:
            print(f"Error: {error}")

    def setupUi(self):
        # Load the main window's UI module
        rt = load_module_func(module_name="source.ui_designer.main_frame")
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

    def closeEvent(self, event):
        answer = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit?\nAll data will be lost.",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if answer == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.terminate_env_setup()
        else:
            event.ignore()

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

        # evaluation tab
        self.mainFrame_ui.open_pushButton.clicked.connect(self.open_file_for_evaluation)
        self.mainFrame_ui.refresh_pushButton.clicked.connect(self.refresh_scenario)
        self.mainFrame_ui.analyze_pushButton.clicked.connect(self.start_evaluation)
        self.mainFrame_ui.reset_score_pushButton.clicked.connect(self.reset_score)
        self.mainFrame_ui.save_pushButton.clicked.connect(self.save_eval_score)
        self.mainFrame_ui.all_check_scenario.clicked.connect(self.check_all_scenario)
        self.mainFrame_ui.all_uncheck_scenario.clicked.connect(self.check_all_scenario)
        self.mainFrame_ui.all_check_model.clicked.connect(self.check_all_model)
        self.mainFrame_ui.all_uncheck_model.clicked.connect(self.check_all_model)

        # test set creation
        self.mainFrame_ui.dirpushButton.clicked.connect(self.open_dir_for_generating_question_groundTruth_test_set)
        self.mainFrame_ui.gengenpushButton.clicked.connect(self.question_ground_truth_generation)

        self.mainFrame_ui.testset_pushButton.clicked.connect(self.open_file_for_generating_contexts_answer_test_set)
        self.mainFrame_ui.vector_env_pushButton.clicked.connect(self.environment_setup)
        self.mainFrame_ui.vector_start_pushButton.clicked.connect(self.context_answer_generation)

    def context_answer_generation(self):
        if self.embed_open_scenario_file is None or len(self.mainFrame_ui.testset_lineEdit.text()) == 0:
            print("Select File for Generating Context/ Answer : Open Button ")
            return

        try:
            from trex_ai_chatbot_tools import text_gen as tg
        except Exception as e:
            print(f"pls, install trex_ai_chatbot_tools library: {e}")
            return

        self.context_ground = generator_context_answer_class(self, tg)
        self.context_ground.db_connection()
        self.context_ground.start_set_generation()

    def env_file_generation_and_copy2_rag_library(self):
        # env template 수정해서 tsk_ragtools에 생성
        openai_api_key = self.get_OpenAIKey()
        env_path = os.path.join(BASE_DIR, "source", "test_set_creation", "set_env_for_ragas", ".env_template")
        env_path_target = os.path.join(BASE_DIR, "ts_library", "trex_ai_chatbot_tools", ".env")
        connection_string = self.mainFrame_ui.connection_lineEdit.text()

        with open(env_path, 'r') as template_file:
            content = template_file.readlines()

        new_content = []
        for line in content:
            if line.startswith("OPENAI_API_KEY"):
                new_content.append(f'OPENAI_API_KEY={openai_api_key}\n')
            elif line.startswith("CONNECTION_STRING"):
                new_content.append(f'CONNECTION_STRING={connection_string}\n')
            else:
                new_content.append(line)

        with open(env_path_target, 'w') as new_file:
            new_file.writelines(new_content)

    @staticmethod
    def copy_trex_ai_chatbot_tools_to_python_sitepackage():

        def get_site_packages_path():  # 현재 실행 중인 파이썬 인터프리터의 site-packages 경로를 반환하는 함수
            return [path for path in site.getsitepackages() if 'site-packages' in path]

        site_packages_paths = get_site_packages_path()[0]

        source_dir = os.path.join(BASE_DIR, "ts_library", "trex_ai_chatbot_tools")
        destination_dir = os.path.join(site_packages_paths, os.path.basename(source_dir))

        try:
            if os.path.exists(destination_dir):
                shutil.rmtree(destination_dir)  # 대상 폴더가 존재하면 삭제
                print(f'{destination_dir} 폴더가 삭제되었습니다.')
            shutil.copytree(source_dir, destination_dir)  # 새롭게 폴더 복사
            print(f'{source_dir}이(가) {destination_dir}로 복사되었습니다.')
        except Exception as e:
            print(f'복사 중 오류 발생: {e}')

    def environment_setup(self):
        self.env_file_generation_and_copy2_rag_library()
        self.copy_trex_ai_chatbot_tools_to_python_sitepackage()

    @staticmethod
    def terminate_env_setup():
        try:
            # 실행 중인 cmd 창 종료
            subprocess.run('taskkill /f /im cmd.exe /t', check=True)
            # print(f"Closed cmd window with PID: {self.process_ground_truth_ground_truth.pid}")

        except subprocess.CalledProcessError as e:
            print(f"Error while closing cmd: {e}")

    def open_dir_for_generating_question_groundTruth_test_set(self):
        self.directory = easygui.diropenbox()

        # Print the selected directory
        if self.directory is None:
            return

        self.mainFrame_ui.dirlineEdit.setText(self.directory)

    def question_ground_truth_generation(self):
        if self.directory is None:
            answer = QtWidgets.QMessageBox.warning(self,
                                                   "Directory Check...",
                                                   "Open Source Directory for Question Ground_Truth Test Set",
                                                   QtWidgets.QMessageBox.Yes)
            print("Empty Directory")
            return

        self.start_question_ground_truth_gen()

    def start_question_ground_truth_gen(self):
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
        script_path = os.path.join(BASE_DIR, "source", "test_set_creation", "evaluation_set_question_ground_truth_creator.py")

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
        self.process_ground_truth_ground_truth.start(sys.executable, arguments)

    def open_file_for_generating_contexts_answer_test_set(self):
        file_path = easygui.fileopenbox(
            msg="Select Test Set Scenario",
            title="Test Set Selection",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            return

        self.embed_open_scenario_file = file_path
        self.mainFrame_ui.testset_lineEdit.setText(self.embed_open_scenario_file)

    def open_file_for_evaluation(self):
        file_path = easygui.fileopenbox(
            msg="Select Test Set Scenario",
            title="Test Set Selection",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            return

        self.evaluation_ctrl = performance_metric_evaluator_class(parent=self)
        self.evaluation_ctrl.open_file(file_path)

    def refresh_scenario(self):
        if self.evaluation_ctrl is not None:
            self.evaluation_ctrl.refresh_contents_of_evaluation_file()

    def start_evaluation(self):
        if self.evaluation_ctrl is not None:
            self.evaluation_ctrl.test_set_analyzation()

    def reset_score(self):
        if self.evaluation_ctrl is not None:
            self.evaluation_ctrl.evaluation_reset_score()

    def save_eval_score(self):
        if self.evaluation_ctrl is not None:
            self.evaluation_ctrl.save_evaluation_score()

    def check_all_scenario(self):
        if self.evaluation_ctrl is not None:
            sender = self.sender()
            check = False

            if sender:
                if sender.objectName() == "all_check_scenario":
                    check = True
                elif sender.objectName() == "all_uncheck_scenario":
                    check = False

            self.evaluation_ctrl.evaluation_select_all_scenario(check=check)

    def check_all_model(self):
        if self.evaluation_ctrl is not None:
            sender = self.sender()
            check = False

            if sender:
                if sender.objectName() == "all_check_model":
                    check = True
                elif sender.objectName() == "all_uncheck_model":
                    check = False

            self.evaluation_ctrl.model_check(check=check)


def is_admin():
    try:
        return True
        # return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)  # QApplication 생성 (필수)

    if not is_admin():
        msg_box = QtWidgets.QMessageBox()  # QMessageBox 객체 생성
        msg_box.setWindowTitle("Check Administrator privileges")  # 대화 상자 제목
        msg_box.setText(
            "Administrator privileges are required.\nDo you want to continue running with administrator privileges?")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)  # Yes/No 버튼 추가
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 항상 위에 표시

        answer = msg_box.exec_()  # 대화 상자를 실행하고 사용자의 응답을 반환

        if answer == QtWidgets.QMessageBox.Yes:
            # 관리자 권한으로 프로그램 재실행
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)  # 일반 모드 실행 종료
        else:
            print("Normal Termination.")
            sys.exit(0)  # 일반 모드 실행 종료

    app.setStyle("Fusion")
    ui = Performance_metrics_MainWindow()
    ui.showMaximized()
    ui.connectSlotSignal()

    os.environ["OPENAI_API_KEY"] = ui.get_OpenAIKey()

    sys.exit(app.exec_())
