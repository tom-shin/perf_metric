import threading
import easygui
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, QThread

from .configuration.model_config import *
from .. import *
from ..ui_designer import main_widget


class Load_test_scenario_thread(QtCore.QThread):
    send_scenario_update_ui_sig = QtCore.pyqtSignal(int, dict)
    send_max_scenario_cnt_sig = QtCore.pyqtSignal(int)
    send_finish_scenario_update_ui_sig = QtCore.pyqtSignal()

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        scenario_path = self.file_path

        ret, scenarios = json_load_f(file_path=scenario_path)

        self.send_max_scenario_cnt_sig.emit(len(scenarios) + 1)

        for idx, scenario in enumerate(scenarios):
            user_input = scenario[0]["user_input"]

            reference_contexts = [element + "<context_split>\n" for element in scenario[0]["reference_contexts"]]
            reference = scenario[0]["reference"]

            chatbot_response = scenario[0]["chatbot_response"]

            scenario_data = {
                "user_input": user_input,

                "reference_contexts": reference_contexts,
                "reference": reference,

                "trex_reference": "response from james",
                "chatbot_response": chatbot_response,
                "idx": idx
            }

            self.send_scenario_update_ui_sig.emit(idx, scenario_data)

        self.send_finish_scenario_update_ui_sig.emit()


class Metric_Evaluation_Thread(QThread):
    update_evaluation_progress_status_sig = pyqtSignal(list)
    send_evaluation_network_error_sig = pyqtSignal(str)

    def __init__(self, parent, sub_widget, test_model, method, openai_model, total_progress_count):
        super().__init__()
        self.working = True

        self.parent = parent
        self.sub_widget = sub_widget
        self.max_cnt = int(self.parent.mainFrame_ui.max_iter_spinBox.text())
        self.model = test_model
        self.method = method
        self.openai_model = openai_model
        self.total_progress_count = total_progress_count

        self.progress = 0

    @staticmethod
    def call_metric_function(model, scenario_data, max_iter, thread):
        score = 0

        if "ragas" not in model.lower():
            score = common_llm_model(model=model, scenario_data=scenario_data, max_iter=max_iter,
                                     thread=thread)

        elif "ragas" in model.lower():
            score = common_ragas_metric_model(model=model, scenario_data=scenario_data, max_iter=max_iter,
                                              thread=thread)

        else:
            print("Warning: No Supported Metric Model")
        return model, score

    def evaluate_model(self, args):
        scenario_data, model, idx, cnt, max_iter, thread = args
        model_name, score = self.call_metric_function(model=model, scenario_data=scenario_data, max_iter=max_iter,
                                                      thread=thread)
        result = {
            "model": str(model_name),
            "metric": None,
            "score": str(score),
            "idx": idx,
            "cnt": cnt
        }
        return result

    def run(self):
        self.progress = 0

        for idx, (widget_ui, widget_ui_instance) in enumerate(self.sub_widget):
            if not self.working:
                break

            if widget_ui.scenario_checkBox.isChecked():
                scenario_data = {
                    "user_input": widget_ui.question_plainTextEdit.toPlainText(),
                    "reference_contexts": widget_ui.contexts_plainTextEdit.toPlainText().split("<context_split>\n")[
                                          :-1],
                    "reference": widget_ui.answer_plainTextEdit.toPlainText(),
                    "trex_reference": widget_ui.truth_plainTextEdit.toPlainText(),
                    "chatbot_response": widget_ui.ref_contexts_plainTextEdit.toPlainText()
                }

                # print("===============================================")
                # print(scenario_data)
                # print("===============================================")

                for cnt, (model, metrics) in enumerate(self.model.items()):
                    if not self.working:
                        break

                    checkbox = self.parent.findChild(QtWidgets.QCheckBox, f"metric_{model}_{cnt}")
                    if checkbox.isChecked():
                        try:
                            result = self.evaluate_model(
                                (scenario_data, model, idx, cnt, self.max_cnt, self))

                            result['widget_ui'] = widget_ui
                            result['widget_ui_instance'] = widget_ui_instance
                            self.progress += 1
                            self.update_evaluation_progress_status_sig.emit(
                                [self.progress, self.total_progress_count, result, model])

                        except Exception as e:
                            self.send_evaluation_network_error_sig.emit(
                                f"Error in common_ragas_metric_model for model {model}: {e}")

    def stop(self):
        # print("Evaluation Stop")
        self.working = False
        self.quit()
        self.wait(3000)


class performance_metric_evaluator_class(QObject):
    send_sig_delete_all_sub_widget = pyqtSignal()
    evaluation_finish_save = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.open_scenario_file = None
        self.added_scenario_widgets = None
        self.update_sub_widget_progress = None
        self.update_thread = None
        self.save_progress = None
        self.save_thread = None
        self.update_evaluation_progress = None
        self.eval_thread = None
        self.start_evaluation_time = None
        self.end_evaluation_time = None

        self.send_sig_delete_all_sub_widget.connect(self.evaluation_update_all_sub_widget)
        self.evaluation_finish_save.connect(self.evaluation_finish_save_data)

    def open_file(self, open_scenario_path):
        self.open_scenario_file = open_scenario_path
        self.parent.mainFrame_ui.scenario_path_lineedit.setText(self.open_scenario_file)
        self.parent.mainFrame_ui.scenario_path_lineedit.setReadOnly(True)

        self.refresh_contents_of_evaluation_file()

    def refresh_contents_of_evaluation_file(self):
        while self.parent.mainFrame_ui.formLayout.count():
            item = self.parent.mainFrame_ui.formLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.send_sig_delete_all_sub_widget.emit()

    def evaluation_update_all_sub_widget(self):
        # PRINT_("add_scenario_in_subwidget")

        if self.parent.mainFrame_ui.popctrl_radioButton.isChecked():
            self.update_sub_widget_progress = ModalLess_ProgressDialog(message="Loading Scenario")
        else:
            self.update_sub_widget_progress = Modal_ProgressDialog(message="Loading Scenario")

        self.added_scenario_widgets = []
        self.update_thread = Load_test_scenario_thread(self.open_scenario_file)
        self.update_thread.send_scenario_update_ui_sig.connect(self.add_scenario_widget)
        self.update_thread.send_max_scenario_cnt_sig.connect(self.set_max_progressbar_cnt)
        self.update_thread.send_finish_scenario_update_ui_sig.connect(self.finished_add_scenario_widget)

        self.update_thread.start()

        self.update_sub_widget_progress.showModal_less()

    def add_scenario_widget(self, idx, scenario_data):
        rt = main_widget  # load_module_func(module_name="common.ui_designer.main_widget")
        widget_ui = rt.Ui_Form()
        widget_instance = QtWidgets.QWidget()
        widget_ui.setupUi(widget_instance)

        widget_ui.scenario_checkBox.setText(f"scenario_{idx + 1}")
        widget_ui.question_plainTextEdit.setPlainText(scenario_data["user_input"])
        widget_ui.contexts_plainTextEdit.setPlainText("".join(scenario_data["reference_contexts"]))
        widget_ui.answer_plainTextEdit.setPlainText(scenario_data["reference"])
        widget_ui.truth_plainTextEdit.setPlainText(scenario_data["trex_reference"])
        widget_ui.ref_contexts_plainTextEdit.setPlainText(scenario_data["chatbot_response"])

        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)

        cnt = 0

        def draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name, is_sub=False):
            label = QtWidgets.QLabel(widget_ui.groupBox_2)
            label.setFont(font)
            label.setObjectName(f"label_{idx}_{cnt}")
            label.setText(obj_name)
            widget_ui.formLayout.setWidget(cnt, QtWidgets.QFormLayout.LabelRole, label)

            if not is_sub:
                score_line = QtWidgets.QLineEdit(widget_ui.groupBox_2)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(score_line.sizePolicy().hasHeightForWidth())
                score_line.setSizePolicy(sizePolicy)
                score_line.setMaximumSize(QtCore.QSize(75, 16777215))
                score_line.setFont(font)
                score_line.setObjectName(f"score_line_{idx}_{cnt}")
                widget_ui.formLayout.setWidget(cnt, QtWidgets.QFormLayout.FieldRole, score_line)

        for model, metrics in Models.items():
            if metrics is None:
                draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=model)
                cnt += 1
            else:
                draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=model, is_sub=True)
                cnt += 1
                for sub_metric in metrics:
                    draw_sub_widget_model(widget_ui, idx, cnt, model, metrics, obj_name=sub_metric)
                    cnt += 1

        self.added_scenario_widgets.append((widget_ui, widget_instance))
        self.parent.mainFrame_ui.formLayout.setWidget(idx, QtWidgets.QFormLayout.FieldRole, widget_instance)

        if self.update_sub_widget_progress is not None:
            self.update_sub_widget_progress.onCountChanged(idx)

    def set_max_progressbar_cnt(self, value):
        if self.update_sub_widget_progress is not None:
            # PRINT_("max value", value)
            self.update_sub_widget_progress.setProgressBarMaximum(max_value=value)

    def finished_add_scenario_widget(self):
        if self.update_sub_widget_progress is not None:
            # PRINT_("finished_add_scenario_widget")
            self.update_sub_widget_progress.close()

    def evaluation_reset_score(self):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        for widget_ui, widget_ui_instance in self.added_scenario_widgets:
            # Find all QLineEdit widgets within the current scenario widget
            line_edits = widget_ui_instance.findChildren(QtWidgets.QLineEdit)
            for line_edit in line_edits:
                line_edit.setText("")

    def evaluation_finish_save_data(self):
        if self.save_progress is not None:
            self.save_progress.close()
            print("Save Completed")

    def save_evaluation_result_to_file(self):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        file_path = easygui.filesavebox(
            msg="Want to Save File?",
            title="Saving File",
            default="*.json",
            filetypes=["*.json"]
        )

        if file_path is None:
            self.evaluation_finish_save.emit()
            return

        output_data = []
        progress = 0

        for idx, (widget_ui, widget_ui_instance) in enumerate(self.added_scenario_widgets):
            progress += 1
            self.save_progress.onCountChanged(progress % 99)

            result_out = {"user_input": widget_ui.question_plainTextEdit.toPlainText(),
                          "reference_contexts": widget_ui.contexts_plainTextEdit.toPlainText().split(
                              "<context_split>\n")[:-1],
                          "reference": widget_ui.answer_plainTextEdit.toPlainText(),
                          "trex_reference":  widget_ui.truth_plainTextEdit.toPlainText(),
                          "chatbot_response": widget_ui.ref_contexts_plainTextEdit.toPlainText(),
                          "score": ""
                          }

            score_dict = {}
            for cnt, (model, metric) in enumerate(Models.items()):
                score_line = widget_ui_instance.findChild(QtWidgets.QLineEdit, f"score_line_{idx}_{cnt}")
                if score_line and score_line.text() != "":

                    if "ragas" in model.lower():
                        score_dict[model.split(":")[-1]] = float(score_line.text())
                    else:
                        score_dict[Rag_Models_Metric[model]] = float(score_line.text())

            result_out["score"] = score_dict
            output_data.append(result_out)

        self.save_progress.onCountChanged(100)
        QThread.sleep(1)

        json_dump_f(file_path=file_path, data=output_data)

        self.evaluation_finish_save.emit()

    def save_evaluation_score(self):
        print("complete_test_set_evaluation")

        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        if self.parent.mainFrame_ui.popctrl_radioButton.isChecked():
            self.save_progress = ModalLess_ProgressDialog(message="Saving Result ...")
        else:
            self.save_progress = Modal_ProgressDialog(message="Saving Result ...")

        self.save_thread = threading.Thread(target=self.save_evaluation_result_to_file, daemon=True)
        self.save_thread.start()

        self.save_progress.showModal_less()

    def evaluation_select_all_scenario(self, check):
        if self.added_scenario_widgets is None or len(self.added_scenario_widgets) == 0:
            return

        for scenario_widget, scenario_widget_instance in self.added_scenario_widgets:
            scenario_widget.scenario_checkBox.setChecked(check)

    def model_check(self, check):
        for idx, (model, metric) in enumerate(Models.items()):
            checkbox = self.parent.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")
            checkbox.setChecked(check)

    def check_warning_message(self):
        if self.added_scenario_widgets is None:
            return

        scenario_exist = False
        for widget, widget_instance in self.added_scenario_widgets:
            if widget.scenario_checkBox.isChecked():
                scenario_exist = True
                break

        if not scenario_exist:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Warning...")
            msg_box.setText(
                "Select Test Scenario")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
            # Always show the message box on top
            msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            # 메시지 박스를 최상단에 표시
            answer = msg_box.exec_()
            return False

        metric_exist = False
        for idx, (model, metric) in enumerate(Models.items()):

            checkbox = self.parent.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")

            if checkbox.isChecked():
                metric_exist = True
                break

        if not metric_exist:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Warning...")
            msg_box.setText(
                "Select Test Metric")
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
            # Always show the message box on top
            msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

            # 메시지 박스를 최상단에 표시
            answer = msg_box.exec_()

            return False

        return True

    def total_test_cnt(self):
        selected_scenario_cnt = 0
        for scenario_widget, scenario_widget_instance in self.added_scenario_widgets:
            if scenario_widget.scenario_checkBox.isChecked():
                selected_scenario_cnt += 1

        selected_metric_cnt = 0
        for idx, (model, metric) in enumerate(Models.items()):
            checkbox = self.parent.findChild(QtWidgets.QCheckBox, f"metric_{model}_{idx}")
            if checkbox.isChecked():
                if metric is None:
                    selected_metric_cnt += 1
                else:
                    selected_metric_cnt += len(metric)

        return selected_metric_cnt * selected_scenario_cnt

    def update_evaluation_progress_status(self, event):
        if self.eval_thread is not None:
            # print(event[0], event[1], event[2])

            # 결과 업데이트
            result = event[2]
            widget_ui = result["widget_ui"]
            widget_ui_instance = result["widget_ui_instance"]
            score = result["score"]
            idx = result["idx"]
            cnt = result["cnt"]

            score_line = widget_ui_instance.findChild(QtWidgets.QLineEdit, f"score_line_{idx}_{cnt}")

            if score_line:
                if score == -999:
                    score = "thread terminated"
                elif score == -998:
                    score = "all NaN"

                score_line.setText(score)

            # 프로그래스 바 업데이트
            if int(event[0]) != int(event[1]):
                if self.update_evaluation_progress is not None:
                    self.update_evaluation_progress.onCountChanged(value=str(event[0]))
                    self.update_evaluation_progress.onProgressTextChanged(
                        text=f"\nScenario: {widget_ui.scenario_checkBox.text()}\nModel: {event[3]}\nProgress: {event[0]}/{event[1]}")

            else:
                self.end_evaluation_time = time.time()
                elapsed_time = self.end_evaluation_time - self.start_evaluation_time
                days = elapsed_time // (24 * 3600)
                remaining_secs = elapsed_time % (24 * 3600)
                hours = remaining_secs // 3600
                remaining_secs %= 3600
                minutes = remaining_secs // 60
                seconds = remaining_secs % 60

                total_time = f"{int(days)}day {int(hours)}h {int(minutes)}m {int(seconds)}s"

                self.eval_thread.stop()
                self.update_evaluation_progress.close()

                msg_box = QtWidgets.QMessageBox()
                msg_box.setWindowTitle("Test Done...")
                msg_box.setText(f"All Test Done !       \nElapsed time: {total_time}")
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
                # Always show the message box on top
                msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

                # 메시지 박스를 최상단에 표시
                answer = msg_box.exec_()

    def get_evaluation_network_error(self, event):
        if self.eval_thread is not None:
            self.eval_thread.stop()

        if self.update_evaluation_progress is not None:
            self.update_evaluation_progress.close()

        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("Evaluation Error - Network Error...")
        msg_box.setText(f"{event}")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes)
        # Always show the message box on top
        msg_box.setWindowFlags(msg_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # 메시지 박스를 최상단에 표시
        answer = msg_box.exec_()

    def test_set_analyzation(self):

        if not self.check_warning_message():
            return

        if self.parent.mainFrame_ui.creation_gpt4o_radioButton.isChecked():
            openai_model = "gpt-4o"
        elif self.parent.mainFrame_ui.creation_gpt4omini_radioButton.isChecked():
            openai_model = "gpt-4o-mini"
        else:
            openai_model = "gpt-3.5-turbo-16k"

        cal_method = ""
        if self.parent.mainFrame_ui.iqr_median_radioButton.isChecked():
            cal_method = "IQR-MEDIAN"
        elif self.parent.mainFrame_ui.iqr_mean_radioButton.isChecked():
            cal_method = "IQR-MEAN"
        elif self.parent.mainFrame_ui.mean_radioButton.isChecked():
            cal_method = "MEAN"

        self.evaluation_reset_score()

        if self.parent.mainFrame_ui.popctrl_radioButton.isChecked():
            self.update_evaluation_progress = ModalLess_ProgressDialog(message="Evaluation ...", show=True)
        else:
            self.update_evaluation_progress = Modal_ProgressDialog(message="Evaluation ...", show=True)

        total_progress_count = self.total_test_cnt()
        self.update_evaluation_progress.setProgressBarMaximum(max_value=total_progress_count)

        self.eval_thread = Metric_Evaluation_Thread(parent=self.parent,
                                                    sub_widget=self.added_scenario_widgets,
                                                    test_model=Models,
                                                    method=cal_method,
                                                    openai_model=openai_model,
                                                    total_progress_count=total_progress_count
                                                    )

        self.eval_thread.update_evaluation_progress_status_sig.connect(self.update_evaluation_progress_status)
        self.eval_thread.send_evaluation_network_error_sig.connect(self.get_evaluation_network_error)

        # eval 중 사용자가 취소하고 싶을 때
        self.update_evaluation_progress.send_user_close_event.connect(self.eval_thread.stop)

        self.eval_thread.start()

        self.start_evaluation_time = time.time()

        self.update_evaluation_progress.showModal_less()
