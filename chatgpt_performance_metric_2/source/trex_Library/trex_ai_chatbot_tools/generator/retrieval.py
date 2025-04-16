from pandas import DataFrame
from . import CONTEXT_TOKEN, CHUNK_LIMIT, INPUT_TOKEN, prompt as p, log, call
from .ChatData import ChatData
from .. import token_size
from ..database import vector_search
from ..embedding import sort_relevancy


@call("DocDB_vector")
def search(e):
    return vector_search(e, CHUNK_LIMIT * 2)


@call("tiktoken")
def get_token(text):
    return token_size(text)


@log("Generation")
def generate_components(data: ChatData):
    if data.cache_similar:
        data.set_context(
            DataFrame(),
            generate_messages(
                data, "\n***\n".join(["Context:"] + data.cache["context"])
            ),
            data.cache["context"],
            data.cache["relevancy"],
        )
        return
    generate_context(data)


def generate_context(data: ChatData) -> None:
    df = sort_relevancy(data.qe, search(data.qe))
    if not len(df):
        data.set_context(df, generate_messages(data, ""), [], 2)
        return
    if CHUNK_LIMIT:
        df = df[:CHUNK_LIMIT]
    context = "Context:"
    token = CONTEXT_TOKEN
    for i, row in df.iterrows():
        if token - row["token"] < 0:
            df = df[: i - 1]
            break
        token -= row["token"]
        context += "\n***\n" + row["data"]
    data.set_context(
        df, generate_messages(data, context), list(df["data"]), df.iloc[0]["cosineDist"]
    )


def generate_messages(data: ChatData, context: str) -> list[dict]:
    history = data.history
    size = INPUT_TOKEN - get_token("\n".join([p.prompt, context, data.query]))
    i = len(history) - 1
    while i > -1:
        size -= get_token(history[i]["content"])
        if size < 0:
            break
        i -= 1
    return (
        [
            {"role": "system", "content": p.prompt},
            {"role": "system", "name": "context_provider", "content": context},
        ]
        + history[i + 1 :]
        + [
            {"role": "user", "content": data.query},
        ]
    )
