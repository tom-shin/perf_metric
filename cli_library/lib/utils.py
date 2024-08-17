
import os
from datetime import datetime
from tqdm import tqdm

from lib.chatbot_eveluator import ChatbotEvaluator
from lib.testset_generator import TestGenerator
from lib.data_loader import DataLoader
from lib.lambda_manager import LambdaManager
from lib.s3_manager import S3Manager



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

DEFAULT_TESTSET_DIR = f"./test/testset_{datetime.today().strftime('%Y%m%d')}.json"
DEFAULT_EVALSET_DIR = f"./test/evalset_{datetime.today().strftime('%Y%m%d')}.json"
DEFAULT_RESULT_DIR = f"./test/result_{datetime.today().strftime('%Y%m%d')}.json"

DEFAULT_RAGAS_METRIC = [faithfulness, context_relevancy, answer_correctness]


def generate_testset(
        source_dir, 
        n = 20, 
        testset_dir = DEFAULT_TESTSET_DIR
        ):
    context = DataLoader.load_document(source_dir)
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


def generate_evalset(
        testset_dir, 
        evalset_dir = DEFAULT_EVALSET_DIR
        ):
    lambda_manager = LambdaManager()
    testset = DataLoader.load_json(testset_dir)
    evalset = []
    for test in tqdm(testset, desc="Generating Evalset"):
        context, response = lambda_manager.invoke_chat(test["question"])
        test.update({"contexts":context, "answer":response})
        
        evalset.append(test)
        
    DataLoader.dump_json(evalset, evalset_dir)
    return evalset_dir
    

def evaluate(
        evalset_dir, 
        result_dir = DEFAULT_RESULT_DIR
        ):
    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(evalset_dir)
    chatbot_eval.evaluate_all(None, ["Ragas"], DEFAULT_RAGAS_METRIC)
    chatbot_eval.export_data(result_dir)


def insert_chunk(source_dir, bucket):
    s3_manager = S3Manager()
    lambda_manager = LambdaManager()
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if ".md" in file:
                s3_manager.upload(
                    os.path.join(root, file),
                    bucket,
                    file
                    )
                
                chunks = lambda_manager.invoke_chunk(bucket, file)
                status = lambda_manager.invoke_embed(chunks)
                print(f"Insert file({file}): {status}")
                s3_manager.delete(bucket, file)