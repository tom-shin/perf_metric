from .generator import GENERATOR_LOG, log, call
from .generator.ChatData import ChatData
from .generator.moderator import mod_check
from .generator.cache import cache_check
from .generator.retrieval import generate_components
from .generator.generate import generate_answer
from .generator.postgen import generate_features
from .database import cache_add, log_add, new_log_id


@log("CacheAdd")
@call("DocDB_cache_add")
def new_cache(result: dict):
    cache_add(result)


@call("DocDB_log_check")
def new_id():
    return new_log_id()


def get_log_print() -> bool:
    return not GENERATOR_LOG.silent


def toggle_log_print() -> bool:
    GENERATOR_LOG.silent = not GENERATOR_LOG.silent
    return not GENERATOR_LOG.silent


def simple_answer(query: str, history: list[dict] = []) -> dict:
    return post_generation(answer_question(query, history))


def answer_question(
    query: str, history: list[dict] = [], stream: bool = False
) -> ChatData:
    GENERATOR_LOG.begin()
    data = ChatData(query, history)
    data.set_mod(mod_check(query))
    if data.dna:
        return data
    cache_check(data)
    generate_components(data)
    generate_answer(data, stream)
    return data


def post_generation(data: ChatData) -> dict:
    if data.dna:
        result = data.export()
    else:
        GENERATOR_LOG.log("Response")
        generate_features(data)
        result = data.export()
        result.update({"_id": new_id()})
        if not data.cache_similar:
            new_cache(result)
    result.update({"ExecTime": GENERATOR_LOG.summary()})
    for attr in ["embedding"]:
        if result.get(attr):
            result.pop(attr)
    if result.get("cache"):
        result["cache"] = {
            k: result["cache"][k]
            for k in ["_id", "success", "query", "history", "asked", "conversation"]
        }
    GENERATOR_LOG.quiet_log(result)
    log_add(result)
    return result
