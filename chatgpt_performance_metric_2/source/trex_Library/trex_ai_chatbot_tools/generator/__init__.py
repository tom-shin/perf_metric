import os
import re
from functools import wraps
from numpy import dot
from numpy.linalg import norm
from pandas import DataFrame
from .. import CONFIG, tg_model
from ..database import vector_search
from ..inspector import Log

TEXTGEN_MODEL = str(tg_model)
PROMPT_ID: str = os.getenv("PROMPT_ID", "default")
INPUT_TOKEN: int = CONFIG["TEXTGEN"]["INPUT_TOKENS"]
CONTEXT_TOKEN: int = CONFIG["TEXTGEN"]["CONTEXT_TOKENS"]
OUTPUT_TOKEN: int = CONFIG["TEXTGEN"]["OUTPUT_TOKENS"]
CHUNK_LIMIT: int = CONFIG["TEXTGEN"]["CONTEXT_CHUNK_LIMIT"]
GEN_TEMP: int = CONFIG["TEXTGEN"]["TEMPERATURE"]
LINK_COUNT: int = CONFIG["TEXTGEN"]["HYPERLINK_COUNT"]
MIN_CONV: int = CONFIG["TEXTGEN"]["MIN_CONVERSATION"] * 2
MAX_CONV: int = CONFIG["TEXTGEN"]["MAX_CONVERSATION"] * 2
CACHE_SIM: float = CONFIG["TEXTGEN"]["CACHE_SIMILAR"]
CACHE_EQ: float = CONFIG["TEXTGEN"]["CACHE_EQUAL"]
LINK_FILTER: float = CONFIG["METADATA"]["LINK"]
IMAGE_FILTER: float = CONFIG["METADATA"]["IMAGE"]

SPLIT_STRING = re.compile("\s*\S+")

GENERATOR_LOG = Log(
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


def log(step: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            GENERATOR_LOG.log(step)
            return result

        return wrapper

    return decorator


def call(category: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            GENERATOR_LOG.start_watch(category)
            result = func(*args, **kwargs)
            GENERATOR_LOG.stop_watch()
            return result

        return wrapper

    return decorator


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return 1 - dot(e1, e2) / (norm(e1) * norm(e2))


def get_relevant_embeddings(
    qe: list[float], number: int = CHUNK_LIMIT * 2
) -> DataFrame:
    result = vector_search(qe, number)
    result["cosineDist"] = result["embedding"].apply(lambda x: relevancy_score(x, qe))
    return result
