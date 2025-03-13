import os
import numpy as np
import math

from sentence_transformers import SentenceTransformer, util
from ragas import evaluate

# ragas version 0.2.x 이상
from ragas import EvaluationDataset, SingleTurnSample
from ragas.metrics import Faithfulness, LLMContextRecall, FactualCorrectness, SemanticSimilarity
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

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
    "Ragas(open-ai): LLMContextRecall": None,
    "Ragas(open-ai): FactualCorrectness": None,
    "Ragas(open-ai): SemanticSimilarity": None
}

""" 아래 부터는 수정 하지 말 것 """
Rag_Models_Metric = {
    "all-roberta-large-v1": "all-roberta-large-v1",
    "all-MiniLM-L12-v2": "all-MiniLM-L12-v2",
    "all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "all-mpnet-base-v2": "all-mpnet-base-v2",
    "paraphrase-MiniLM-L6-v2": "paraphrase-MiniLM-L6-v2",
    "distiluse-base-multilingual-cased-v2": "distiluse-base-multilingual-cased-v2",
    "paraphrase-mpnet-base-v2": "paraphrase-mpnet-base-v2",
    "all-distilroberta-v1": "all-distilroberta-v1",

    "Ragas(open-ai): Faithfulness": lambda llm: Faithfulness(llm=llm),
    "Ragas(open-ai): LLMContextRecall": lambda llm: LLMContextRecall(llm=llm),
    "Ragas(open-ai): FactualCorrectness": lambda llm: FactualCorrectness(llm=llm),
    "Ragas(open-ai): SemanticSimilarity": lambda embeddings: SemanticSimilarity(embeddings=embeddings)
}

# method for metric definition
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cal_iqr_mean_score(raw_cal_data):
    cal_data = [x for x in raw_cal_data if not math.isnan(x)]

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


def common_llm_model(model, scenario_data, max_iter, thread):
    local_model_dir = os.path.join(parent_directory, "local_models", model)
    c_model = SentenceTransformer(local_model_dir)
    # 문장 임베딩 생성
    embedding1 = c_model.encode(scenario_data["response"], convert_to_tensor=True)
    embedding2 = c_model.encode(scenario_data["reference"], convert_to_tensor=True)

    cal_data = []
    print(f"[{model}]")
    for i in range(max_iter):

        if not thread.working:
            print("쓰레드 작업 중지됨")
            break

        cosine_score = util.pytorch_cos_sim(embedding1, embedding2)  # 코사인 유사도 계산
        temp = float(cosine_score.item())

        cal_data.append(temp)
        print(i + 1, "th: ", temp)

    if not thread.working:
        return float(-999)

    if all(math.isnan(x) for x in cal_data):  # all float(nan)
        return -998

    mean_score, iqr_median_score, iqr_mean_score = cal_iqr_mean_score(raw_cal_data=cal_data)
    print(
        f"IQR(Median): {round(iqr_median_score, 3)}\nIQR(Mean): {round(iqr_mean_score, 3)}\nMean: {round(mean_score, 3)}")

    if len(set(cal_data)) != 1:  # 측정된 값이 달라졌음.
        print("><==========================")
    else:
        print("==========================")

    # print("<", thread.method, ">")

    if thread.method == "IQR-MEDIAN":
        return str(round(iqr_median_score, 5))
    elif thread.method == "IQR-MEAN":
        return str(round(iqr_mean_score, 5))
    else:
        return str(round(mean_score, 5))


def common_ragas_metric_model(model, scenario_data, max_iter, thread):
    sample = SingleTurnSample(
        user_input=scenario_data["user_input"],
        # retrieved_contexts=scenario_data["reference_contexts"],

        response=scenario_data["reference"],
        # reference_contexts=scenario_data["reference_contexts"],
        #
        reference=scenario_data["chatbot_response"]

    )
    #
    # """
    #                 "user_input": widget_ui.question_plainTextEdit.toPlainText(),
    #                 "reference_contexts": widget_ui.contexts_plainTextEdit.toPlainText().split("<context_split>\n")[
    #                                       :-1],
    #                 "reference": widget_ui.answer_plainTextEdit.toPlainText(),
    #                 "trex_reference": widget_ui.truth_plainTextEdit.toPlainText(),
    #                 "chatbot_response": widget_ui.ref_contexts_plainTextEdit.toPlainText()
    #
    # """
    #
    data_samples = [sample]
    eval_dataset = EvaluationDataset(samples=data_samples)

    cal_data = []
    print(f"[{model}]")

    use_legacy = True
    for i in range(max_iter):

        if not thread.working:
            print("쓰레드 작업 중지됨")
            break

        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=thread.openai_model))
        evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

        if "SemanticSimilarity" in model:
            metrics = [
                Rag_Models_Metric[model](embeddings=evaluator_embeddings)
            ]
        else:
            metrics = [
                Rag_Models_Metric[model](llm=evaluator_llm)
            ]

        score = evaluate(dataset=eval_dataset, metrics=metrics)
        extract_score = float(next(iter(score.scores[0].values())))

        cal_data.append(extract_score)
        print(i + 1, "th: ", score)

    if not thread.working:
        return float(-999)

    if all(math.isnan(x) for x in cal_data):  # all float(nan)
        return -998

    mean_score, iqr_median_score, iqr_mean_score = cal_iqr_mean_score(raw_cal_data=cal_data)
    print(
        f"IQR(Median): {round(iqr_median_score, 3)}\nIQR(Mean): {round(iqr_mean_score, 3)}\nMean: {round(mean_score, 3)}")

    if len(set(cal_data)) != 1:  # 측정된 값이 달라졌음.
        print("><==========================")
    else:
        print("==========================")

    # print("<", thread.method, ">")
    if thread.method == "IQR-MEDIAN":
        # print(method)
        score = str(round(iqr_median_score, 5))
    elif thread.method == "IQR-MEAN":
        # print(method)
        return str(round(iqr_mean_score, 5))
    else:
        # print(method)
        score = str(round(mean_score, 5))

    return score
