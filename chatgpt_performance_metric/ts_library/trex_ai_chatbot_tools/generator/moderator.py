from .. import CONFIG, openai_client as client

OPENAI_FLAG: bool = CONFIG["MODERATION"]["USE_FLAG"]
MOD_CATEGORIES: dict = CONFIG["MODERATION"]["CATEGORIES"]
MOD_MODEL: str = CONFIG["MODERATION"]["MODEL"]


def mod_check(content: str) -> bool:
    response = client.moderations.create(model=MOD_MODEL, input=content)
    while response.id == "modr-":  # Moderation API bug: occasionally returns all None
        response = client.moderations.create(model=MOD_MODEL, input=content)
    result = response.results[0]
    if OPENAI_FLAG and result.flagged:  # Use OpenAI flagging standard
        return True
    for category, value in MOD_CATEGORIES.items():
        if getattr(result.category_scores, category) > value:
            return True
    return False
