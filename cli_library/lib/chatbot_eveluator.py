import json
from tqdm import tqdm

from datasets import Dataset
from sentence_transformers import SentenceTransformer, util

from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_precision, 
    context_recall, 
    context_entity_recall, 
    answer_similarity, 
    answer_correctness
)
from ragas import evaluate

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

class ChatbotEvaluator:
    def __init__(self):
        pass

    def parse_data(self, data):
        return Record(data)

    def load_data(self, data_path):
        with open(data_path, 'r') as file:
            data = json.load(file)
        self.records = list(map(self.parse_data, data))
    
    def cal_score(self, model, record):
        control_embedding = model.encode(record.control_answer, convert_to_tensor=True)
        test_embedding = model.encode(record.test_answer, convert_to_tensor=True)
        
        cosine_score = util.pytorch_cos_sim(control_embedding, test_embedding)

        return cosine_score

    def set_ragas(self):
        self.ragas_llm = ChatOllama(model="llama3:latest", temperature=0)
        self.ragas_embedding = OllamaEmbeddings(model="llama3:latest")


    def run_ragas(self, record):
        data = {
            'question': [record.question],
            'contexts': [record.contexts[0]],
            'answer': [record.test_answer],
            'ground_truth': [record.control_answer]
        }
        dataset = Dataset.from_dict(data)

        #metric = [faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, answer_similarity, answer_correctness]
        #metric = [faithfulness, answer_correctness]
        metric = [answer_correctness]

        return evaluate(
            dataset = dataset, 
            llm = self.ragas_llm, 
            embeddings = self.ragas_embedding, 
            metrics=metric
        )
        

    def evaluate_all(self, model_dir, tests):
        for test in tests:
            if test == "Ragas":
                print("Evaluation with Ragas")
                self.set_ragas()
                for record in tqdm(self.records):
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
