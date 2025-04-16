from pymongo import MongoClient
from pymongo.collection import Collection
from pandas import DataFrame
from . import CONNECTION_STRING, CONFIG, DB_COLS, USER_DB_ID, get_time
from .embedding import DIM
from .navigation import read_file
from bson import ObjectId

mongo_client = MongoClient(CONNECTION_STRING)
VECTOR_DB: str = CONFIG["DATABASE"]["VECTOR"]["DB_ID"]
PROMPT_DB: str = CONFIG["DATABASE"]["PROMPT"]["DB_ID"]
VECTOR_ALL_ID: str = CONFIG["DATABASE"]["VECTOR"]["ALL_ID"]
VECTOR_INDEX: str = CONFIG["DATABASE"]["VECTOR"]["INDEX"]
DB_USERTYPES: dict = CONFIG["DATABASE"]["VECTOR_DB_TYPES"]
VECTOR_ID: str = CONFIG["DATABASE"]["VECTOR"]["COL_ID"]
CACHE_ID: str = CONFIG["DATABASE"]["SYSTEM"]["CACHE_ID"]
CACHE_INDEX: str = CONFIG["DATABASE"]["SYSTEM"]["CACHE_INDEX"]
CACHE_LIMIT: str = CONFIG["DATABASE"]["SYSTEM"]["CACHE_LIMIT"]
LOG_ID: str = CONFIG["DATABASE"]["SYSTEM"]["LOG_ID"]
PROMPT_COL = mongo_client[PROMPT_DB][CONFIG["DATABASE"]["PROMPT"]["COL_ID"]]

vector_col = mongo_client[VECTOR_DB][VECTOR_ID]
cache_col = mongo_client[USER_DB_ID][CACHE_ID]
log_col = mongo_client[USER_DB_ID][LOG_ID]
curr_vector = VECTOR_ID
curr_user = USER_DB_ID
CACHE_STRING = ["count", "last_accessed", "asked"]


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


def add_vector_index(col: Collection):
    """
    https://github.com/aws-samples/amazon-documentdb-samples/blob/master/samples/vector-search/semantic_text_hnsw.ipynb
    """
    if VECTOR_INDEX not in [el["name"] for el in col.list_indexes()]:
        col.create_index(
            [("embedding", "vector")],
            name=VECTOR_INDEX,
            vectorOptions={"dimensions": DIM, "similarity": "cosine"},
        )


def list_users():
    return [
        db
        for db in mongo_client.list_database_names()
        if db not in [VECTOR_DB, PROMPT_DB]
    ]


def vector_add(df: DataFrame, add_cols: list[str] = [], reset: bool = False):
    if reset:
        vector_col.delete_many({})
        add_vector_index(vector_col)
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
                                "path": "embedding",
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
        return DataFrame(columns=["data", "URL", "section", "embedding"])
    return result


def cache_add(data: dict):
    if cache_col.count_documents({}) >= CACHE_LIMIT:
        cache_col.delete_many(
            {
                "_id": {
                    "$in": [
                        doc["_id"]
                        for doc in (
                            cache_col.find()
                            .sort(CACHE_STRING)
                            .limit(cache_col.count_documents({}) - CACHE_LIMIT)
                        )
                    ]
                }
            }
        )
    data.update({"count": 0, "last_accessed": get_time()})
    cache_col.insert_one(data)


def cache_get(q_dict: dict):
    return cache_col.find_one_and_update(
        q_dict,
        {"$inc": {"count": 1}, "$set": {"last_accessed": get_time()}},
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
        return cache_get({"_id": result[0]["_id"]})
    return {}


def clear_cache():
    cache_col.delete_many({})
    log_col.delete_many({})
    add_vector_index(cache_col)
    if CACHE_INDEX not in [el["name"] for el in cache_col.list_indexes()]:
        cache_col.create_index(CACHE_STRING, name=CACHE_INDEX)


def log_add(data: dict):
    log_col.insert_one(data)


def new_log_id() -> ObjectId:
    oid = ObjectId()
    while log_col.find_one({"_id": oid}):
        oid = ObjectId()
    return oid


def prompt_add(id: str, prompt: str):
    return PROMPT_COL.insert_one({"ID": id, "text": prompt, "uploadtime": get_time()})


def prompt_update(p_list: list[dict], reset: bool = False):
    time = get_time()
    if reset:
        PROMPT_COL.delete_many({})
    for p_file in p_list:
        PROMPT_COL.insert_one(
            {"ID": p_file["id"], "text": read_file(p_file["path"]), "uploadtime": time}
        )


def prompt_get(id: str) -> str:
    prompt_obj = PROMPT_COL.find_one({"ID": id})
    if prompt_obj:
        return prompt_obj["text"]
    return None
