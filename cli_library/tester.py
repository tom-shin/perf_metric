from datetime import datetime
from tqdm import tqdm

from lib.chatbot_eveluator import ChatbotEvaluator
from lib.testset_generator import TestGenerator
from lib.data_loader import DataLoader
from lib.lambda_invoke_manager import LambdaInvokeManager


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


def generate_testset(context, n = 20, testset_dir = f"./test/testset_{datetime.today().strftime('%Y%m%d')}.json"):
    # data = DataLoader.load_document("/workspace/cli_library/test/docs")
    data = DataLoader.load_general("/workspace/cli_library/test/data/")
    test_generator = TestGenerator()
    testset = test_generator.generate(documents=context, n=n)
    
    data = [{
        "question": row["question"],
        "contexts": row["contexts"],
        "ground_truth": row["ground_truth"],
        "evolution_type": row["evolution_type"],
        "metadata": row["metadata"],
    } for _, row in testset.iterrows()]
    
    DataLoader.dump_json(data, testset_dir)
    return testset_dir


def generate_evalset(testset_dir, evalset_dir = f"./test/evalset_{datetime.today().strftime('%Y%m%d')}.json"):
    lambda_manager = LambdaInvokeManager()
    testset = DataLoader.load_json(testset_dir)
    evalset = []
    for test in tqdm(testset, desc="Generating Evalset"):
        context, response = lambda_manager.invoke_chat(test["question"])
        test.update({"contexts":context, "answer":response})
        
        evalset.append(test)
        
    DataLoader.dump_json(evalset, evalset_dir)
    return evalset_dir
    

def evaluate(data_dir):
    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(data_dir)
    chatbot_eval.evaluate_all(None, ["Ragas"], [faithfulness, context_relevancy, answer_correctness])
    chatbot_eval.export_data(f"./test/result_{datetime.today().strftime('%Y%m%d')}.json")


# evalset_dir = generate_evalset("./test/testset_do_not_answer.json")
# evaluate(evalset_dir)