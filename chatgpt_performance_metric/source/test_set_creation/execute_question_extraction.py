import sys
import os
import easygui
from datetime import datetime
import pytz

from PyQt5 import QtWidgets, QtCore

from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.graph import KnowledgeGraph
from ragas.testset.transforms import default_transforms, apply_transforms
from ragas.testset.graph import Node, NodeType
from ragas.testset.synthesizers import default_query_distribution
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset.synthesizers.single_hop.specific import (
    SingleHopSpecificQuerySynthesizer,
)
from ragas.testset.synthesizers.multi_hop import (
    MultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer,
)
from langchain_community.document_loaders import TextLoader
import fnmatch

######################################################################
# 아래 매우 중요
# question creator는 별도 프로세스로 수행되기에 context.py와 같이 상대 경로 안됨.
# 따라서 sys등록후 이를 이용해야 함.
flag_process = True

if flag_process:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')
    from source.__init__ import *
else:
    from .. import *
######################################################################


import nltk

nltk.download('punkt')


class TestSetCreation:
    korea_tz = pytz.timezone('Asia/Seoul')

    def __init__(self, src_dir_path=None, test_size=10, gpt_model="gpt-4o", user_name="admin"):
        super().__init__()
        self.test_size = test_size
        self.gpt_model = gpt_model
        self.includeList = ["*.md", "*.txt"]
        self.src_path = src_dir_path
        self.file_list = []  # 추출된 파일 목록 저장
        self.outputPath = "Generate_Question.json"
        self.user = user_name
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

    def execute(self):
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
                else:
                    self.testSetGenFailList.append((file_path, "empty"))

            except Exception as e:
                self.testSetGenFailList.append((file_path, e))

        # 루프 끝나고 전체 리스트를 JSON 파일로 저장
        if all_data:
            self.json_dump_f(file_path=self.outputPath, data=all_data, append=False)


def get_markdown_dir(source_dir):
    dir_ = source_dir
    loader = DirectoryLoader(dir_, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    # print("number of doc: ", len(documents))
    return documents


def get_markdown_files(source_dir):
    md_data = load_document(base_dir=source_dir)
    text_data = load_general(base_dir=source_dir)

    return md_data + text_data


def save_question_groundtruth_to_file(test_set, append, source_dir='', test_server=''):
    if append:
        file_path = os.path.join(os.getcwd(), "TestSet_Result").replace("\\", "/")
    else:
        file_path = easygui.filesavebox(
            msg="Want to Save Test Set File?",
            title="Saving File",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            return False, False

    df = test_set.to_pandas()
    df["file"] = str(source_dir)
    df["retrieved_contexts"] = ""
    df["response"] = ""
    df["chatbot_response"] = ""

    # 한국 시간대 설정
    korea_tz = pytz.timezone('Asia/Seoul')
    # 현재 시간 가져오기
    now = datetime.now(korea_tz)
    df["date_time"] = str(now)

    df["chatbot_server"] = test_server

    if not df.empty:
        json_data = df.to_dict(orient='records')

        # # json_data가 주어진 데이터라고 가정
        # for cnt, data_ in enumerate(json_data):
        #     for key, val in data_.items():
        #         if "eval" in key:
        #             for key2, val2 in val.items():
        #                 if key2 == "retrieved_contexts":
        #                     json_data[cnt][key][key2] = []
        #                     continue
        #                 if val2 is None:
        #                     json_data[cnt][key][key2] = ""

        try:
            modified_json_data, not_present = check_the_answer_is_not_present(data_=json_data)
            ret = json_dump_f(file_path=file_path, data=modified_json_data, append=append)

            # # CSV 저장
            # csv_file_path = file_path.replace('.json', '.csv') + ".csv"  # JSON 파일명을 기반으로 CSV 파일명 생성

            # if append:
            #     df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
            # else:
            #     df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')  # CSV 저장

            return ret, not_present

        except Exception as e:
            # print(f"Error saving the file: {e}")
            return False, False


def complete_creating_question_groundTruth(test_set, query_synthesize=None, append=False, source_dir='',
                                           test_server=''):
    if append:
        save_question_groundtruth_to_file(test_set=test_set, append=append, source_dir=source_dir,
                                          test_server=test_server)

    else:
        save_successful = False

        # 저장이 성공할 때까지 또는 사용자가 저장을 거부할 때까지 반복
        while not save_successful:
            # QMessageBox 인스턴스를 직접 생성
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Confirm Save...")
            msg_box.setText(
                "Are you sure you want to save the test set(Question, Ground-Truth)?\nIf No, all data will be lost.")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            # Always show the message box on top
            msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            # 메시지 박스를 최상단에 표시
            answer = msg_box.exec_()

            if answer == QtWidgets.QMessageBox.Yes:
                save_successful, not_present = save_question_groundtruth_to_file(test_set=test_set,
                                                                                 test_server=test_server)
                if save_successful:
                    _box = QtWidgets.QMessageBox()
                    _box.setWindowTitle("Saved File")

                    if not_present:
                        _box.setText(
                            f"[Warning] Test set saved successfully.\nBut 'The answer to given is not present' so Remove it")
                    else:
                        _box.setText("Test set saved successfully.\n")

                    _box.setStandardButtons(QtWidgets.QMessageBox.Yes)
                    _box.setWindowFlags(_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

                    _answer = _box.exec_()

                else:
                    # 저장 실패 시 재시도 여부를 묻는 메시지 박스
                    retry_box = QtWidgets.QMessageBox()
                    retry_box.setWindowTitle("Save Failed")
                    retry_box.setText("Saving failed. Do you want to try saving again?")
                    retry_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    retry_box.setWindowFlags(retry_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

                    retry_answer = retry_box.exec_()

                    if retry_answer == QtWidgets.QMessageBox.No:
                        break
            else:
                # print("test set(Question, Ground-Truth) not saved.")
                break


def main(source_dir, test_size, query_synthesize, model, append=False, test_server=''):
    try:
        # QApplication 인스턴스를 먼저 생성
        if not append:
            app = QtWidgets.QApplication(sys.argv)

        # Test 용도
        # loader = DirectoryLoader(source_dir, glob="**/*.txt")
        # docs = loader.load()
        # generator_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
        # generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        # generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
        # test_set = generator.generate_with_langchain_docs(docs, testset_size=test_size)
        # complete_creating_question_groundTruth(test_set=test_set, append=True, source_dir=source_dir,
        #                                        test_server=test_server)
        # return

        generator_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
        generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        transformer_llm = generator_llm
        embedding_model = generator_embeddings

        load_data = get_markdown_files(source_dir=source_dir)
        # loader = DirectoryLoader(source_dir, glob="**/*.md")
        # load_data = loader.load()

        kg = KnowledgeGraph()
        for doc in load_data:
            kg.nodes.append(
                Node(
                    type=NodeType.DOCUMENT,
                    properties={"page_content": doc.page_content, "document_metadata": doc.metadata}
                )
            )

        trans = default_transforms(documents=load_data, llm=transformer_llm, embedding_model=embedding_model)

        apply_transforms(kg, trans)

        # cwd = os.path.join(os.getcwd(), 'knowledge_graph.json')
        # kg.save(cwd)
        # loaded_kg = KnowledgeGraph.load(cwd)

        generator = TestsetGenerator(llm=generator_llm, embedding_model=embedding_model, knowledge_graph=kg)

        # query_distribution = default_query_distribution(generator_llm)
        # # print(query_distribution)

        query_distribution = [
            (SingleHopSpecificQuerySynthesizer(llm=generator_llm),
             query_synthesize["SingleHopSpecificQuerySynthesizer"]),
            (MultiHopAbstractQuerySynthesizer(llm=generator_llm), query_synthesize["MultiHopAbstractQuerySynthesizer"]),
            (MultiHopSpecificQuerySynthesizer(llm=generator_llm), query_synthesize["MultiHopSpecificQuerySynthesizer"]),
        ]

        if len(load_data) == 0:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Check Files...")
            msg_box.setText(
                "There are no available files (either 0 bytes or unsupported format).\nPlease check the file size and format [*.md, *.txt]\n")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
            # Always show the message box on top
            msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            # 메시지 박스를 최상단에 표시
            answer = msg_box.exec_()

        else:
            # print("----------------------------------------------------------------")
            # print(test_size)
            # print(query_distribution)

            test_set = generator.generate(testset_size=test_size, query_distribution=query_distribution)

            complete_creating_question_groundTruth(test_set=test_set, append=append, source_dir=source_dir,
                                                   test_server=test_server)

        # QApplication 종료
        # print(source_dir)

        if not append:
            sys.exit(0)

    except Exception as e:
        path = os.path.join(os.getcwd(), "TestSet_Fail.txt")  # 현재 작업 디렉터리에 'err_file.txt' 지정
        with open(path, "w", encoding="utf-8") as file:  # "a+" 모드 사용 (append write)
            file.write(f"{source_dir}'\n'   : {e}\n\n")  # 줄바꿈 포함하여 내용 추가


if __name__ == "__main__":

    individual_file = True

    if individual_file:  # file 하나 씩 생성
        source_dir = sys.argv[1]
        test_size = int(sys.argv[2])
        SpecificQuerySynthesizer_ratio = float(sys.argv[3])
        ComparativeAbstractQuerySynthesizer_ratio = float(sys.argv[4])
        AbstractQuerySynthesizer_ratio = float(sys.argv[5])
        model = sys.argv[6]
        openaikey = sys.argv[7]
        os.environ["OPENAI_API_KEY"] = openaikey
        chatbot_server = sys.argv[8]
        user_name = sys.argv[9]

        instance = TestSetCreation(src_dir_path=source_dir.replace("\\", "/"), test_size=test_size, gpt_model=model,
                                   user_name=user_name)
        instance.execute()

        if len(instance.testSetGenFailList) != 0:
            ErrorPath = "Fail_Generate_Question.txt"

            with open(ErrorPath, "w", encoding="utf-8") as f:
                for data in instance.testSetGenFailList:
                    file = data[0]  # 파일명
                    reason = data[1]  # 실패 원인
                    f.write(f"{file}\nReason: {reason}\n\n")

            print("실패한 파일이 있음. Fail_Generate_Question.txt 파일을 학인하세요")

        # def find_files(root_dir, extensions):
        #     found_files = []
        #     for dirpath, _, filenames in os.walk(root_dir):
        #         for filename in filenames:
        #             if any(filename.lower().endswith(ext) for ext in extensions):
        #                 found_files.append(os.path.join(dirpath, filename))
        #     return found_files
        #
        #
        # file_extensions = [".md", ".txt"]
        #
        # files = find_files(source_dir, file_extensions)
        #
        # for idx, file in enumerate(files):
        #     print(rf"[{idx+1}/{len(files)}] Generating.... Wait until Finished.   File: {file}")
        #
        #     query_synthesize = {
        #         "SingleHopSpecificQuerySynthesizer": SpecificQuerySynthesizer_ratio,
        #         "MultiHopAbstractQuerySynthesizer": ComparativeAbstractQuerySynthesizer_ratio,
        #         "MultiHopSpecificQuerySynthesizer": AbstractQuerySynthesizer_ratio
        #     }
        #
        #     main(source_dir=file, test_size=test_size, query_synthesize=query_synthesize, model=model, append=True, test_server=chatbot_server)
        #
        print("Completed Test Generation..")

    else:
        if len(sys.argv) >= 4:  # main.py gui parameter 전달 받음
            source_dir = sys.argv[1]
            test_size = int(sys.argv[2])
            SpecificQuerySynthesizer_ratio = float(sys.argv[3])
            ComparativeAbstractQuerySynthesizer_ratio = float(sys.argv[4])
            AbstractQuerySynthesizer_ratio = float(sys.argv[5])
            model = sys.argv[6]
            openaikey = sys.argv[7]
            os.environ["OPENAI_API_KEY"] = openaikey
            chatbot_server = sys.argv[8]
            user_name = sys.argv[9]
            # print("given from main.py")
        else:
            # os.environ["OPENAI_API_KEY"] = ""
            # main.py의 gui 에서 실행한 경우가 아니고 단독으로 test_set_Creator.py를 실행한 경우
            source_dir = rf"C:\Users\User\Downloads\20250317_input\Input\testset_2503\fail"

            test_size = 10
            SpecificQuerySynthesizer_ratio = 1.0
            ComparativeAbstractQuerySynthesizer_ratio = 0.0
            AbstractQuerySynthesizer_ratio = 0.0
            model = "gpt-4o-mini"
            chatbot_server = ""
            user_name = "admin"
            # print("given from test_set_creator.py")

        query_synthesize = {
            "SingleHopSpecificQuerySynthesizer": SpecificQuerySynthesizer_ratio,
            "MultiHopAbstractQuerySynthesizer": ComparativeAbstractQuerySynthesizer_ratio,
            "MultiHopSpecificQuerySynthesizer": AbstractQuerySynthesizer_ratio
        }

        # main 함수 실행
        main(source_dir=source_dir, test_size=test_size, query_synthesize=query_synthesize, model=model,
             test_server=chatbot_server)
