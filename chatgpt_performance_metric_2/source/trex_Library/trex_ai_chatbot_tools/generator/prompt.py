from . import PROMPT_ID
from ..database import prompt_get

prompt_id = PROMPT_ID
prompt = prompt_get(PROMPT_ID)
if prompt == None:
    if PROMPT_ID == "default":
        print(f"WARNING: PROMPT ID MISSING IN ENVIRONMENT, PROMPT SET TO EMPTY STRING")
    else:
        print(f"WARNING: PROMPT ID [{PROMPT_ID}] INVALID, PROMPT SET TO EMPTY STRING")
    prompt_id = "NOT FOUND"
    prompt = ""


def set_prompt(id: str = PROMPT_ID) -> bool:
    search = prompt_get(id)
    if search == None:
        print(f"Prompt with ID [{id}] doesn't exist.")
        return False
    global prompt_id, prompt
    prompt_id = id
    prompt = search
    print(f"Prompt set to [{id}].")
    return True
