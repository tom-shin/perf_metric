from pandas import DataFrame
from . import (
    LAMBDA_ENV,
    openai_client as client,
    CONFIG,
    tg_model,
    token_size,
    SERVER_URL,
    GPT_INSTRUCTIONS,
)
from .embedding import get_embedding
import trex_ai_chatbot_tools.db_ops as dbo

# Static variables
DIM = CONFIG["EMBED"]["DIM"]
INPUT_TOKEN = CONFIG["TEXTGEN"]["INPUT_TOKENS"]
CONTEXT_TOKEN = CONFIG["TEXTGEN"]["CONTEXT_TOKENS"]
OUTPUT_TOKEN = CONFIG["TEXTGEN"]["OUTPUT_TOKENS"]
LIMIT = CONFIG["TEXTGEN"]["LIMIT"]
LINK_COUNT = CONFIG["TEXTGEN"]["HYPERLINK_COUNT"]
COSINE_FILTER = CONFIG["TEXTGEN"]["VECTOR_DISTANCE"]

if LAMBDA_ENV:
    import trex_ai_chatbot_tools.lambda_env.text_gen as tg
else:
    import trex_ai_chatbot_tools.local_env.text_gen as tg


def relevancy_score(e1: list[float], e2: list[float]) -> float:
    return tg.relevancy_score(e1, e2)


def get_relevant_embeddings(
    qe: list[float], number: int = CONFIG["TEXTGEN"]["LIMIT"] * 2
) -> DataFrame:
    result = dbo.vector_search(qe, number)
    result["CosineDist"] = result["Embedding"].apply(lambda x: relevancy_score(x, qe))
    return result


def get_cache_score(qe: list[float]) -> tuple[float, dict]:
    cache_result = dbo.cache_search(qe)
    if not cache_result:
        return 3, cache_result
    cosine_score = relevancy_score(qe, cache_result["embedding"])
    return cosine_score, cache_result


def filter_pages(
    sorted_df: DataFrame,
    number: int = LINK_COUNT,
    filter: float = COSINE_FILTER,
    fullpage: bool = False,
) -> list[str]:
    """
    Get most relevant pages from a sorted DataFrame given by get_relevant_embeddings()

    Input
    ---
    - sorted_df: DataFrame (result of get_relevant_embeddings())
    - number: int (number of pages to get)
    - fullpage: bool (if true, return urls that don't specify a section)

    Output
    ---
    - list[str] (list of urls)
    """
    sects = []
    urls = []
    for _, row in sorted_df.dropna(subset="URL").iterrows():
        if row["CosineDist"] > filter:
            break
        section = row["URL"].split("#")[0]
        if section not in sects:
            sects.append(section)
            urls.append(row["URL"])
            if len(urls) >= number:
                break
    return [SERVER_URL + url for url in (sects if fullpage else urls)]


def generate_content(
    df: DataFrame, token: int = CONTEXT_TOKEN, limit: int = LIMIT
) -> tuple[str, list[str]]:
    sorted_context = df.sort_values(by="CosineDist")
    if limit:
        sorted_context = sorted_context[:limit]
    context = "Context:"
    for i, data in sorted_context.iterrows():
        if token - data["Token"] < 0:
            if i == 0:
                return "", []
            return context, list(sorted_context["Data"])[: i - 1]
        token -= data["Token"]
        context += "\n***\n" + data["Data"]
    return context, list(sorted_context["Data"])


def filter_history(history: list[dict], content: str) -> list[dict]:
    split_i = 0
    size = INPUT_TOKEN - token_size(content)
    for i in range(len(history) - 1, -1, -1):
        size -= token_size(history[i]["content"])
        if size < 0:
            split_i = i + 1
    return history[split_i:]


def ask_question(
    query: str, context: str, history: list[dict] = [], token_limit: int = OUTPUT_TOKEN
) -> str:
    answer = client.chat.completions.create(
        model=str(tg_model),
        messages=[
            {
                "role": "system",
                "content": GPT_INSTRUCTIONS,
            }
        ]
        + filter_history(history, query + "\n" + context)
        + [
            {"role": "system", "name": "context_provider", "content": context},
            {"role": "user", "content": query},
        ],
        max_tokens=token_limit,
    )
    return answer.choices[0].message.content


def answer_question(query: str, history: list[dict] = []) -> dict:
    qe = get_embedding(query)
    score, cache = get_cache_score(qe)
    if cache_check(score):
        return cache_return(query, history, score, cache)

    # Filter history (return from cache if found)
    sorted_df = get_relevant_embeddings(qe)
    conv = ""
    if history and sorted_df.iloc[0]["CosineDist"] > COSINE_FILTER:
        conv = f"user: {query}"
        add_i = len(history)
        for i in range(add_i - 1, -1, -1):
            if history[i]["role"] == "user":
                conv = "\n\n".join(
                    [f"{el['role']}: {el['content']}" for el in history[i:add_i]]
                    + [conv]
                )
                qe = get_embedding(conv)
                score, cache = get_cache_score(qe)
                if cache_check(score):
                    return cache_return(query, history, score, cache)
                sorted_df = get_relevant_embeddings(qe)
                if sorted_df.iloc[0]["CosineDist"] <= COSINE_FILTER:
                    break
                add_i = i
        if add_i > 0:
            conv = "\n\n".join(
                [f"{el['role']}: {el['content']}" for el in history[i:add_i]]
                + [f"user: {query}"]
            )
            qe = get_embedding(conv)
            score, cache = get_cache_score(qe)
            if cache_check(score):
                return cache_return(query, history, score, cache)
            sorted_df = get_relevant_embeddings(qe)

    links = filter_pages(sorted_df)
    context, c_list = generate_content(sorted_df, CONTEXT_TOKEN - token_size(query))
    return {
        "query": query,
        "history_used": bool(conv),
        "conversation": conv,
        "context": context,
        "list": c_list,
        "response": ask_question(query, context, history),
        "hyperlinks": links,
        "cache_used": False,
        "embedding": qe,
    }


def cache_check(score: float) -> bool:
    return score < 0.05


def cache_return(query: str, history: list[dict], score: float, cache: dict) -> dict:
    cache.update({"cache_used": True})
    if score < 0.01:
        return cache
    cache.update(
        {"query": query, "response": ask_question(query, cache["context"], history)}
    )
    return cache
