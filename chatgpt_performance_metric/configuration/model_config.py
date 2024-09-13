import os
import numpy as np
import math

from sentence_transformers import SentenceTransformer, util
from ragas import evaluate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from datasets import Dataset
# from ragas.metrics import faithfulness, context_relevancy, answer_relevancy, context_precision, context_recall, \
#     context_entity_recall, \
#     answer_similarity, answer_correctness

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
"""아래 Models에서 평가하고자 하는 모델만 enable 그리로 main.py 실행"""

Models = {
    # "all-roberta-large-v1": None,
    # "all-MiniLM-L12-v2": None,
    # "all-MiniLM-L6-v2": None,
    # "all-mpnet-base-v2": None,
    # "paraphrase-MiniLM-L6-v2": None,
    # "distiluse-base-multilingual-cased-v2": None,
    # "paraphrase-mpnet-base-v2": None,
    # "all-distilroberta-v1": None,

    "Ragas(open-ai): Faithfulness": None,
    # "Ragas(open-ai): Answer Relevancy": None,
    # "Ragas(open-ai): Context Precision": None,
    # "Ragas(open-ai): Context Recall": None,
    # "Ragas(open-ai): Context Entity Recall": None,
    "Ragas(open-ai): Context Relevancy": None,
    # "Ragas(open-ai): Answer Similarity": None,
    "Ragas(open-ai): Answer Correctness": None
}

""" 아래 부터는 수정 하지 말 것 """

Rag_Models_Metric = {
    "Ragas(open-ai): Faithfulness": faithfulness,
    "Ragas(open-ai): Answer Relevancy": answer_relevancy,
    "Ragas(open-ai): Context Precision": context_precision,
    "Ragas(open-ai): Context Recall": context_recall,
    "Ragas(open-ai): Context Entity Recall": context_entity_recall,
    "Ragas(open-ai): Context Relevancy": context_relevancy,
    "Ragas(open-ai): Answer Similarity": answer_similarity,
    "Ragas(open-ai): Answer Correctness": answer_correctness
}

# method for metric definition
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cal_iqr_mean_score(cal_data):
    if len(cal_data) == 0:   # 모두 non이라는 것임.
        return 0, 0, 0

    # 평균 계산
    mean_score = np.mean(cal_data)

    data = np.array(cal_data)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    # boundary for remove-outlier
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]

    # 대표값 계산
    mean_filtered = np.mean(filtered_data)
    median_filtered = np.median(filtered_data)

    return float(mean_score), float(median_filtered), float(mean_filtered)


def common_llm_model(model, scenario_data, max_iter, thread, method="IQR-MEDIAN"):
    local_model_dir = os.path.join(parent_directory, "local_models", model)
    c_model = SentenceTransformer(local_model_dir)
    # 문장 임베딩 생성
    embedding1 = c_model.encode(scenario_data["answer"], convert_to_tensor=True)
    embedding2 = c_model.encode(scenario_data["ground_truth"], convert_to_tensor=True)

    cal_data = []
    print(f"[{model}]")
    for i in range(max_iter):

        if not thread.working:
            print("쓰레드 작업 중지됨")
            break

        cosine_score = util.pytorch_cos_sim(embedding1, embedding2)  # 코사인 유사도 계산
        temp = float(cosine_score.item())
        if isinstance(temp, (int, float)) and not math.isnan(temp):
            cal_data.append(temp)
        print(i + 1, "th: ", temp)

    if not thread.working:
        return float(-999)

    mean_score, iqr_median_score, iqr_mean_score = cal_iqr_mean_score(cal_data=cal_data)
    print(
        f"IQR(Median): {round(iqr_median_score, 3)}\nIQR(Mean): {round(iqr_mean_score, 3)}\nMean: {round(mean_score, 3)}")

    if len(set(cal_data)) != 1:  # 측정된 값이 달라졌음.
        print("><==========================")
    else:
        print("==========================")

    if method == "IQR-MEDIAN":
        # print(method)
        return str(round(iqr_median_score, 5))
    elif method == "IQR-MEAN":
        # print(method)
        return str(round(iqr_mean_score, 5))
    else:
        # print(method)
        return str(round(mean_score, 5))


def common_ragas_metric_model(model, scenario_data, max_iter, thread, method="IQR-MEDIAN"):
    data_samples = {
        'question': [scenario_data["question"]],
        'contexts': [[scenario_data["contexts"]]],
        'answer': [scenario_data["answer"]],
        'ground_truth': [scenario_data["ground_truth"]]
    }

    dataset = Dataset.from_dict(data_samples)

    cal_data = []
    print(f"[{model}]")
    for i in range(max_iter):

        if not thread.working:
            print("쓰레드 작업 중지됨")
            break

        if "gpt-4o-mini" == thread.openai_model:
            # print(thread.openai_model)
            llm = ChatOpenAI(model="gpt-4o-mini")
        else:
            # print(thread.openai_model)
            llm = ChatOpenAI(model="gpt-3.5-turbo-16k")

        # embeddings = OpenAIEmbeddings()
        # score = evaluate(dataset, llm=llm, embeddings=embeddings, metrics=[Rag_Models_Metric[model]])

        score = evaluate(dataset, llm=llm, metrics=[Rag_Models_Metric[model]], raise_exceptions=False)
        temp = float(score[str(Rag_Models_Metric[model].name)])

        if isinstance(temp, (int, float)) and not math.isnan(temp):
            cal_data.append(temp)
        print(i + 1, "th: ", temp)

    if not thread.working:
        return float(-999)

    mean_score, iqr_median_score, iqr_mean_score = cal_iqr_mean_score(cal_data=cal_data)
    print(
        f"IQR(Median): {round(iqr_median_score, 3)}\nIQR(Mean): {round(iqr_mean_score, 3)}\nMean: {round(mean_score, 3)}")

    if len(set(cal_data)) != 1:  # 측정된 값이 달라졌음.
        print("><==========================")
    else:
        print("==========================")

    if method == "IQR-MEDIAN":
        # print(method)
        score = str(round(iqr_median_score, 5))
    elif method == "IQR-MEAN":
        # print(method)
        return str(round(iqr_mean_score, 5))
    else:
        # print(method)
        score = str(round(mean_score, 5))

    return score
