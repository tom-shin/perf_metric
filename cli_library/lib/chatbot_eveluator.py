
import os   
from tqdm import tqdm

from datasets import Dataset
from sentence_transformers import SentenceTransformer, util

from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_precision, 
    context_recall, 
    context_entity_recall,
    context_relevancy, 
    answer_similarity, 
    answer_correctness
)
from ragas import evaluate

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

from lib.data_loader import DataLoader


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
        pass

    def load_data(self, data_path):
        data = DataLoader.load_json(data_path)
        self.records = list(map(lambda x: Record(x), data))
    
    def cal_score(self, model, record):
        control_embedding = model.encode(record.control_answer, convert_to_tensor=True)
        test_embedding = model.encode(record.test_answer, convert_to_tensor=True)
        
        cosine_score = util.pytorch_cos_sim(control_embedding, test_embedding)

        return cosine_score

    def set_ragas(
            self, 
            llm_model = "llama2-uncensored:latest", 
            embedding_model = "mxbai-embed-large:latest",
            temperature = 0
        ):
        self.ragas_llm = ChatOllama(model = llm_model, temperature = temperature)
        self.ragas_embedding = OllamaEmbeddings(model = embedding_model)


    def run_ragas(self, record):
        data = {
            'question': [record.question],
            'contexts': [record.contexts[0]],
            'answer': [record.test_answer],
            'ground_truth': [record.control_answer]
        }
        dataset = Dataset.from_dict(data)

        #metric = [faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, answer_similarity, answer_correctness]
        metric = [faithfulness, context_relevancy, answer_correctness]
        #metric = [answer_correctness]
        # metric = [faithfulness]

        return evaluate(
            dataset = dataset, 
            # llm = self.ragas_llm, 
            # embeddings = self.ragas_embedding, 
            metrics=metric,
            in_ci = True,
            raise_exceptions=False
        )
        

    def evaluate_all(self, model_dir, tests):
        for test in tests:
            if test == "Ragas":
                print("Evaluation with Ragas")
                for record in self.records:
                    record.score.update(self.run_ragas(record))
                continue

            print(f"Evaluating with model: {test}")
            model_file = os.path.join(model_dir, test)
            model = SentenceTransformer(model_file)

            for record in tqdm(self.records): 
                record.score[test] = self.cal_score(model, record).item()
                


    def print_scores(self):
        for record in self.records:
            print(record.score)


    def export_data(self, export_path = "./test/result.json"):
        export_data = list(map(lambda x: x.to_dict(), self.records))
        DataLoader.dump_json(export_data, export_path)
