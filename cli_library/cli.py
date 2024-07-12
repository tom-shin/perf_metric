import json
import os
import argparse
from tqdm import tqdm


from datasets import Dataset
from sentence_transformers import SentenceTransformer, util

from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, answer_similarity, answer_correctness
from ragas import evaluate

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings


class Record:
    def __init__(self, data):
        self.question = data["question"]
        self.contexts = data["contexts"]
        self.control_answer = data["ground_truth"]
        self.test_answer = data["answer"]
        self.score = {}

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

    def run_ragas(self, record):
        llm_llama3 = ChatOllama(model="llama3:latest", temperature=0)
        ollama_emb = OllamaEmbeddings(model="llama3:latest")

        #print(record.contexts)
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

        return evaluate(dataset = dataset, llm = llm_llama3, embeddings=ollama_emb, metrics=metric)
        

    def evaluate_all(self, model_dir, tests):
        for test in tests:
            if test == "Ragas":
                print("Evaluation with Ragas")
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

def is_different(value1, value2):
    return abs(value1 - value2) > 0.0001

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Chatbot')
    parser.add_argument('tests', metavar='TEST_NAME', nargs='+', help='a test to run')
    parser.add_argument('-m', '--model_dir', required=True, help='the location of test models')
    parser.add_argument('-d', '--data_dir', required=True, help='the location of test data')
    args = parser.parse_args()

    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(args.data_dir)

    chatbot_eval.evaluate_all(args.model_dir, args.tests)
    
    chatbot_eval.print_scores()

