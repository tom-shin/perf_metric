from . import TEXTGEN_MODEL, OUTPUT_TOKEN, SPLIT_STRING, GEN_TEMP, call, log
from .ChatData import ChatData
from .. import openai_client as client, proxy_request
import requests
from .. import PROXY_SERVER_URL


@call("OpenAI_chat")
def generate_response(messages: list[dict]) -> dict:
    # return client.chat.completions.create(payload).choices[0].message.content
    return proxy_request(
        "generate",
        {
            "model": TEXTGEN_MODEL,
            "messages": messages,
            "temperature": GEN_TEMP,
            "output_token": OUTPUT_TOKEN,
        },
    )["response"]


@call("OpenAI_chat")
def generate_stream(messages: list[dict]) -> dict:
    return client.chat.completions.create(
        model=TEXTGEN_MODEL,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
        temperature=GEN_TEMP,
        max_completion_tokens=OUTPUT_TOKEN,
    )


@log("APICall")
def generate_answer(data: ChatData, stream: bool) -> dict:
    if stream:
        if data.cache_equivalent:
            data.set_stream(iter(SPLIT_STRING.findall(data.cache["response"])), True)
            return
        data.set_stream(generate_stream(data.messages))
    else:
        if data.cache_equivalent:
            data.set_response(data.cache["response"])
            return
        data.set_response(generate_response(data.messages))
