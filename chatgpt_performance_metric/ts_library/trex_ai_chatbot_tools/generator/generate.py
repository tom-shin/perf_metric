from . import GPT_INSTRUCTIONS, INPUT_TOKEN, OUTPUT_TOKEN, SPLIT_STRING, GEN_TEMP
from .ChatData import ChatData
from .. import openai_client as client, tg_model, token_size


def generate_response(data: ChatData) -> dict:
    if data.cache_equivalent:
        data.set_response(data.cache["response"])
        return
    data.set_response(
        client.chat.completions.create(
            model=str(tg_model),
            messages=generate_messages(data),
            temperature=GEN_TEMP,
            max_completion_tokens=OUTPUT_TOKEN,
        )
        .choices[0]
        .message.content
    )


def generate_stream(data: ChatData) -> dict:
    if data.cache_equivalent:
        data.set_stream(iter(SPLIT_STRING.findall(data.cache["response"])), True)
        return
    data.set_stream(
        client.chat.completions.create(
            model=str(tg_model),
            messages=generate_messages(data),
            stream=True,
            stream_options={"include_usage": True},
            temperature=GEN_TEMP,
            max_completion_tokens=OUTPUT_TOKEN,
        )
    )


def get_response(cache: dict) -> str:
    return cache["response"] if cache.get("response") else "".join(cache["stream"])


def generate_messages(data: ChatData) -> list[dict]:
    history = data.history
    content = data.query + "\n" + data.context
    size = INPUT_TOKEN - token_size(content)
    i = len(history) - 1
    while i > -1:
        size -= token_size(history[i]["content"])
        if size < 0:
            break
        i -= 1
    return (
        [
            {
                "role": "system",
                "content": GPT_INSTRUCTIONS,
            }
        ]
        + history[i + 1 :]
        + [
            {"role": "system", "name": "context_provider", "content": data.context},
            {"role": "user", "content": data.query},
        ]
    )
