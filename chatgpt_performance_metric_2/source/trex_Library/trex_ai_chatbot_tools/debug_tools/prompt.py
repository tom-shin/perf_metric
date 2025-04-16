import pandas as pd
from ..database import PROMPT_COL, prompt_add, prompt_get
from ..generator import prompt as p
from ..navigation import read_file


def opening():
    print(
        f"""Current prompt: {p.prompt_id}
Available prompts: {PROMPT_COL.count_documents({})}
Commands:
    prompt list: list currently available prompts by id
    prompt print: print current prompt
    prompt print [id]: print prompt by id
    prompt set [id]: set prompt by id
    prompt upload [id] [path]: upload prompt from file with id (must contain no spaces)"""
    )


def prompt_main(command: list[str]):
    if not command:
        opening()
        return
    match command[0].lower():
        case "list":
            df = pd.DataFrame(PROMPT_COL.find({})).drop(columns=["_id", "text"])
            df.insert(0, " ", " ")
            df.loc[df["ID"] == p.prompt_id, " "] = "•"
            print(df.to_string(index=False))
        case "print":
            if len(command) == 1:
                print(p.prompt)
                return
            id = command[1]
            text = prompt_get(id)
            if text == None:
                print(f"A prompt with ID [{id}] doesn't exist.")
                return
            print(text)
        case "set":
            if len(command) == 1:
                print("A prompt id has not been provided.")
            id = command[1]
            p.set_prompt(id)
        case "upload":
            if len(command) == 1:
                print("[prompt upload] requires an id and an upload path.")
            id = command[1]
            if prompt_get(id) is not None:
                print(f"Prompt id [{id}] is already taken. Use a new ID.")
                return
            path = " ".join(command[2:])
            if not path:
                print("A file path must be provided.")
                return
            try:
                text = read_file(path)
            except:
                print(f"[{path}] is not a valid file path/cannot be read.")
                return
            prompt_add(id, text)
            print(f"Prompt [{id}] has been added to the prompt DB.")
        case _:
            print(f"[{command[0]}] is not a valid prompt command.")
