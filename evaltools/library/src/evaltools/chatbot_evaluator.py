from datasets import Dataset

# Ragas
from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_precision, 
    context_recall, 
    context_entity_recall,
    # context_relevancy, 
    answer_similarity, 
    answer_correctness
)
from ragas import evaluate

# Langchain OpenAI
from langchain_openai.chat_models import ChatOpenAI


class Record:
    def __init__(self, data):
        self.question = data["question"]
        self.contexts = data["contexts"]
        self.control_answer = data["ground_truth"]
        self.test_answer = data["answer"]
        self.score = {}

    def to_dict(self):
        return {
            "question": self.question,
            "contexts": self.contexts,
            "ground_truth": self.control_answer,
            "answer": self.test_answer,
            "score": self.score
        }

class ChatbotEvaluator:
    def __init__(self):
        self.set_ragas()
        pass

    def load_data(self, data):
        self.records = list(map(lambda x: Record(x), data))

    def set_ragas(
            self, 
            llm_model = "gpt-4o-mini"
        ):
        self.ragas_llm = ChatOpenAI(model=llm_model)

    def run_ragas(self, record, metric, in_ci):
        data = {
            'question': [record.question],
            'contexts': [record.contexts],
            'answer': [record.test_answer],
            'ground_truth': [record.control_answer]
        }
        dataset = Dataset.from_dict(data)

        return evaluate(
            dataset = dataset, 
            llm = self.ragas_llm, 
            metrics=metric,
            in_ci = in_ci,
            raise_exceptions=False
        )
        

    def evaluate_all(self, 
                     metric = [faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, answer_similarity, answer_correctness],
                     in_ci = False
                     ):
        for record in self.records:
            record.score.update(self.run_ragas(record, metric, in_ci))