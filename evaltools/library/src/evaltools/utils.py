from .chatbot_evaluator import ChatbotEvaluator
from .testset_generator import TestGenerator
from .lambda_manager import LambdaManager 

from langchain.docstore.document import Document

from ragas.metrics import (
    faithfulness, 
    answer_relevancy, 
    context_precision, 
    context_recall, 
    context_entity_recall,
    answer_similarity, 
    answer_correctness
)

DEFAULT_RAGAS_METRIC = [faithfulness, answer_correctness]

def generate_testset(
        body, 
        n = 20, 
        ):
    documents = [Document(page_content=b["Content"], metadata={"Section":b["Section"]}) for b in body]
    
    test_generator = TestGenerator()
    testset = test_generator.generate(documents=documents, n=n)
    
    data = [{
        "question": row["question"],
        "contexts": row["contexts"],
        "ground_truth": row["ground_truth"],
        "evolution_type": row["evolution_type"],
        "metadata": row["metadata"],
    } for _, row in testset.iterrows()]
    
    return data


def generate_evalset(
        testset, 
        ):
    lambda_manager = LambdaManager()
    evalset = []
    for test in testset:
        context, response = lambda_manager.invoke_chat(test["question"])
        test.update({"contexts":context, "answer":response})
        
        evalset.append(test)
        
    return evalset
    

def evaluate(
        evalset,
        metric = DEFAULT_RAGAS_METRIC
        ):
    chatbot_eval = ChatbotEvaluator()
    chatbot_eval.load_data(evalset)
    chatbot_eval.evaluate_all(metric = metric)
    return [r.to_dict() for r in chatbot_eval.records]
