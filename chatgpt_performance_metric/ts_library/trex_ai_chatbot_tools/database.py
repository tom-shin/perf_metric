from pymongo import MongoClient
from pandas import DataFrame
from . import CONNECTION_STRING, CONFIG, DB_COLS, USER_DB_ID
from bson import ObjectId

mongo_client = MongoClient(CONNECTION_STRING)
VECTOR_DB = CONFIG["DATABASE"]["VECTOR"]["DB_ID"]
VECTOR_ID = CONFIG["DATABASE"]["VECTOR"]["COL_ID"]
CACHE_ID = CONFIG["DATABASE"]["COL_IDS"]["CACHE_ID"]
LOG_ID = CONFIG["DATABASE"]["COL_IDS"]["LOG_ID"]
vector_col = mongo_client[VECTOR_DB][VECTOR_ID]
cache_col = mongo_client[USER_DB_ID][CACHE_ID]
log_col = mongo_client[USER_DB_ID][LOG_ID]
DB_USERTYPES: dict = CONFIG["DATABASE"]["USERS"]

curr_vector = VECTOR_ID
curr_user = USER_DB_ID


def set_db(user_db: str = curr_user, vector_id: str = curr_vector):
    global curr_user, curr_vector
    if user_db == curr_user and vector_id == curr_vector:
        return
    global vector_col, cache_col, log_col
    vector_col = mongo_client[VECTOR_DB][vector_id]
    cache_col = mongo_client[user_db][CACHE_ID]
    log_col = mongo_client[user_db][LOG_ID]
    curr_user = user_db
    curr_vector = vector_id
    print(f"VECTOR ID: {vector_id}, USER DB: {user_db}")


def vector_add(df: DataFrame, add_cols: list[str] = [], reset: bool = False):
    if reset:
        vector_col.delete_many({})
    return vector_col.insert_many(df[DB_COLS + add_cols].to_dict("records"))


def vector_search(qe: list[float], number: int, filter: list[dict] = []) -> DataFrame:
    """
    https://docs.aws.amazon.com/documentdb/latest/developerguide/vector-search.html

    filter example:
    {"$match": {"ID": "DOC_2.0"}}
    """
    result = DataFrame(
        list(
            vector_col.aggregate(
                filter
                + [
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
    if result.empty:
        return DataFrame(columns=["Data", "URL", "Section", "Embedding"])
    return result


def cache_add(data: dict):
    cache_col.insert_one(data)


def cache_get(q_dict: dict):
    return cache_col.find_one(q_dict)


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


def clear_cache():
    cache_col.delete_many({})
    log_col.delete_many({})


def log_add(data: dict):
    log_col.insert_one(data)


def log_id_found(oid: ObjectId) -> bool:
    return bool(log_col.find_one({"_id": oid}))
