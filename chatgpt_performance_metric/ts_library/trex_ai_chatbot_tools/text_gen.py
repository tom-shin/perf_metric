from bson import ObjectId
from .generator import gen_log
from .generator.ChatData import ChatData
from .generator.moderator import mod_check
from .generator.retrieval import generate_components
from .generator.generate import generate_response, generate_stream
from .generator.postgen import generate_features
from .database import cache_add, log_add, log_id_found


def simple_answer(query: str, history: list[dict] = []) -> dict:
    return post_generation(answer_question(query, history))


def answer_question(
    query: str, history: list[dict] = [], stream: bool = False
) -> ChatData:
    gen_log.begin()
    data = ChatData(query, history)
    data.set_mod(mod_check(query))
    if data.dna:
        return data
    gen_log.log("Moderation")
    generate_components(data)
    gen_log.log("Generation")
    if stream:
        generate_stream(data)
    else:
        generate_response(data)
    gen_log.log("APICall")
    return data


def post_generation(data: ChatData) -> dict:
    if data.dna:
        result = data.export()
    else:
        gen_log.log("Response")
        generate_features(data)
        gen_log.log("PostGen")
        result = data.export()
        oid = ObjectId()
        while log_id_found(oid):
            oid = ObjectId()
        result.update({"_id": oid})
        if not data.cache_similar:
            cache_add(result)
            gen_log.log("CacheAdd")
    gen_log.summary(result)
    log_add(result)
    return result
