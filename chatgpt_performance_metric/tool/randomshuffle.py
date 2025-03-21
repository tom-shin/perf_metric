import json
import random

for i in range(20):
    # JSON 파일 읽기
    path_ = rf"C:\Users\ADMIN\Documents\tom\perf_metric\chatgpt_performance_metric\shuffled_file.json"
    path = path_.replace("\\", "/")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)  # data는 list[dict] 형태

    # 리스트 섞기
    random.shuffle(data)

    # 섞인 결과 확인
    for cnt, item in enumerate(data):
        print(cnt, item)

    # (선택) 다시 파일로 저장하고 싶다면:
    with open(rf'shuffled_file_{i}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
