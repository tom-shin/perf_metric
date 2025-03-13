import os
import subprocess
import json
import chardet
from collections import OrderedDict

from PyQt5.QtCore import pyqtSignal, QTimer

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QSpacerItem, \
    QSizePolicy, QRadioButton, QWidget

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import CharacterTextSplitter


class ModalLess_ProgressDialog(QWidget):  # popup 메뉴가 있어도 뒤 main gui의 제어가 가능 함
    send_user_close_event = pyqtSignal(bool)

    def __init__(self, message, show=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(message)

        self.resize(400, 100)  # 원하는 크기로 조절

        self.progress_bar = QProgressBar(self)
        self.label = QLabel("", self)
        self.close_button = QPushButton("Close", self)
        self.radio_button = QRadioButton("", self)

        # Create a horizontal layout for the close button and spacer
        h_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout.addSpacerItem(spacer)
        h_layout.addWidget(self.close_button)

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        layout.addWidget(self.radio_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        # Close 버튼 클릭 시 다이얼로그를 닫음
        self.close_button.clicked.connect(self.close)

        if show:
            self.close_button.show()
        else:
            self.close_button.hide()

        # Timer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_radio_button)
        self.timer.start(500)  # 500ms 간격으로 토글

        self.radio_state = False  # 깜빡임 상태 초기화

    def setProgressBarMaximum(self, max_value):
        self.progress_bar.setMaximum(int(max_value))

    def onCountChanged(self, value):
        self.progress_bar.setValue(int(value))

    def onProgressTextChanged(self, text):
        self.label.setText(text)

    def showModal_less(self):
        self.showModal()

    def showModal(self):
        self.show()

    def closeEvent(self, event):
        subprocess.run("taskkill /f /im cmd.exe /t", shell=True)

        self.send_user_close_event.emit(True)
        event.accept()

    def toggle_radio_button(self):
        if self.radio_state:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: red;
                            border-radius: 5px;
                        }
                    """)
        else:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: blue;
                            border-radius: 5px;
                        }
                    """)
        self.radio_state = not self.radio_state


class Modal_ProgressDialog(QDialog):  # popup 메뉴가 있으면 뒤 main gui의 제어 불 가능 -> modal
    send_user_close_event = pyqtSignal(bool)

    def __init__(self, message, show=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(message)
        self.setModal(True)

        self.resize(400, 100)  # 원하는 크기로 조절

        self.progress_bar = QProgressBar(self)
        self.label = QLabel("", self)
        self.close_button = QPushButton("Close", self)
        self.radio_button = QRadioButton("", self)

        # Create a horizontal layout for the close button and spacer
        h_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        h_layout.addSpacerItem(spacer)
        h_layout.addWidget(self.close_button)

        # Create the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.label)
        layout.addWidget(self.radio_button)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        # Close 버튼 클릭 시 다이얼로그를 닫음
        self.close_button.clicked.connect(self.close)

        if show:
            self.close_button.show()
        else:
            self.close_button.hide()

        # Timer 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_radio_button)
        self.timer.start(500)  # 500ms 간격으로 토글

        self.radio_state = False  # 깜빡임 상태 초기화

    def setProgressBarMaximum(self, max_value):
        self.progress_bar.setMaximum(int(max_value))

    def onCountChanged(self, value):
        self.progress_bar.setValue(int(value))

    def onProgressTextChanged(self, text):
        self.label.setText(text)

    def showModal(self):
        super().exec_()

    def showModal_less(self):
        super().show()

    def closeEvent(self, event):
        self.send_user_close_event.emit(True)
        event.accept()

    def toggle_radio_button(self):
        if self.radio_state:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: red;
                            border-radius: 5px;
                        }
                    """)
        else:
            self.radio_button.setStyleSheet("""
                        QRadioButton::indicator {
                            width: 12px;
                            height: 12px;
                            background-color: blue;
                            border-radius: 5px;
                        }
                    """)
        self.radio_state = not self.radio_state


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
        else:
            existing_data = []  # 파일이 없거나 비어있으면 빈 리스트로 초기화

        # 새로운 데이터 추가
        if isinstance(existing_data, list):
            existing_data.append(data)  # 리스트라면 추가
        elif isinstance(existing_data, dict):
            existing_data.update(data)  # 딕셔너리라면 업데이트

        # JSON 파일에 다시 저장 (덮어쓰기)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
    else:
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)

    return True


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


def load_markdown(data_path):
    with open(data_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    with open(data_path, 'r', encoding=encoding) as file:
        # print(data_path)
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
    with open(data_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    text_splitter = CharacterTextSplitter(
        separator="\n",
        length_function=len,
        is_separator_regex=False,
    )

    with open(data_path, 'r', encoding=encoding) as file:
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
    cnt = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 0:
                    cnt += 1
                    data += load_txt(file_path)

    # print(f"the number of txt files is : {cnt}")
    return data


def load_document(base_dir):
    data = []
    cnt = 0

    if os.path.isdir(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    if os.path.getsize(file_path) > 0:
                        cnt += 1
                        data += load_markdown(file_path)

    elif os.path.isfile(base_dir):
        if base_dir.endswith(".md"):
            if os.path.getsize(base_dir) > 0:
                cnt += 1
                data += load_markdown(base_dir)

    else:
        print("No File")

    # print(f"the number of md files is : {cnt}")
    return data


def check_the_answer_is_not_present(data_=None):
    return data_, False   # 아래 check skip하고다 할 때

    # json_data = data_
    # modified_json_data = []
    # abnormal_cnt = 0
    #
    # ERR_KEYWORD = ["not present", "We do not have the information you requested"]
    #
    # for cnt, t_set in enumerate(json_data):    # json data :eval, query type 모두 포함 되어 있음.
    #
    #     exist_error = False
    #     for value in t_set.values():
    #         if type(value) is str:
    #             continue
    #
    #         for compare_s in value.values():
    #
    #             if type(compare_s) is str:
    #                 if any(keyword in value for keyword in ERR_KEYWORD):
    #                     exist_error = True
    #                     abnormal_cnt += 1
    #                     break
    #             elif type(compare_s) is list:
    #                 for sub_ in compare_s:
    #                     if any(keyword in sub_ for keyword in ERR_KEYWORD):
    #                         exist_error = True
    #                         abnormal_cnt += 1
    #                         break
    #             if exist_error:
    #                 break
    #         if exist_error:
    #             break
    #
    #     if not exist_error:
    #         modified_json_data.append(t_set)
    #
    # if abnormal_cnt == 0:
    #     exist_error = False
    # else:
    #     exist_error = True
    #
    # print(f" >>>>>>>>>>>>>>>> SKIP Test Set: {abnormal_cnt}")
    # return modified_json_data, exist_error



