import json
import os
from tqdm import tqdm


from sentence_transformers import SentenceTransformer, util

from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, answer_similarity, answer_correctness
from ragas import evaluate

MODEL_DIR = ""
TEST_FILE_DIR = ""

class Record:
    def __init__(self, data):
        self.question = data["question"]
        self.contexts = data["contexts"]
        self.control_answer = data["ground_truth"]
        self.test_answer = data["answer"]
        self.score = {}

class ChatbotEvaluator:
    
    test_case = ["all-distilroberta-v1", "all-MiniLM-L6-v2", "all-mpnet-base-v2", "distiluse-base-multilingual-cased-v2", "paraphrase-MiniLM-L6-v2", "paraphrase-mpnet-base-v2"]
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

    def evaluate_all(self):
        for test in self.test_case:
            model_dir = os.path.join(MODEL_DIR, test)
            model = SentenceTransformer(model_dir)

            print(f"Evaluating with model: {test}")
            for record in tqdm(self.records): 
                record.score[test] = self.cal_score(model, record).item()
                


    def print_scores(self):
        for record in self.records:
            print(record.score)


if __name__ == "__main__":
    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(TEST_FILE_DIR)

    chatbot_eval.evaluate_all()
    chatbot_eval.print_scores()
#    for data in test_data:
#        print(data)
        

