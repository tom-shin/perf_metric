import easygui

from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets, QtCore

from .. import *  # __init__ 호출

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Creating_Contexts_Answer_thread(QThread):
    progress_status = pyqtSignal(int, int)
    complete_creating_context_answer_sig = pyqtSignal(list)

    def __init__(self, library, data):
        super().__init__()

        self.tg = library
        self.json_data = data
        self.running = True

    def run(self):
        for i, obj in enumerate(self.json_data):

            if not self.running:
                break

            response = self.tg.answer_question(obj["eval_sample"]["user_input"])
            obj["eval_sample"].update({"retrieved_contexts": response["list"], "response": response["response"]})

            self.progress_status.emit(i + 1, len(self.json_data))

        if self.running:
            self.complete_creating_context_answer_sig.emit(self.json_data)
            # self.save_test_data(result_data=json_data)

        # subprocess.run("taskkill /f /im cmd.exe /t", shell=True)

    def stop(self):
        self.running = False
        subprocess.run("taskkill /f /im cmd.exe /t", shell=True)
        self.quit()
        self.wait(3000)


def save_context_answer_to_file(result_data):
    file_path = easygui.filesavebox(
        msg="Want to Save Test Set File?",
        title="Saving File",
        default="*.json",
        filetypes=["*.json"]
    )

    if file_path is None:
        return False, False

    modified_json_data, not_present = check_the_answer_is_not_present(data_=result_data)
    ret = json_dump_f(file_path=file_path, data=modified_json_data)

    return True, not_present


class generator_context_answer_class:
    def __init__(self, parent, tg):
        self.rag_test_process = None
        self.update_rag_test_process = None
        self.parent = parent
        self.tg = tg

    @staticmethod
    def db_connection():
        batch_path = os.path.join(BASE_DIR, "set_env_for_ragas", "set.bat")
        batch_dir = os.path.dirname(batch_path)

        try:
            # subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', batch_path], cwd=batch_dir, shell=True)
            subprocess.run(['cmd', '/c', 'start', 'cmd', '/k', batch_path], cwd=batch_dir, shell=True)

        except Exception as e:
            print(f"Error while running batch file: {e}")

    def progress_for_creating_context_answer(self, current_idx, max_idx):
        message = f"Generating Ragas {current_idx}/{max_idx}"
        if self.update_rag_test_process is not None:
            # self.update_rag_test_process.setProgressBarMaximum(max_value=max_idx)
            self.update_rag_test_process.onCountChanged(value=current_idx)
            self.update_rag_test_process.onProgressTextChanged(text=message)

    def complete_creating_context_answer(self, result_data):
        if self.update_rag_test_process is not None:
            self.update_rag_test_process.close()

        save_successful = False

        # 저장이 성공할 때까지 또는 사용자가 저장을 거부할 때까지 반복
        while not save_successful:
            # QMessageBox 인스턴스를 직접 생성
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Confirm Save...")
            msg_box.setText(
                "Are you sure you want to save the test set(Contexts, Answer)?\nIf No, all data will be lost.")

            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            # Always show the message box on top
            msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            # 메시지 박스를 최상단에 표시
            answer = msg_box.exec_()

            if answer == QtWidgets.QMessageBox.Yes:
                save_successful, not_present = save_context_answer_to_file(result_data=result_data)
                if save_successful:
                    _box = QtWidgets.QMessageBox()
                    _box.setWindowTitle("Saved File")

                    if not_present:
                        _box.setText(
                            f"[Warning] Evaluation set saved successfully.\nBut 'The answer to given is not present' so Remove it")
                    else:
                        _box.setText("Evaluation set saved successfully.\n")

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
                print("\ntest set(Contexts, Answer) not saved.")
                break

        # subprocess.run("taskkill /f /im cmd.exe /t", shell=True)

    def start_set_generation(self):
        ret, json_data = json_load_f(file_path=self.parent.embed_open_scenario_file)
        if not ret:
            return

        if self.parent.mainFrame_ui.popctrl_radioButton.isChecked():
            self.update_rag_test_process = ModalLess_ProgressDialog(message="Contexts and Answer Creating")
        else:
            self.update_rag_test_process = Modal_ProgressDialog(message="Contexts and Answer Creating")

        self.update_rag_test_process.setProgressBarMaximum(max_value=len(json_data))

        self.update_rag_test_process.setWindowFlags(
            self.update_rag_test_process.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.rag_test_process = Creating_Contexts_Answer_thread(library=self.tg,
                                                                data=json_data
                                                                )
        self.rag_test_process.progress_status.connect(self.progress_for_creating_context_answer)
        self.rag_test_process.complete_creating_context_answer_sig.connect(self.complete_creating_context_answer)
        self.rag_test_process.start()

        self.update_rag_test_process.showModal_less()
