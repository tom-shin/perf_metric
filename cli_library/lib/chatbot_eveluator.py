from datetime import datetime
import os   
from tqdm import tqdm

from datasets import Dataset
from sentence_transformers import SentenceTransformer, util

# Ragas
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

# Langchain Ollama
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
# Langchain OpenAI
from langchain_openai.chat_models import ChatOpenAI


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
            llm_model = None, 
            embedding_model = None,
            temperature = 0
        ):
        if "OpenAI" in llm_model:
            self.ragas_llm = ChatOpenAI(model=llm_model.split(":")[-1])
        else:
            self.ragas_llm = ChatOllama(model=llm_model, temperature=temperature)
        self.ragas_embedding = OllamaEmbeddings(model = embedding_model) if embedding_model != None else None


    def run_ragas(self, record, metric, in_ci):
        data = {
            'question': [record.question],
            'contexts': [record.contexts[0]],
            'answer': [record.test_answer],
            'ground_truth': [record.control_answer]
        }
        dataset = Dataset.from_dict(data)

        return evaluate(
            dataset = dataset, 
            llm = self.ragas_llm, 
            embeddings = self.ragas_embedding, 
            metrics=metric,
            in_ci = in_ci,
            raise_exceptions=False
        )
        

    def evaluate_all(self, 
                     model_dir, 
                     tests,
                    #  metric = [faithfulness, context_relevancy, answer_correctness],
                     metric = [faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, context_relevancy, answer_similarity, answer_correctness],
                     in_ci = False
                     ):
        for test in tests:
            if test == "Ragas":
                print("Evaluation with Ragas")
                for record in self.records:
                    record.score.update(self.run_ragas(record, metric, in_ci))
                continue

            print(f"Evaluating with model: {test}")
            model_file = os.path.join(model_dir, test)
            model = SentenceTransformer(model_file)

            for record in tqdm(self.records): 
                record.score[test] = self.cal_score(model, record).item()
                


    def print_scores(self):
        for record in self.records:
            print(record.score)


    def export_data(self, export_path = f"./test/result-{datetime.today().strftime('%Y-%m-%d')}.json"):
        export_data = list(map(lambda x: x.to_dict(), self.records))
        DataLoader.dump_json(export_data, export_path)