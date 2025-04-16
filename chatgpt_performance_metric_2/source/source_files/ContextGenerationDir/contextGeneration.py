import os.path
import subprocess
import time

import pytz
from datetime import datetime
import shutil
from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_community.document_loaders import TextLoader

from PyQt5.QtCore import QThread, pyqtSignal
from source.head import handle_exception, FileManager, log_info


class ContextGeneration_with_Trex_Ai_Chatbot_tools(QThread, FileManager):
    ContextGeneration_progress_signal = pyqtSignal(int)
    ContextGeneration_text_update_signal = pyqtSignal(str)
    ContextGeneration_finished_thread_signal = pyqtSignal()
    ContextGeneration_total_files_cnt_signal = pyqtSignal(int)
    # ContextGeneration_creation_fail_file_signal = pyqtSignal(str, int)
    ContextGeneration_creation_update_list_widget_signal = pyqtSignal(int)

    korea_tz = pytz.timezone('Asia/Seoul')

    def __init__(self, ctrl_parm=None, file_path=""):
        super().__init__()
        self.thread_run = False
        self.ctrl_parm = ctrl_parm

        self.setup_env()

    @staticmethod
    def setup_env():
        # DB 연결
        try:
            """ .env setting """
            env_src_path = os.path.normpath(os.path.join("source", "source_files", "ContextGenerationDir", ".env"))
            src_trex_lib_dir = os.path.normpath(os.path.join("source", "trex_Library", "trex_ai_chatbot_tools"))
            dst_trex_lib_dir = os.path.normpath(os.path.join("venv", "Lib", "site-packages", "trex_ai_chatbot_tools"))

            # 1. .env 파일을 src_trex_lib_dir로 복사 (기존 파일 있으면 덮어쓰기)
            env_dst_path = os.path.normpath(os.path.join(src_trex_lib_dir, ".env"))
            if os.path.exists(env_dst_path):
                os.remove(env_dst_path)
            shutil.copy2(env_src_path, env_dst_path)

            # 2. dst_trex_lib_dir이 존재하면 삭제
            if os.path.exists(dst_trex_lib_dir):
                shutil.rmtree(dst_trex_lib_dir)

            # 3. 디렉토리 복사
            shutil.copytree(src_trex_lib_dir, dst_trex_lib_dir)

            print(".env copied and trex_ai_chatbot_tools updated.")

            """ DB 서버에 연결 """
            # start cmd /k --> 실행 후 종료 하지 않고 유지
            # start cmd /c --> 실행 후 종료
            connectDB_path = os.path.normpath(
                os.path.join("source", "source_files", "ContextGenerationDir", "connectDB.bat"))

            subprocess.Popen(f'start cmd /k {os.path.basename(connectDB_path)}',
                             cwd=os.path.dirname(connectDB_path), shell=True)

            print("Connected DB successfully")
        except Exception as e:
            handle_exception(e)

    def run(self):
        from trex_ai_chatbot_tools import text_gen as tg
        self.thread_run = True

        # question 리스트 파일 가져 오기
        _, datas = self.load_json(file_path=self.ctrl_parm["context_file_path"])
        total_cnt = len(datas)
        self.ContextGeneration_total_files_cnt_signal.emit(total_cnt)

        try:
            for cnt, data in enumerate(datas):

                if not self.thread_run:
                    break

                self.ContextGeneration_text_update_signal.emit(
                    f"{cnt + 1}/{total_cnt}: Starting..."
                )
                self.ContextGeneration_creation_update_list_widget_signal.emit(cnt)

                response = tg.answer_question(data["user_input"])
                post_response = tg.post_generation(response)

                if post_response['success']:
                    response = post_response['response']
                    retrieved_contexts = post_response['context']
                else:
                    response = post_response['response']
                    retrieved_contexts = post_response['response']

                data["retrieved_contexts"] = retrieved_contexts
                data["response"] = response

                self.ContextGeneration_progress_signal.emit(cnt + 1)
                self.ContextGeneration_text_update_signal.emit(
                    f"{cnt + 1}/{total_cnt}: Done..."
                )

            if self.thread_run:
                self.save_json(file_path=self.ctrl_parm["context_file_path"], data=datas)

            self.ContextGeneration_finished_thread_signal.emit()

            subprocess.run('taskkill /FI "WINDOWTITLE eq connectDB" /F', shell=True)

        except Exception as e:
            subprocess.run('taskkill /FI "WINDOWTITLE eq connectDB" /F', shell=True)
            handle_exception(e)

    def stop(self):
        # log_info("info", "Thread 종료")
        self.thread_run = False
        self.quit()
        if not self.wait(3000):  # 3초 기다려도 종료되지 않으면 강제 종료
            self.terminate()
