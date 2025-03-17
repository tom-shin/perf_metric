# import json
#
# # 예시 JSON 데이터 불러오기
# with open("data.json", "r", encoding="utf-8") as f:
#     data = json.load(f)  # data는 list[dict] 형태
#
# # 중복 제거 처리
# seen_inputs = set()
# unique_data = []
#
# for item in data:
#     user_input = item.get("user_input")
#     if user_input not in seen_inputs:
#         unique_data.append(item)
#         seen_inputs.add(user_input)
#     else:
#         print(f"중복 제거됨: {user_input}")
#
# # 결과 확인 및 저장 (옵션)
# with open("cleaned_data.json", "w", encoding="utf-8") as f:
#     json.dump(unique_data, f, ensure_ascii=False, indent=2)


import pandas as pd
import json

# 엑셀 파일 읽기
df = pd.read_excel(rf"C:\Users\User\Downloads\testset.xlsx")  # 엑셀 파일 경로를 지정하세요


# 컬럼 이름 확인 후 필요한 컬럼만 사용 (대소문자 구분 유의)
df = df[['Question', 'Response', 'file']]

# 컬럼 이름을 변경 (JSON 키에 맞게)
df.rename(columns={'Question': 'user_input', 'Response': 'response', 'file': 'file'}, inplace=True)

df['reference_contexts'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['synthesizer_name'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['retrieved_contexts'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['chatbot_response'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['date_time'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['chatbot_server'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능
df['reference'] = ""  # 빈 문자열로 설정. 원하는 값으로 변경 가능


# DataFrame을 JSON 리스트로 변환
json_list = df.to_dict(orient='records')

# JSON 출력 (예: 파일로 저장하거나 프린트)
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(json_list, f, ensure_ascii=False, indent=2)

# 또는 화면에 출력
print(json.dumps(json_list, ensure_ascii=False, indent=2))
