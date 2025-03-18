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


class TestSetCreation(QThread):
    os.environ["OPENAI_API_KEY"] = "sk-"
    korea_tz = pytz.timezone('Asia/Seoul')

    def __init__(self, src_dir_path=None, user="admin"):
        super().__init__()
        self.test_size = 1
        self.gpt_model = "gpt-4o-mini"
        self.includeList = ["*.md", "*.txt"]
        self.src_path = src_dir_path
        self.file_list = []  # 추출된 파일 목록 저장
        self.outputPath = "output.json"
        self.user = user
        self.testSetGenFailList = []

        self.extractFileList()

    def extractFileList(self):
        self.file_list = []
        for root, _, files in os.walk(self.src_path):
            for pattern in self.includeList:
                matched_files = fnmatch.filter(files, pattern)
                for file in matched_files:
                    full_path = os.path.join(root, file)
                    self.file_list.append(full_path)

    @staticmethod
    def json_dump_f(file_path, data, use_encoding=False, append=False):
        if file_path is None:
            return False

        if not file_path.endswith(".json"):
            file_path += ".json"

        if use_encoding:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']
        else:
            encoding = "utf-8"

        if append:
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)  # 기존 데이터 로드

                # 새로운 데이터 추가
                existing_data.extend(data)  # 리스트라면 추가

            else:
                existing_data = data  # 파일이 없거나 비어있으면 빈 리스트로 초기화

            # JSON 파일에 다시 저장 (덮어쓰기)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
        else:
            with open(file_path, "w", encoding=encoding) as f:
                json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)

        return True

    def run(self):
        generator_llm = LangchainLLMWrapper(ChatOpenAI(model=self.gpt_model))
        generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

        all_data = []

        for file_ in self.file_list:
            file_path = file_.replace("\\", "/")
            try:
                loader = TextLoader(file_path, autodetect_encoding=True)
                docs = loader.load()

                generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
                dataset = generator.generate_with_langchain_docs(docs, testset_size=self.test_size)

                df = dataset.to_pandas()

                """ 추가 필드 """
                df["file"] = file_path  # 파일 경로 추가
                df["retrieved_contexts"] = ""
                df["response"] = ""
                df["chatbot_response"] = ""
                df["user_comment"] = ""
                df["date_time"] = str(datetime.now(self.korea_tz))
                df["chatbot_server"] = ""
                df["user"] = self.user

                if not df.empty:
                    json_data = df.to_dict(orient='records')  # 리스트 of dict
                    all_data.extend(json_data)  # 하나씩 추가

            except Exception as e:
                self.testSetGenFailList.append((file_path, e))

        # 루프 끝나고 전체 리스트를 JSON 파일로 저장
        if all_data:
            self.json_dump_f(file_path=self.outputPath, data=all_data, append=False)


path = rf"C:\Users\User\Downloads\20250317_input\Input\testset_2503"
instance = TestSetCreation(src_dir_path=path.replace("\\", "/"))
instance.start()
instance.wait()
print(instance.testSetGenFailList)

