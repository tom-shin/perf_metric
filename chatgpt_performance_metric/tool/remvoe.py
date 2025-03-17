import json

# 예시 JSON 데이터 불러오기
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)  # data는 list[dict] 형태

# 중복 제거 처리
seen_inputs = set()
unique_data = []

for item in data:
    user_input = item.get("user_input")
    if user_input not in seen_inputs:
        unique_data.append(item)
        seen_inputs.add(user_input)
    else:
        print(f"중복 제거됨: {user_input}")

# 결과 확인 및 저장 (옵션)
with open("cleaned_data.json", "w", encoding="utf-8") as f:
    json.dump(unique_data, f, ensure_ascii=False, indent=2)
