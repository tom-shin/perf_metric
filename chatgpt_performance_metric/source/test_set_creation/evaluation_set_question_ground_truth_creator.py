import sys
import os
import easygui

from PyQt5 import QtWidgets, QtCore

from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

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
    print("number of doc: ", len(documents))
    return documents


def get_markdown_files(source_dir):
    md_data = load_document(base_dir=source_dir)
    text_data = load_general(base_dir=source_dir)

    return md_data + text_data


def save_question_groundtruth_to_file(test_set):
    file_path = easygui.filesavebox(
        msg="Want to Save Test Set File?",
        title="Saving File",
        default="*.json",
        filetypes=["*.json"]
    )

    if file_path is None:
        return False, False

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
            modified_json_data, not_present = check_the_answer_is_not_present(data_=json_data)

            ret = json_dump_f(file_path=file_path, data=modified_json_data)
            return ret, not_present

        except Exception as e:
            print(f"Error saving the file: {e}")
            return False


def complete_creating_question_groundTruth(test_set):
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
                        "[Warning] Test set saved successfully.\nBut 'The answer to given is not present' so Remove it")
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
            print("test set(Question, Ground-Truth) not saved.")
            break


def main(source_dir, test_size, simple_ratio, reasoning_ratio, multi_complex_ratio, model):
    # QApplication 인스턴스를 먼저 생성
    app = QtWidgets.QApplication(sys.argv)

    generator_llm = ChatOpenAI(model=model)
    critic_llm = ChatOpenAI(model="gpt-4o")
    embeddings = OpenAIEmbeddings()
    generator = TestsetGenerator.from_langchain(
        generator_llm, critic_llm, embeddings
    )

    load_data = get_markdown_files(source_dir=source_dir)

    if len(load_data) == 0:
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Check Files...")
        msg_box.setText("There are no available files (either 0 bytes or unsupported format).\nPlease check the file size and format [*.md, *.txt]\n")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
        # Always show the message box on top
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # 메시지 박스를 최상단에 표시
        answer = msg_box.exec_()

    else:
        test_set = generator.generate_with_langchain_docs(load_data,
                                                          test_size=test_size,
                                                          distributions={simple: simple_ratio,
                                                                         reasoning: reasoning_ratio,
                                                                         multi_context: multi_complex_ratio}
                                                          )

        complete_creating_question_groundTruth(test_set=test_set)

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
        source_dir = rf"C:\ai_studio_2.0_markdown_documentation"
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
