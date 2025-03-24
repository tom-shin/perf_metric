from . import MIN_CONV, CACHE_SIM
from .ChatData import ChatData
from .. import relevancy_score
from ..database import cache_search
from ..embedding import get_embedding


def get_cache_score(qe: list[float]) -> tuple[float, dict]:
    cache_result = cache_search(qe)
    if not cache_result:
        return 2, cache_result
    cosine_score = relevancy_score(qe, cache_result["embedding"])
    return cosine_score, cache_result


def get_cache(data: ChatData):
    def build_conv(add_list: list, conv: str = ""):
        return "\n\n".join(
            [f"{el['role']}: {el['content']}" for el in add_list] + [conv]
        )

    def cache_pass(score: float) -> bool:
        return score < CACHE_SIM

    conv = build_conv(data.history[-MIN_CONV:], f"user: {data.query}")
    i = len(data.history) - MIN_CONV - 2
    ce = get_embedding(conv)
    score, cache = get_cache_score(ce)
    while i >= 0 and not cache_pass(score):
        conv = build_conv(data.history[i : i + 2], conv)
        ce = get_embedding(conv)
        score, cache = get_cache_score(ce)
        i -= 2
    data.set_cache(cache, score, conv, ce)
    return
