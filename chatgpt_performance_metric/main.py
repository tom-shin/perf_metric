import subprocess
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import logging
import easygui
import site
import shutil
import ctypes
import chardet
import json
from collections import OrderedDict
from datetime import datetime
import pytz

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PyQt5.QtCore import pyqtSignal, QObject, QProcess
from PyQt5 import QtWidgets, QtCore, QtGui

import os
import fnmatch
import chardet
import json
from datetime import datetime
import pytz

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from ragas.testset import TestsetGenerator

from PyQt5.QtCore import QThread

import pandas as pd

# 모든 행과 열을 출력할 수 있도록 설정 변경
pd.set_option('display.max_rows', None)  # 모든 행을 출력
pd.set_option('display.max_columns', None)  # 모든 열을 출력
pd.set_option('display.width', None)  # 출력 폭을 제한하지 않음
pd.set_option('display.max_colwidth', None)  # 각 열의 최대 너비를 제한하지 않음

# user defined module
from source.test_set_evaluation.configuration.model_config import *
from source.test_set_creation.execute_trex_ai_chatbot_tools import generator_context_answer_class
from source.test_set_evaluation.execute_ragas_metrics import performance_metric_evaluator_class
from source.test_set_creation.execute_chatbot import ChatBotGenerationThread

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

        self.testset_creation_instance = None
        self.chatbot_instance = None
        self.edge_driver = None
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

        self.chatbot_xpath = {
            "text_input": "/html/body/div/div/form/div/div/div/textarea[1]",
            "gpt_answer": "/html/body/div/div/div[2]/div/div/div[ThunderSoft]/div[2]/div/div[1]/div/div",
            "check_chatbot_ready_status": "/html/body/div/div/div[2]/div/div/div[1]/div[2]/div/p"
        }

    def handle_stdout(self):
        output = self.process_ground_truth_ground_truth.readAllStandardOutput().data().decode()
        print(output)

    def handle_stderr(self):
        error = self.process_ground_truth_ground_truth.readAllStandardError().data().decode()
        if len(error) != 0:
            print(f"{error}")

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

        self.mainFrame_ui.chatbotpushButton.setEnabled(False)

    def closeEvent(self, event):
        answer = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit?",
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

        # self.mainFrame_ui.questionlistWidget.itemDoubleClicked.connect(self.question_item_double_clicked)
        self.mainFrame_ui.chatbotpushButton.clicked.connect(self.chatbot_generation)
        self.mainFrame_ui.delqlistpushButton.clicked.connect(self.delete_all_question_items)

        self.mainFrame_ui.qinput_lineEdit.returnPressed.connect(self.add_to_question_list)
        self.mainFrame_ui.msgwritepushButton.clicked.connect(self.message_write_on_item)

        self.mainFrame_ui.responsestop_pushButton.clicked.connect(self.stop_response)
        self.mainFrame_ui.suspendpushButton.clicked.connect(self.suspend_resume_response)

        self.mainFrame_ui.label_SpecificQuerySynthesizer.hide()
        self.mainFrame_ui.label_ComparativeAbstractQuerySynthesizer.hide()
        self.mainFrame_ui.label_11.hide()

        self.mainFrame_ui.lineEdit_SpecificQuerySynthesizer.hide()
        self.mainFrame_ui.lineEdit_ComparativeAbstractQuerySynthesizer.hide()
        self.mainFrame_ui.lineEdit_AbstractQuerySynthesizer.hide()

    def suspend_resume_response(self):
        if self.chatbot_instance is not None:
            if not self.chatbot_instance.suspended:
                self.chatbot_instance.suspend()
                self.mainFrame_ui.suspendpushButton.setText("Resume")
            else:
                self.chatbot_instance.resume()
                self.mainFrame_ui.suspendpushButton.setText("Suspend")

    def stop_response(self):
        if self.chatbot_instance is not None:
            self.reset_chatbot()

    def setUserName(self, user=''):
        self.mainFrame_ui.userlineEdit.setText(user)

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
        self.mainFrame_ui.filelistlistWidget.clear()

        def find_files(root_dir, extensions):
            found_files = []
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        found_files.append(os.path.join(dirpath, filename))
            return found_files

        file_extensions = [".md", ".txt"]

        files = find_files(self.directory.replace("\\", "/"), file_extensions)
        self.mainFrame_ui.filelistlistWidget.addItems(files)
        self.mainFrame_ui.filenumlineEdit.setText(str(len(files)))

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

        test_size_ = int(self.mainFrame_ui.n_lineEdit.text())
        if self.mainFrame_ui.creation_gpt4o_radioButton.isChecked():
            model = "gpt-4o"
        elif self.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
            model = "gpt-4o-mini"
        else:
            model = "gpt-3.5-turbo-16k"

        source_dir = str(self.directory)

        user_name = self.mainFrame_ui.userlineEdit.text().strip()

        SpecificQuerySynthesizer_cnt = float(self.mainFrame_ui.lineEdit_SpecificQuerySynthesizer.text())
        ComparativeAbstractQuerySynthe_cnt = float(
            self.mainFrame_ui.lineEdit_ComparativeAbstractQuerySynthesizer.text())
        AbstractQuerySynthesizer_cnt = float(self.mainFrame_ui.lineEdit_AbstractQuerySynthesizer.text())

        # 실행할 파이썬 파일 경로와 전달할 인자들
        script_path = os.path.join(BASE_DIR, "source", "test_set_creation",
                                   "execute_question_extraction.py")

        # 다른 변수들도 문자열로 변환

        test_size_str = str(test_size_)
        SpecificQuerySynthesizer_str = str(SpecificQuerySynthesizer_cnt)
        ComparativeAbstractQuerySynthesizer_str = str(ComparativeAbstractQuerySynthe_cnt)
        AbstractQuerySynthesizer_str = str(AbstractQuerySynthesizer_cnt)
        model_str = str(model)
        chatbot_server = self.mainFrame_ui.gptserverlineEdit.text().strip()

        # 인자로 넘길 리스트 (모두 문자열이어야 함)
        arguments = [script_path, source_dir, test_size_str, SpecificQuerySynthesizer_str,
                     ComparativeAbstractQuerySynthesizer_str, AbstractQuerySynthesizer_str, model_str,
                     self.get_OpenAIKey(), chatbot_server, user_name]

        # QProcess로 파이썬 스크립트를 인자와 함께 실행
        self.process_ground_truth_ground_truth.start(sys.executable, arguments)

    def start_browser(self, initial_open=True):
        try:
            subprocess.run("taskkill /F /IM msedgedriver.exe /T", shell=True, check=True)
        except subprocess.CalledProcessError:
            print("")

        ms_drive = os.path.join(BASE_DIR, "ts_library", "edgedriver_win64", "msedgedriver.exe")

        """Edge 브라우저 실행"""
        edge_options = Options()
        edge_options.use_chromium = True  # Chromium 기반 Edge 사용 설정

        # "http://d1x4texestgncv.cloudfront.net/global/chatbot"

        # # HTTPS 업그레이드 방지

        # edge_options.add_argument(
        #     "--disable-features=BlockInsecurePrivateNetworkRequests,InsecurePrivateNetworkRequestsAllowed")
        # edge_options.add_argument("--disable-features=UpgradeHttpToHttps")  # 강제 변환 방지
        # """
        # reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v InsecurePrivateNetworkRequestsAllowed /t REG_DWORD /d 1 /f
        # reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Edge" /v UpgradeHttpToHttpsEnabled /t REG_DWORD /d 0 /f
        #
        # """

        # Edge WebDriver 경로 지정
        driver_path = ms_drive.replace("\\", "/")
        service = Service(driver_path)

        # Edge 브라우저 실행
        driver = webdriver.Edge(service=service, options=edge_options)

        chatbot_server = self.mainFrame_ui.gptserverlineEdit.text().strip()
        driver.get(chatbot_server)

        self.edge_driver = driver

        if not initial_open:
            input_field = WebDriverWait(self.edge_driver, 300).until(
                EC.presence_of_element_located((By.XPATH, self.chatbot_xpath["check_chatbot_ready_status"]))
            )
        time.sleep(2)

    def delete_all_question_items(self):
        self.mainFrame_ui.questionlistWidget.clear()
        self.mainFrame_ui.questionnumlineEdit.setText("0")

    def add_to_question_list(self):
        text = self.mainFrame_ui.qinput_lineEdit.text().strip()  # 입력된 텍스트 가져오기
        if text:  # 빈 값이 아니면 추가
            self.mainFrame_ui.questionlistWidget.addItem(text)  # 리스트 마지막에 추가
            self.mainFrame_ui.questionlistWidget.setCurrentRow(
                self.mainFrame_ui.questionlistWidget.count() - 1)  # 마지막 아이템 선택
            self.mainFrame_ui.qinput_lineEdit.clear()  # 입력 필드 초기화

            file_ = self.mainFrame_ui.testset_lineEdit.text().strip()
            file_path = file_.replace("\\", "/")
            # 1. JSON 파일 읽기
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)  # JSON 데이터 로드

            # 한국 시간대 설정
            korea_tz = pytz.timezone('Asia/Seoul')
            # 현재 시간 가져오기
            now = datetime.now(korea_tz)

            chatbot_server = self.mainFrame_ui.gptserverlineEdit.text().strip()

            new_item = {
                "user_input": text,
                "reference_contexts": [""],
                "reference": "",
                "synthesizer_name": "",
                "file": "manual",
                "retrieved_contexts": "",
                "response": "",
                "chatbot_response": "",
                "date_time": str(now),
                "chatbot_server": chatbot_server,
                "user_comment": ""
            }
            data.append(new_item)

            # 3. JSON 파일 다시 저장
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)  # 보기 좋게 저장

    def message_write_on_item(self):
        current_row = self.mainFrame_ui.questionlistWidget.currentRow()  # 현재 선택된 인덱스
        item_text = self.mainFrame_ui.questionlistWidget.item(current_row).text()  # 해당 인덱스의 텍스트

        def message():
            dialog = SimpleMsg(message=True)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                input_text = dialog.get_input_text()

                if input_text:  # 입력값이 있으면 관리자 모드 실행
                    # print("message", input_text)
                    return input_text
                else:  # 입력 없으면 경고 후 종료
                    return ""
            else:
                # 이 경우는 사실상 실행되지 않겠지만, 대비용
                return ""

        comment = message()
        if len(comment) == 0:
            return

        file_ = self.mainFrame_ui.testset_lineEdit.text().strip()
        file_path = file_.replace("\\", "/")

        # 1. JSON 파일 읽기
        with open(file_path, "r", encoding="utf-8") as file:
            datas = json.load(file)  # JSON 데이터 로드

        for data in datas:
            if data["user_input"] == item_text:
                data["user_comment"] = comment
                break

        # 3. JSON 파일 다시 저장
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(datas, file, ensure_ascii=False, indent=4)  # 보기 좋게 저장

    def question_item_double_clicked(self, item):
        """ 더블 클릭한 항목의 텍스트 출력 """
        text_to_copy = item.text()
        timeout = 30

        try:
            # 입력 필드가 나타날 때까지 기다림 (최대 10초)
            input_field = WebDriverWait(self.edge_driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, self.chatbot_xpath["text_input"]))
            )
            input_field.clear()
            input_field.send_keys(text_to_copy)
            time.sleep(0.5)
            input_field.send_keys(Keys.RETURN)  # 'Enter' 키 입력

        except TimeoutException:
            print("Error: 입력 필드를 찾을 수 없습니다. 페이지 로딩을 확인하세요.")
        except NoSuchElementException as e:
            print(f"Error: Element not found - {e}")

    def chatbot_generation(self):

        item_count = self.mainFrame_ui.questionlistWidget.count()
        # print(item_count)
        if item_count == 0:
            print("There are No Questions")
            return
        self.reset_chatbot()
        self.start_browser(initial_open=False)

        self.chatbot_instance = ChatBotGenerationThread(base_dir=BASE_DIR, q_lists=self.mainFrame_ui.questionlistWidget,
                                                        drive=self.edge_driver,
                                                        gpt_xpath=self.chatbot_xpath,
                                                        source_result_file=self.mainFrame_ui.testset_lineEdit.text()
                                                        )
        self.chatbot_instance.start()

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
        self.mainFrame_ui.questionlistWidget.clear()

        # self.start_browser()

        def json_load_f(file_path, use_encoding=False):
            if file_path is None:
                return False, False

            if use_encoding:
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
                    encoding = result['encoding']
            else:
                encoding = "utf-8"

            with open(file_path, "r", encoding=encoding) as f:
                json_data = json.load(f, object_pairs_hook=OrderedDict)

            return True, json_data

        ret, scenarios = json_load_f(file_path=file_path.replace("\\", "/"))
        cnt = 0

        for data in scenarios:
            # user_input 키에 해당하는 질문만 리스트에 추가
            if isinstance(data, dict) and "user_input" in data:
                user_input = data["user_input"]
                if isinstance(user_input, str):
                    self.mainFrame_ui.questionlistWidget.addItem(user_input)
                    cnt += 1
                elif isinstance(user_input, list):
                    for question in user_input:
                        self.mainFrame_ui.questionlistWidget.addItem(question)
                        cnt += 1

        self.mainFrame_ui.questionnumlineEdit.setText(str(cnt))
        self.mainFrame_ui.chatbotpushButton.setEnabled(True)

        self.reset_chatbot()

    def reset_chatbot(self):
        self.mainFrame_ui.suspendpushButton.setText("Suspend")
        if self.chatbot_instance is not None:
            self.chatbot_instance.stop()
            self.chatbot_instance = None

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
    return True

    # try:
    #     # return True
    #     return ctypes.windll.shell32.IsUserAnAdmin()
    # except Exception as e:
    #     return False


class SimpleMsg(QtWidgets.QDialog):
    def __init__(self, message=False):
        super().__init__()

        if message:
            self.setWindowTitle("Check User")
        else:
            self.setWindowTitle("Write Message")

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)  # 항상 위에 표시

        self.setMinimumSize(400, 40)  # Set a larger window size

        layout = QtWidgets.QVBoxLayout()

        # 메시지 라벨
        if message:
            self.label = QtWidgets.QLabel("Write Message.\n")
        else:
            self.label = QtWidgets.QLabel("User Name is Required.\n")

        layout.addWidget(self.label)

        # 입력 필드
        self.input_field = QtWidgets.QLineEdit()
        if message:
            self.input_field.setPlaceholderText("Message")
        else:
            self.input_field.setPlaceholderText("Enter your name")

        self.input_field.setMinimumHeight(40)  # Make the input taller
        font = self.input_field.font()
        font.setPointSize(12)  # Optional: larger font
        self.input_field.setFont(font)

        layout.addWidget(self.input_field)

        # # Enter 키가 기본적으로 accept() 호출하지 않도록 설정
        # self.input_field.returnPressed.connect(lambda: None)
        #
        # # 버튼 추가
        # self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        # self.button_box.accepted.connect(self.accept)  # OK 버튼 클릭 시만 accept
        # layout.addWidget(self.button_box)

        self.setLayout(layout)

        # Enter 키 입력 시 다이얼로그 종료 (accept)
        self.input_field.returnPressed.connect(self.accept)

    def get_input_text(self):
        return self.input_field.text().strip()


def checkUserName():
    dialog = SimpleMsg()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        input_text = dialog.get_input_text()

        if input_text:  # 입력값이 있으면 관리자 모드 실행
            print("Your name is", input_text)
            return input_text
        else:  # 입력 없으면 경고 후 종료
            QtWidgets.QMessageBox.warning(None, "Error", "You must enter user name.")
            sys.exit(0)
    else:
        # 이 경우는 사실상 실행되지 않겠지만, 대비용
        sys.exit(0)


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

    user = checkUserName()

    app.setStyle("Fusion")
    ui = Performance_metrics_MainWindow()

    ui.setUserName(user)
    ui.showMaximized()
    ui.connectSlotSignal()

    os.environ["OPENAI_API_KEY"] = ui.get_OpenAIKey()

    sys.exit(app.exec_())
