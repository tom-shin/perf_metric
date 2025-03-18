import json
from collections import OrderedDict

f = rf"C:\Work\tom\python_project\Testset_Generation_Evaluation\perf_metric\chatgpt_performance_metric\TestSet_Result.json"
encoding = "utf-8"

# 파일 열기 및 데이터 읽기
with open(f, "r", encoding=encoding) as file:
    json_data = json.load(file, object_pairs_hook=OrderedDict)

# 데이터 수정
for data in json_data:
    data["user_comment"] = ""  # 'user_comment' 추가
    data["user"] = ""  # 'user' 추가

# 수정된 데이터를 다시 파일에 저장
with open(f, 'w', encoding='utf-8') as file:
    json.dump(json_data, file, ensure_ascii=False, indent=2)
