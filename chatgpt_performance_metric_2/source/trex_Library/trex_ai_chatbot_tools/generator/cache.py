from . import MIN_CONV, MAX_CONV, CACHE_SIM, log, call
from .ChatData import ChatData
from .. import relevancy_score
from ..database import cache_search
from ..embedding import get_embedding


@call("OpenAI_embed")
def embed(input: str) -> list[float]:
    e = get_embedding(input)
    return e


@call("DocDB_cache_check")
def search(e: list[float]) -> dict:
    return cache_search(e)


@log("Retrieval")
def cache_check(data: ChatData):
    def build_conv(add_list: list, conv: str = ""):
        return "\n\n".join(
            [f"{el['role']}: {el['content']}" for el in add_list] + [conv]
        )

    def cache_pass(score: float) -> bool:
        return score < CACHE_SIM

    if not data.history:
        qe = embed(data.query)
        score, cache = get_cache_score(qe)
        data.set_cache(cache, score, f"user: {data.query}", qe)
        return
    conv = build_conv(data.history[-MIN_CONV:], f"user: {data.query}")
    qe = embed(conv)
    score, cache = get_cache_score(qe)
    for i in range(MIN_CONV, MAX_CONV, 2):
        if not data.history[-i - 2 : -i]:
            break
        conv = build_conv(data.history[-i - 2 : -i], conv)
        qe = embed(conv)
        score, cache = get_cache_score(qe)
        if cache_pass(score):
            break
    data.set_cache(cache, score, conv, qe)
    return


def get_cache_score(qe: list[float]) -> tuple[float, dict]:
    cache_result = search(qe)
    if not cache_result:
        return 2, cache_result
    cosine_score = relevancy_score(qe, cache_result["embedding"])
    return cosine_score, cache_result
