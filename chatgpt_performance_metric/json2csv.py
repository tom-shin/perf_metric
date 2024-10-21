import json
import csv

# JSON 파일을 읽고 데이터 로드
json_path = rf"C:\Work\tom\python_project\Testset_Generation_Evaluation\ragas_evaluation_result_241018.json"
with open(json_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# CSV 파일로 변환
csv_file = 'ragas_evaluation_result_241018.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # 헤더 작성
    headers = ["question", "split_context", "answer", "ground_truth", "Ragas(Open-ai): Faithfulness", "Ragas(Open-ai): Context Relevancy", "Ragas(Open-ai): Answer Correctness"]
    writer.writerow(headers)
    
    # 데이터 작성
    for item in data:
        writer.writerow([
            item['question'],
            "; ".join(item['contexts']),
            item['answer'],
            item['ground_truth'],    
            item['score']['faithfulness'],
            item['score']['context_relevancy'],
            item['score']['answer_correctness']
        ])

print(f"CSV 파일이 생성되었습니다: {csv_file}")
