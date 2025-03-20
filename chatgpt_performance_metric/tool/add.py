import json
from collections import OrderedDict

f = rf"C:\Users\ADMIN\Documents\tom\perf_metric\chatgpt_performance_metric\Evaluation_Release_Result\20241018\ragas_evaluation_result_241018.json"
encoding = "utf-8"

# 파일 열기 및 데이터 읽기
with open(f, "r", encoding=encoding) as file:
    json_data = json.load(file, object_pairs_hook=OrderedDict)

new_data = {
    "user_input": "",
    "response": "",
    "file": "",
    "reference_contexts": "",
    "synthesizer_name": "",
    "retrieved_contexts": "",
    "chatbot_response": "",
    "date_time": "",
    "chatbot_server": "",
    "reference": "",
    "user_comment": "",
    "user": ""
  }

# 데이터 수정
new_tc = []
for data in json_data:
    new_data["user_input"] = data["question"]

    new_tc.append(new_data)

# 수정된 데이터를 다시 파일에 저장
f = rf"C:\Users\ADMIN\Documents\tom\perf_metric\chatgpt_performance_metric\Evaluation_Release_Result\20241018\old_ragas_evaluation_result_241018.json"
with open(f, 'w', encoding='utf-8') as file:
    json.dump(new_tc, file, ensure_ascii=False, indent=2)
