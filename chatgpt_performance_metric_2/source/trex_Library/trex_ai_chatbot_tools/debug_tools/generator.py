from tqdm import tqdm
from .. import relevancy_score
from ..database import vector_search
from ..embedding import get_embedding
from ..text_gen import simple_answer, get_log_print, toggle_log_print


def bulk_generate(questions: list[dict]) -> list[dict]:
    revert = get_log_print()
    if revert:
        toggle_log_print()
    for q in tqdm(questions, desc="Generating debug data"):
        qe = get_embedding(q["query"])
        score = relevancy_score(qe, vector_search(qe, 1).iloc[0]["embedding"])
        q["cosineScore"] = score
        answer = simple_answer(q["query"], q.get("history", []))
        q["answer"] = answer.get("response")
        q["links"] = answer.get("link_scores")
        q["image"] = answer.get("image")
    if revert:
        toggle_log_print()
    return questions
