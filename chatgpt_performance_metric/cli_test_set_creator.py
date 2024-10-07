import sys
import os
import json
import easygui
from PyQt5 import QtWidgets, QtCore

from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import CharacterTextSplitter

import nltk

nltk.download('punkt')


def load_markdown(data_path):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    with open(data_path, 'r') as file:
        data_string = file.read()
        documents = markdown_splitter.split_text(data_string)

        # 파일명을 metadata에 추가
        domain = data_path  # os.path.basename(data_path)
        for doc in documents:
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata["domain"] = domain  # Document 객체의 metadata 속성에 파일명 추가

        return documents

    # with open(data_path, 'r') as file:
    #     data_string = file.read()
    #     return markdown_splitter.split_text(data_string)


def load_txt(data_path):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        length_function=len,
        is_separator_regex=False,
    )

    with open(data_path, 'r') as file:
        data_string = file.read().split("\n")
        domain = data_path  # os.path.basename(data_path)
        documents = text_splitter.create_documents(data_string)

        for doc in documents:
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata["domain"] = domain  # Document 객체의 metadata 속성에 파일명 추가

        return documents
    # with open(data_path, 'r') as file:
    #     data_string = file.read().split("\n")
    #     domain = os.path.splitext(os.path.basename(data_path))[0]
    #     metadata = [{"domain": domain} for _ in data_string]
    #     return text_splitter.create_documents(
    #         data_string,
    #         metadata
    #     )


def load_general(base_dir):
    data = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if ".txt" in file:
                data += load_txt(os.path.join(root, file))

    return data


def load_document(base_dir):
    data = []
    cnt = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if ".md" in file:
                cnt += 1
                data += load_markdown(os.path.join(root, file))

    print(f"the number of md files is : {cnt}")
    return data


def X_get_markdown_files(source_dir):
    dir_ = source_dir
    loader = DirectoryLoader(dir_, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    print("number of doc: ", len(documents))
    return documents


def get_markdown_files(source_dir):
    md_data = load_document(base_dir=source_dir)
    return md_data


def save_test_set(test_set):
    file_path = easygui.filesavebox(
        msg="Want to Save Test Set File?",
        title="Saving File",
        default="*.json",
        filetypes=["*.json"]
    )

    if file_path is None:
        return False

    if not file_path.endswith(".json"):
        file_path += ".json"

    df = test_set.to_pandas()

    if not df.empty:
        json_data = df[['question', 'contexts', 'ground_truth', 'evolution_type', 'metadata']].to_dict(
            orient='records')

        # json_data가 주어진 데이터라고 가정
        for data_ in json_data:
            for key, val in data_.items():
                if key == "contexts":
                    data_["contexts"] = []  # contexts만 빈 리스트로 초기화
            data_["answer"] = ""

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving the file: {e}")
            return False


def main(source_dir, test_size, simple_ratio, reasoning_ratio, multi_complex_ratio, model):
    # QApplication 인스턴스를 먼저 생성
    app = QtWidgets.QApplication(sys.argv)

    generator_llm = ChatOpenAI(model=model)
    critic_llm = ChatOpenAI(model="gpt-4o")
    embeddings = OpenAIEmbeddings()
    generator = TestsetGenerator.from_langchain(
        generator_llm, critic_llm, embeddings
    )

    test_set = generator.generate_with_langchain_docs(get_markdown_files(source_dir=source_dir),
                                                      test_size=test_size,
                                                      distributions={simple: simple_ratio, reasoning: reasoning_ratio,
                                                                     multi_context: multi_complex_ratio}
                                                      )

    save_successful = False

    # 저장이 성공할 때까지 또는 사용자가 저장을 거부할 때까지 반복
    while not save_successful:
        # QMessageBox 인스턴스를 직접 생성
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Confirm Save...")
        msg_box.setText("Are you sure you want to save the test set?\nIf No, all data will be lost.")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        # Always show the message box on top
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # 메시지 박스를 최상단에 표시
        answer = msg_box.exec_()

        if answer == QtWidgets.QMessageBox.Yes:
            save_successful = save_test_set(test_set=test_set)
            if save_successful:
                print("Test set saved successfully.")
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
            print("Test set not saved.")
            break

    # QApplication 종료
    sys.exit(0)


if __name__ == "__main__":
    # OpenAI API 키 설정

    if len(sys.argv) == 8:  # main.py gui parameter 전달 받음
        source_dir = sys.argv[1]
        test_size = int(sys.argv[2])
        simple_ratio = float(sys.argv[3])
        reasoning_ratio = float(sys.argv[4])
        multi_complex_ratio = float(sys.argv[5])
        model = sys.argv[6]
        openaikey = sys.argv[7]
        os.environ["OPENAI_API_KEY"] = openaikey
        print("given from main.py")
    else:
        os.environ["OPENAI_API_KEY"] = ""

        # main.py의 gui 에서 실행한 경우가 아니고 단독으로 test_set_Creator.py를 실행한 경우
        source_dir = rf"C:\exynos-ai-studio-docs-main_240924"
        test_size = 10
        simple_ratio = 0.9
        reasoning_ratio = 0.1
        multi_complex_ratio = 0.0
        model = "gpt-4o"
        print("given from test_set_creator.py")

    # main 함수 실행
    main(source_dir=source_dir, test_size=test_size, simple_ratio=simple_ratio, reasoning_ratio=reasoning_ratio,
         multi_complex_ratio=multi_complex_ratio,
         model=model)
