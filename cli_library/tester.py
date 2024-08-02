from datetime import datetime

from lib.chatbot_eveluator import ChatbotEvaluator
from lib.testset_generator import TestGenerator
from lib.data_loader import DataLoader
from lib.lambda_generator import LambdaGenerator


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
    generator = LambdaGenerator()
    return generator.generate_evalset(testset_dir, evalset_dir)


    

def evaluate(data_dir):
    models = [
    # "tinyllama:latest",
    # "phi3:3.8b",
    # "llama2:latest",
    # "llama3:latest",
    # "gemma2:latest",
    # "llama3.1:latest",
    "OpenAI:gpt-4o-mini",
    ]

    for m in models:
        chatbot_eval = ChatbotEvaluator()
        chatbot_eval.load_data(data_dir)

        chatbot_eval.set_ragas(
            llm_model = m if m != "OpenAI" else None,
            # embedding_model = "mxbai-embed-large:latest",
            temperature = 0
        )
        chatbot_eval.evaluate_all(None, ["Ragas"], [faithfulness, context_relevancy, answer_correctness])
        chatbot_eval.export_data(f"./test/result_{m}_{datetime.today().strftime('%Y%m%d')}.json")


evalset_dir = generate_evalset("./test/testset_general.json")
evaluate(evalset_dir)