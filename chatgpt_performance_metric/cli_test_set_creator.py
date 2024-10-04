import sys
import os
import json
import easygui
from PyQt5 import QtWidgets

from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader

import nltk

nltk.download('punkt')


def get_markdown_files(s_d):
    dir_ = s_d
    loader = DirectoryLoader(dir_, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    print("number of doc: ", len(documents))
    return documents


def save_test_set(test_set):
    file_path = easygui.filesavebox(
        msg="Want to Save Test Set File?",
        title="Saving File",
        default="*.json",
        filetypes=["*.json"]
    )

    if not file_path:
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

    test_set = generator.generate_with_langchain_docs(get_markdown_files(source_dir),
                                                      test_size=test_size,
                                                      distributions={simple: simple_ratio, reasoning: reasoning_ratio,
                                                                     multi_context: multi_complex_ratio},
                                                      raise_exceptions=False
                                                      )

    save_successful = False

    # 저장이 성공할 때까지 또는 사용자가 저장을 거부할 때까지 반복
    while not save_successful:
        answer = QtWidgets.QMessageBox.question(None,
                                                "Confirm Save...",
                                                "Are you sure you want to save the test set?\nIf No, all data will be lost.",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if answer == QtWidgets.QMessageBox.Yes:
            save_successful = save_test_set(test_set=test_set)
            if save_successful:
                print("Test set saved successfully.")
            else:
                retry_answer = QtWidgets.QMessageBox.question(None,
                                                              "Save Failed",
                                                              "Saving failed. Do you want to try saving again?",
                                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if retry_answer == QtWidgets.QMessageBox.No:
                    break
        else:
            print("Test set not saved.")
            break

    # QApplication 종료
    sys.exit(0)


if __name__ == "__main__":
    # OpenAI API 키 설정
    os.environ["OPENAI_API_KEY"] = ""

    if len(sys.argv) == 7:    # main.py gui parameter 전달 받음
        source_dir = sys.argv[1]
        test_size = int(sys.argv[2])
        simple_ratio = float(sys.argv[3])
        reasoning_ratio = float(sys.argv[4])
        multi_complex_ratio = float(sys.argv[5])
        model = sys.argv[6]
        # print("given from main.py")
    else:
        # main.py의 gui 에서 실행한 경우가 아니고 단독으로 test_set_Creator.py를 실행한 경우
        source_dir = rf"C:\exynos-ai-studio-docs-main_240924"
        test_size = 10
        simple_ratio = 0.9
        reasoning_ratio = 0.1
        multi_complex_ratio = 0.0
        model = "gpt-4o"
        # print("given from test_set_creator.py")

    # main 함수 실행
    main(source_dir=source_dir, test_size=test_size, simple_ratio=simple_ratio, reasoning_ratio=reasoning_ratio,
         multi_complex_ratio=multi_complex_ratio,
         model=model)
    