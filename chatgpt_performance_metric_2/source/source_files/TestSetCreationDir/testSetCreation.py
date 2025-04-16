import os.path
import pytz
from datetime import datetime

from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_community.document_loaders import TextLoader

from PyQt5.QtCore import QThread, pyqtSignal
from source.head import handle_exception, FileManager, log_info


class TestSetCreation(QThread, FileManager):
    TestSetCreation_progress_signal = pyqtSignal(int)
    TestSetCreation_text_update_signal = pyqtSignal(str)
    TestSetCreation_finished_thread_signal = pyqtSignal()
    TestSetCreation_total_files_cnt_signal = pyqtSignal(int)
    TestSetCreation_creation_fail_file_signal = pyqtSignal(str, int)
    TestSetCreation_creation_update_list_widget_signal = pyqtSignal(int)

    korea_tz = pytz.timezone('Asia/Seoul')

    def __init__(self, ctrl_parm=None):
        super().__init__()
        self.thread_run = False

        self.ctrl_parm = ctrl_parm
        self.output_path = "testset_creation_results.json"
        self.failed_path = "testset_creation_failed_files.json"
        self.file_list = self.ctrl_parm["file_list"]

        self.generator_llm = LangchainLLMWrapper(ChatOpenAI(model=self.ctrl_parm["gpt_model"]))
        self.generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

        self.testset_creation_fail_cnt = None

    def execute(self, file_path):
        loader = TextLoader(file_path, autodetect_encoding=True)
        docs = loader.load()

        try:
            generator = TestsetGenerator(llm=self.generator_llm, embedding_model=self.generator_embeddings)
            dataset = generator.generate_with_langchain_docs(docs, testset_size=self.ctrl_parm["test_size"])

            df = dataset.to_pandas()

            if not df.empty:
                """ 추가 필드 """
                df["file"] = file_path
                df["retrieved_contexts"] = ""
                df["response"] = ""
                df["chatbot_response"] = ""
                df["user_comment"] = ""
                df["date_time"] = str(datetime.now(self.korea_tz))
                df["chatbot_server"] = ""
                df["user"] = self.ctrl_parm["user"]

                json_data = df.to_dict(orient='records')  # 리스트 of dict
                return {"success": True, "file": file_path, "data": json_data}
            else:
                # log_info("info", f"[Error]: {file_path}")
                self.testset_creation_fail_cnt += 1
                self.TestSetCreation_creation_fail_file_signal.emit(file_path, self.testset_creation_fail_cnt)
                return {"success": False, "file": file_path, "error": "Empty dataset"}

        except Exception as e:
            # log_info("info", f"[Error]: {file_path}")
            self.testset_creation_fail_cnt += 1
            self.TestSetCreation_creation_fail_file_signal.emit(file_path, self.testset_creation_fail_cnt)
            return {"success": False, "file": file_path, "error": str(e)}

    def run(self):
        all_data = []  # ✅ 성공한 데이터 저장 (list)
        failed_files = []  # ✅ 실패한 파일 저장 (list)
        self.testset_creation_fail_cnt = 0

        try:
            self.TestSetCreation_total_files_cnt_signal.emit(len(self.file_list))
            self.thread_run = True

            for cnt, file_name in enumerate(self.file_list):
                if not self.thread_run:
                    break

                self.TestSetCreation_text_update_signal.emit(
                    f"{os.path.basename(file_name)} [{self.get_file_size(file_name)} byte] : Starting..."
                )

                self.TestSetCreation_creation_update_list_widget_signal.emit(cnt)

                result = self.execute(file_path=file_name)

                # ✅ 성공/실패 분류
                if result["success"]:
                    all_data.extend(result["data"])
                else:
                    failed_files.append(result)

                self.TestSetCreation_progress_signal.emit(cnt + 1)
                self.TestSetCreation_text_update_signal.emit(
                    f"{os.path.basename(file_name)} [{self.get_file_size(file_name)} byte] : Done."
                )

                self.msleep(500)

            if self.thread_run:
                self.save_json(file_path=self.output_path, data=all_data, use_encoding=True)
                self.save_json(file_path=self.failed_path, data=failed_files, use_encoding=True)

            self.TestSetCreation_finished_thread_signal.emit()

        except Exception as e:
            handle_exception()

    def stop(self):
        # log_info("info", "Thread 종료")
        self.thread_run = False
        self.quit()
        if not self.wait(3000):  # 3초 기다려도 종료되지 않으면 강제 종료
            self.terminate()
