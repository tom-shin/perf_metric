import os
from sentence_transformers import SentenceTransformer, util
from ragas import evaluate

from datasets import Dataset
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall, context_entity_recall, \
    answer_similarity, answer_correctness

"""아래 Models에서 평가하고자 하는 모델만 enable 그리로 main.py 실행"""

Models = {
    "all-MiniLM-L6-v2": None,
    "all-mpnet-base-v2": None,
    "paraphrase-MiniLM-L6-v2": None,
    "distiluse-base-multilingual-cased-v2": None,
    "paraphrase-mpnet-base-v2": None,
    "all-distilroberta-v1": None,
    "Ragas(open-ai): Faithfulness": None,
    "Ragas(open-ai): Answer Relevancy": None,
    "Ragas(open-ai): Context Precision": None,
    "Ragas(open-ai): Context Recall": None,
    "Ragas(open-ai): Context Entity Recall": None,
    "Ragas(open-ai): Answer Similarity": None,
    "Ragas(open-ai): Answer Correctness": None
}

""" 아래 부터는 수정 하지 말 것 """

Rag_Models_Metric = {
    "Ragas(open-ai): Faithfulness": faithfulness,
    "Ragas(open-ai): Answer Relevancy": answer_relevancy,
    "Ragas(open-ai): Context Precision": context_precision,
    "Ragas(open-ai): Context Recall": context_recall,
    "Ragas(open-ai): Context Entity Recall": context_entity_recall,
    "Ragas(open-ai): Answer Similarity": answer_similarity,
    "Ragas(open-ai): Answer Correctness": answer_correctness
}

# method for metric definition
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def common_llm_model(model, scenario_data):
    local_model_dir = os.path.join(parent_directory, "local_models", model)
    c_model = SentenceTransformer(local_model_dir)
    # 문장 임베딩 생성
    embedding1 = c_model.encode(scenario_data["answer"], convert_to_tensor=True)
    embedding2 = c_model.encode(scenario_data["ground_truth"], convert_to_tensor=True)

    # 코사인 유사도 계산
    cosine_score = util.pytorch_cos_sim(embedding1, embedding2)

    return str(round(cosine_score.item(), 5))


def common_ragas_metric_model(model, scenario_data):
    data_samples = {
        'question': [scenario_data["question"]],
        'contexts': [[scenario_data["contexts"]]],
        'answer': [scenario_data["answer"]],
        'ground_truth': [scenario_data["ground_truth"]]
    }

    dataset = Dataset.from_dict(data_samples)
    score = evaluate(dataset, metrics=[Rag_Models_Metric[model]])
    score = str(round(score[str(Rag_Models_Metric[model].name)], 5))

    return score
