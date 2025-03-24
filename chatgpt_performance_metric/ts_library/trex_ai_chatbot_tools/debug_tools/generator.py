from tqdm import tqdm
from .. import relevancy_score
from ..embedding import get_embedding
from ..database import vector_search
from ..text_gen import simple_answer


def bulk_generate(questions: list[dict]) -> list[dict]:
    for q in tqdm(questions, desc="Generating debug data"):
        qe = get_embedding(q["Query"])
        score = relevancy_score(qe, vector_search(qe, 1).iloc[0]["Embedding"])
        q["CosineScore"] = score
        answer = simple_answer(q["Query"], q.get("History", []))
        q["Answer"] = answer.get("response")
        q["Links"] = answer.get("link_scores")
        q["Image"] = answer.get("image")
    return questions
