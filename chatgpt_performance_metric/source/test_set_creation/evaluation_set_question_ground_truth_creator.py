import sys
import os
import easygui

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


def save_question_groundtruth_to_file(test_set, append, source_dir=''):
    if append:
        file_path = os.path.join(os.getcwd(), "result").replace("\\", "/")
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

            # CSV 저장
            csv_file_path = file_path.replace('.json', '.csv') + ".csv"  # JSON 파일명을 기반으로 CSV 파일명 생성

            if append:
                df.to_csv(csv_file_path, mode='a', index=False, encoding='utf-8-sig', header=False)
            else:
                df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')  # CSV 저장

            return ret, not_present

        except Exception as e:
            # print(f"Error saving the file: {e}")
            return False, False


def complete_creating_question_groundTruth(test_set, query_synthesize=None, append=False, source_dir=''):

    if append:
        save_question_groundtruth_to_file(test_set=test_set, append=append, source_dir=source_dir)

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
                save_successful, not_present = save_question_groundtruth_to_file(test_set=test_set)
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


def main(source_dir, test_size, query_synthesize, model, append=False):
    try:
        # QApplication 인스턴스를 먼저 생성
        if not append:
            app = QtWidgets.QApplication(sys.argv)

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

            complete_creating_question_groundTruth(test_set=test_set, append=append, source_dir=source_dir)

        # QApplication 종료
        # print(source_dir)
        if not append:
            sys.exit(0)

    except Exception as e:
        path = os.path.join(os.getcwd(), "err_file.txt")  # 현재 작업 디렉터리에 'err_file.txt' 지정
        with open(path, "a+", encoding="utf-8") as file:  # "a+" 모드 사용 (append write)
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

        def find_files(root_dir, extensions):
            found_files = []
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        found_files.append(os.path.join(dirpath, filename))
            return found_files


        file_extensions = [".md", ".txt"]

        files = find_files(source_dir, file_extensions)

        for idx, file in enumerate(files):
            print(rf"[{idx+1}/{len(files)}] Generating.... Wait until Finished.   File: {file}")

            query_synthesize = {
                "SingleHopSpecificQuerySynthesizer": SpecificQuerySynthesizer_ratio,
                "MultiHopAbstractQuerySynthesizer": ComparativeAbstractQuerySynthesizer_ratio,
                "MultiHopSpecificQuerySynthesizer": AbstractQuerySynthesizer_ratio
            }

            main(source_dir=file, test_size=test_size, query_synthesize=query_synthesize, model=model, append=True)

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
            # print("given from main.py")
        else:
            # os.environ["OPENAI_API_KEY"] = ""
            # main.py의 gui 에서 실행한 경우가 아니고 단독으로 test_set_Creator.py를 실행한 경우
            source_dir = rf"C:\Users\User\Downloads\new_doc\ECO25_MX_Doc\documentation\getting-started-with-android-samples\guide"

            test_size = 2
            SpecificQuerySynthesizer_ratio = 1.0
            ComparativeAbstractQuerySynthesizer_ratio = 0.0
            AbstractQuerySynthesizer_ratio = 0.0
            model = "gpt-4o-mini"
            # print("given from test_set_creator.py")

        query_synthesize = {
            "SingleHopSpecificQuerySynthesizer": SpecificQuerySynthesizer_ratio,
            "MultiHopAbstractQuerySynthesizer": ComparativeAbstractQuerySynthesizer_ratio,
            "MultiHopSpecificQuerySynthesizer": AbstractQuerySynthesizer_ratio
        }

        # main 함수 실행
        main(source_dir=source_dir, test_size=test_size, query_synthesize=query_synthesize, model=model)
