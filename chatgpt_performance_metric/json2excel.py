import os
import json
import pandas as pd
import chardet

dir_path = r"C:\Work\tom\python_project\Testset_Generation_Evaluation\perf_metric\chatgpt_performance_metric"
filename = r"3.json"


# 인코딩 감지 함수
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
        return result['encoding']


json_path = os.path.join(dir_path, filename)

# 인코딩 감지
encoding = detect_encoding(json_path)
print(f"감지된 인코딩: {encoding}")

# 감지된 인코딩으로 JSON 파일 읽기
with open(json_path, 'r', encoding=encoding) as json_file:
    datas = json.load(json_file)

# 데이터를 리스트로 변환
data_list = []
for data in datas:
    user_input = data["user_input"]
    # context는 여러 줄일 수 있으므로 하나의 문자열로 연결하여 작성
    retrieved_contexts = "; ".join(data["retrieved_contexts"])
    reference = data["reference"]
    response = data["response"]
    faithfulness = data["score"].get("faithfulness", "")
    context_recall = data["score"].get("context_recall", "")
    factual_correctness = data["score"].get("factual_correctness", "")
    semantic_similarity = data["score"].get("semantic_similarity", "")

    # 리스트에 데이터를 추가
    data_list.append({
        "user_input": user_input,
        "retrieved_contexts": retrieved_contexts,
        "response": response,
        "reference": reference,
        "Ragas(open-ai): Faithfulness": faithfulness,
        "Ragas(open-ai): LLMContextRecall": context_recall,
        "Ragas(open-ai): FactualCorrectness": factual_correctness,
        "Ragas(open-ai): SemanticSimilarity": semantic_similarity
    })

# DataFrame으로 변환
df = pd.DataFrame(data_list)

# 엑셀 파일로 저장
excel_file = json_path.replace("json", "xlsx")
df.to_excel(excel_file, index=False, engine='openpyxl')
print(f"엑셀 파일이 생성되었습니다: {excel_file}")
