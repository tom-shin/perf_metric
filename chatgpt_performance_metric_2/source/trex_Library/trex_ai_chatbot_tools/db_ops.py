from pymongo import MongoClient
from pandas import DataFrame
from . import CONNECTION_STRING, CONFIG

mongo_client = MongoClient(CONNECTION_STRING)
vector_col = mongo_client[CONFIG["LAMBDA"]["DB_ID"]][CONFIG["LAMBDA"]["VDB_ID"]]
cache_col = mongo_client[CONFIG["LAMBDA"]["DB_ID"]][CONFIG["LAMBDA"]["CACHE_ID"]]


def vector_search(qe: list[float], number: int) -> DataFrame:
    return DataFrame(
        list(
            vector_col.aggregate(
                [
                    {
                        "$search": {
                            "vectorSearch": {
                                "vector": qe,
                                "path": "Embedding",
                                "k": number,
                                "similarity": "cosine",
                            }
                        }
                    }
                ]
            )
        )
    )


def cache_search(qe: list[float]) -> dict:
    result = list(
        cache_col.aggregate(
            [
                {
                    "$search": {
                        "vectorSearch": {
                            "vector": qe,
                            "path": "embedding",
                            "k": 1,
                            "similarity": "cosine",
                        }
                    }
                }
            ]
        )
    )
    if result:
        return result[0]
    return {}
