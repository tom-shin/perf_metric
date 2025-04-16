from .. import CONFIG, proxy_request
from . import log

OPENAI_FLAG: bool = CONFIG["MODERATION"]["USE_FLAG"]
MOD_CATEGORIES: dict = CONFIG["MODERATION"]["CATEGORIES"]
MOD_MODEL: str = CONFIG["MODERATION"]["MODEL"]


@log("Moderation")
def mod_check(content: str) -> dict:
    # response = client.moderations.create(model=MOD_MODEL, input=content)
    response = proxy_request("moderation", {"input": content, "model": MOD_MODEL})
    while response["id"] == "modr-":  # Moderation API bug: sometimes returns all None
        response = proxy_request("moderation", {"input": content, "model": MOD_MODEL})
    result = response["results"][0]
    if OPENAI_FLAG and result["flagged"]:  # Use OpenAI flagging standard
        return {"flag": True, "category": "OpenAI"}
    for category, value in MOD_CATEGORIES.items():
        if result["category_scores"].get(category) > value:
            return {"flag": True, "category": category}
    return {"flag": False, "category": "OpenAI"}
