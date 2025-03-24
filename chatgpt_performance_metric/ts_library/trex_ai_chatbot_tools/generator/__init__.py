import re
from numpy import dot
from numpy.linalg import norm
from pandas import DataFrame
from .. import CONFIG, LAMBDA_ENV
from ..database import vector_search
from ..inspector import Log

gen_log = Log(
    [
        "Moderation",
        "Retrieval",
        "Generation",
        "APICall",
        "Response",
        "PostGen",
        "CacheAdd",
    ]
)

DIM: int = CONFIG["EMBED"]["DIM"]
INPUT_TOKEN: int = CONFIG["TEXTGEN"]["INPUT_TOKENS"]
CONTEXT_TOKEN: int = CONFIG["TEXTGEN"]["CONTEXT_TOKENS"]
OUTPUT_TOKEN: int = CONFIG["TEXTGEN"]["OUTPUT_TOKENS"]
CHUNK_LIMIT: int = CONFIG["TEXTGEN"]["CONTEXT_CHUNK_LIMIT"]
GEN_TEMP: int = CONFIG["TEXTGEN"]["TEMPERATURE"]
LINK_COUNT: int = CONFIG["TEXTGEN"]["HYPERLINK_COUNT"]
MIN_CONV: int = CONFIG["TEXTGEN"]["MIN_CONVERSATION"] * 2
CACHE_SIM: float = CONFIG["TEXTGEN"]["CACHE_SIMILAR"]
CACHE_EQ: float = CONFIG["TEXTGEN"]["CACHE_EQUAL"]
LINK_FILTER: float = CONFIG["METADATA"]["LINK"]
IMAGE_FILTER: float = CONFIG["METADATA"]["IMAGE"]

if LAMBDA_ENV:
    import trex_ai_chatbot_tools.lambda_env.text_gen as tg_env
else:
    import trex_ai_chatbot_tools.local_env.text_gen as tg_env

GPT_INSTRUCTIONS = tg_env.GPT_INSTRUCTIONS
SPLIT_STRING = re.compile("\s*\S+")


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return 1 - dot(e1, e2) / (norm(e1) * norm(e2))


def get_relevant_embeddings(
    qe: list[float], number: int = CHUNK_LIMIT * 2
) -> DataFrame:
    result = vector_search(qe, number)
    result["CosineDist"] = result["Embedding"].apply(lambda x: relevancy_score(x, qe))
    return result
