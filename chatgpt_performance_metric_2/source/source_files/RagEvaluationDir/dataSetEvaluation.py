import pytz
import math
from collections import defaultdict

from PyQt5.QtCore import QThread, pyqtSignal
from source.head import handle_exception, FileManager, log_info

from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity


class DataSetEvaluation(QThread, FileManager):
    EvaluationDataset_progress_signal = pyqtSignal(int)
    EvaluationDataset_text_update_signal = pyqtSignal(str)
    EvaluationDataset_finished_thread_signal = pyqtSignal()
    EvaluationDataset_total_sets_cnt_signal = pyqtSignal(int)
    EvaluationDataset_update_list_widget_signal = pyqtSignal(int)

    korea_tz = pytz.timezone('Asia/Seoul')

    def __init__(self, ctrl_parm=None):
        super().__init__()
        self.thread_run = False

        self.ctrl_parm = ctrl_parm
        self.max_iter = ctrl_parm["eval_iter"]

        self.metric = []

        if self.ctrl_parm["eval_metric"]["Faithfulness"]:
            self.metric.append(Faithfulness())
        if self.ctrl_parm["eval_metric"]["LLMContextRecall"]:
            self.metric.append(LLMContextRecall())
        if self.ctrl_parm["eval_metric"]["FactualCorrectness"]:
            self.metric.append(FactualCorrectness())
        if self.ctrl_parm["eval_metric"]["SemanticSimilarity"]:
            self.metric.append(SemanticSimilarity())

        self.evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=self.ctrl_parm["gpt_model"]))
        _, self.eval_sets = self.load_json(file_path=self.ctrl_parm["evaluation_file_path"])

    @staticmethod
    def compute_average(score_list):
        if not score_list:
            return {}

        # 1. 모든 metric key 모으기
        all_keys = set()
        for result in score_list:
            for score_dict in result.scores:
                all_keys.update(score_dict.keys())

        # 2. metric 별 값 모으기
        metric_values = {key: [] for key in all_keys}

        for result in score_list:
            for score_dict in result.scores:
                for key in all_keys:
                    value = score_dict.get(key, None)
                    if value is not None:
                        try:
                            value = float(value)
                            if not math.isnan(value):
                                metric_values[key].append(value)
                        except (TypeError, ValueError):
                            pass  # non-convertible to float → skip

        # 3. 평균 계산
        avg_result = {
            key: round(sum(values) / len(values), 4) if values else float('nan')
            for key, values in metric_values.items()
        }

        return avg_result

    def run(self):
        try:
            self.EvaluationDataset_total_sets_cnt_signal.emit(len(self.eval_sets))
            self.thread_run = True

            for cnt, eval_set in enumerate(self.eval_sets):
                if not self.thread_run:
                    break

                test_s = [eval_set]
                evaluation_dataset = EvaluationDataset.from_list(test_s)

                self.EvaluationDataset_update_list_widget_signal.emit(cnt)

                scores = []
                print(f"Question: {test_s[0]['user_input']}")

                for i in range(self.max_iter):
                    self.EvaluationDataset_text_update_signal.emit(
                        f"Mean Cal: {i + 1}/{self.max_iter}: Processing...\nQuestion: {test_s[0]['user_input']}")

                    result = evaluate(dataset=evaluation_dataset,
                                      metrics=self.metric,
                                      llm=self.evaluator_llm)
                    scores.append(result)
                    print(f"   >> {i+1}th, Score: {result}")

                self.EvaluationDataset_progress_signal.emit(cnt + 1)

                average = self.compute_average(scores)
                print(f"Average Score:  {average}")
                self.eval_sets[cnt]["score"] = average
                self.save_json(file_path=self.ctrl_parm["evaluation_file_path"], data=self.eval_sets)
                print("=======================================================================================")

            self.EvaluationDataset_finished_thread_signal.emit()

        except Exception as e:
            handle_exception()

    def stop(self):
        # log_info("info", "Thread 종료")
        self.thread_run = False
        self.quit()
        if not self.wait(3000):  # 3초 기다려도 종료되지 않으면 강제 종료
            self.terminate()
