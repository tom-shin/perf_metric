from PyQt5.QtCore import QThread, pyqtSignal
from ..head import handle_exception


class ExampleThread(QThread):
    ExampleThread_progress_signal = pyqtSignal(int)
    ExampleThread_text_update_signal = pyqtSignal(str)
    ExampleThread_finished_thread_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.thread_run = False

    def run(self):
        try:
            self.thread_run = True
            for i in range(11):  # 0 ~ 10까지 진행
                if not self.thread_run:
                    break

                self.ExampleThread_progress_signal.emit(i)
                self.ExampleThread_text_update_signal.emit(f"{i}th done")
                self.msleep(500)

            self.ExampleThread_finished_thread_signal.emit()

        except Exception as e:
            handle_exception()

    def stop(self):
        self.thread_run = False
        self.quit()
        self.wait(3000)
