import shutil
import os
from sentence_transformers import SentenceTransformer

# model_list = [
#     'all-MiniLM-L6-v2',
#     'all-mpnet-base-v2',
#     'paraphrase-MiniLM-L6-v2',
#     'distiluse-base-multilingual-cased-v2',
#     'paraphrase-mpnet-base-v2',
#     'all-distilroberta-v1'
# ]

model_list = []


base = os.getcwd()

for name in model_list:
    model = SentenceTransformer(name)
    local_model_dir = os.path.join(base, rf"{name}")
    model.save(local_model_dir)
    print("Model downloaded and saved locally.")

    # 로컬 디렉토리에서 모델 로드
    model = SentenceTransformer(local_model_dir)

    # 모델 사용 예제
    sentence = "This is a sample sentence."
    embedding = model.encode(sentence)
    print("Model loaded from local directory and used.")
