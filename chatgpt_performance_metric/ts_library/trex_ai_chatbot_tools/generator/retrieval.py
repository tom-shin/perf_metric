from pandas import DataFrame
from . import CONTEXT_TOKEN, CHUNK_LIMIT, gen_log
from .ChatData import ChatData
from .cache import get_cache
from ..database import vector_search
from ..embedding import get_relevant_embeddings


def generate_components(data: ChatData):
    get_cache(data)
    gen_log.log("Retrieval")
    if data.cache_similar:
        data.set_context(
            DataFrame(),
            data.cache["list"],
            data.cache["context"],
            data.cache["relevancy"],
        )
        return
    generate_context(data)


def generate_context(data: ChatData, token: int = CONTEXT_TOKEN) -> None:
    df = get_relevant_embeddings(data.qe, vector_search(data.qe, CHUNK_LIMIT * 2))
    if not len(df):
        data.set_context(df, [], "", 2)
        return
    if CHUNK_LIMIT:
        df = df[:CHUNK_LIMIT]
    context = "Context:"
    for i, row in df.iterrows():
        if token - row["Token"] < 0:
            df = df[: i - 1]
            break
        token -= row["Token"]
        context += "\n***\n" + row["Data"]
    data.set_context(df, list(df["Data"]), context, df.iloc[0]["CosineDist"])
