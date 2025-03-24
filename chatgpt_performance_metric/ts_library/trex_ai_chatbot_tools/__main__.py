import json
import os
import pandas as pd
import requests
import shutil
import trex_ai_chatbot_tools.database as db
import trex_ai_chatbot_tools.debug_tools as dt
import trex_ai_chatbot_tools.fine_tune as ft
import trex_ai_chatbot_tools.generator as gen
import trex_ai_chatbot_tools.text_gen as tg
from . import CONFIG_PATH, tg_model
from .debug_tools.debug_main import debug_main
from .webapp.routers.stream import STREAM_URL

CONVERSATION = []
TEXTGEN_HISTORY = []


# Main functions
def get_answer(query: str, history: list[dict] = []) -> None:
    result = tg.simple_answer(query, history[:])
    print(result["response"])
    print_features(result)
    history.extend(
        [
            {"role": "user", "content": query},
            {"role": "assistant", "content": result["response"]},
        ]
    )


def stream_answer(query: str, history: list[dict] = []) -> None:
    response = requests.post(
        STREAM_URL + "/chat",
        data=json.dumps({"query": query, "history": history[:]}),
        headers={"Content-Type": "application/json"},
        stream=True,
    )
    if response.status_code != 200:
        raise ConnectionError(f"Error [/chat]: {response.status_code}, {response.text}")

    bytestore = []
    stream = response.iter_content(decode_unicode=True)
    for chunk in stream:
        if bytestore:
            bytestore.append(chunk)
            try:
                line = b"".join(bytestore).decode("utf-8")
                print(line, end="")
                bytestore = []
            except:
                pass
            continue
        try:
            line = chunk.decode("utf-8")
            if line:
                print(line, end="")
            else:
                pass
        except:
            bytestore.append(chunk)
    print()
    response = requests.get(STREAM_URL + "/result")
    if response.status_code != 200:
        raise ConnectionError(
            f"Error [/result]: {response.status_code}, {response.text}"
        )
    result = response.json()
    print_features(result)
    history.extend(
        [
            {"role": "user", "content": query},
            {"role": "assistant", "content": result["response"]},
        ]
    )


def print_features(result: dict):
    if result["hyperlinks"]:
        print(f'Links: {result["link_scores"]}')
    if result["image"]:
        print(f'Image: {result["image"]}')
    TEXTGEN_HISTORY.append(result)


def print_debug(silent=False) -> str:
    "Print last generated answer to DEBUG_OUTPUT"
    if not TEXTGEN_HISTORY:
        if not silent:
            print("No question has been asked yet.")
        return ""
    recent = TEXTGEN_HISTORY[-1]
    if not silent:
        print("Printing...")
        print(recent)
    return ("\n\n" + "--" * 75 + "\n\n").join(
        [
            f"TEXTGEN MODEL: {str(tg_model)}",
            "TEXTGEN INPUT:\n\n" + recent["query"],
            "TEXTGEN OUTPUT:\n\n" + recent["response"],
            "POSTGEN LINK:"
            + (
                "\n" + "\n".join(recent["hyperlinks"])
                if recent["hyperlinks"]
                else " None"
            ),
            "POSTGEN IMAGE:"
            + (
                "\n" + json.dumps(recent["image"], indent=4)
                if recent["image"]
                else " None"
            ),
            f"TIME ASKED: {recent['asked']}",
            "EXECUTION TIME:\n"
            + "\n".join([json.dumps(step, indent=4) for step in recent["ExecTime"]]),
            f"CACHE USED: {recent['cache_score'] < gen.CACHE_SIM} ({recent['cache_score']})",
            (
                "CHAT_HISTORY:"
                + (
                    "\n\n"
                    + "\n".join(
                        [el["role"] + ": " + el["content"] for el in CONVERSATION[:-2]]
                    )
                    if len(CONVERSATION) > 2
                    else " None"
                )
            ),
            "TEXTGEN CONTEXT:\n\n" + ("\n" + "--" * 75 + "\n").join(recent["list"]),
        ]
    )


# Save states
def save_state(state_id: str, override: bool = False, silent=False):
    "override: if state_id is taken, overwrite existing history"
    path = f"History/{state_id}/"
    os.makedirs(path, exist_ok=override)
    # os.makedirs(path + "/Input", exist_ok=override)
    # os.makedirs(path + "/Output", exist_ok=override)
    for file in [CONFIG_PATH]:
        shutil.copy2(file, path + file)
    if not silent:
        print(f"Model files and parameters have been saved to state ID [{state_id}].")


def new_save_state(custom_query: str = "State ID: ") -> str:
    "Ask for state ID until a new ID is given. Return valid ID."
    id = input(custom_query)
    path = f"History/{id}/"
    override = False
    while os.path.exists(path) or id == "TEMPORARY_STATE":
        new_id = input(
            f"""The state ID [{id}] is already taken.\nProvide a different state ID: """
        )
        if new_id == "override":
            override = True
            break
        elif new_id == "TEMPORARY_STATE":
            print("INVALID NAME: DESIGNATED ID")
        else:
            id = new_id
            path = f"History/{id}/"
    save_state(id, override)
    return id


def get_save_state(custom_query: str = "State ID: ") -> str:
    "Ask for state ID until an existing ID is given. Return found ID."
    id = input(custom_query)
    path = f"History/{id}/"
    while not os.path.exists(path):
        id = input(
            f"Save state with ID [{id}] does not exist.\nProvide a different state ID: "
        )
        path = f"History/{id}/"
    return id


def load_state(state_id: str, save_bypass: bool = False):
    "save_bypass: skip saving current state before loading state"
    if not save_bypass:
        if input(
            f"Would you like to save the current state before you load save state [{state_id}]? [Y/N]\n"
        ).lower() in ["y", "yes"]:
            new_save_state()
    for file in [CONFIG_PATH]:
        shutil.copy2(f"History/{state_id}/" + file, file)
    if not save_bypass:
        print(f"Save state [{state_id}] has been loaded.")
    return


def get_state_list():
    return os.listdir("History/")


def delete_state(state_id: str, safety_bypass: bool = False):
    path = f"History/{state_id}/"
    if not os.path.exists(path):
        print(f"Save state with ID [{state_id}] does not exist.")
        return
    if not safety_bypass:
        if (
            input(
                f"Are you sure you wish to delete the save state with ID [{state_id}]?\nThis action is not reversable. (Y/N): "
            )
        ).lower() not in ["y", "yes"]:
            return
    try:
        shutil.rmtree(path)
        if not safety_bypass:
            print(f"Save state with ID [{state_id}] has been permanently deleted.")
    except:
        print(f"Deleting save state with ID [{state_id}] has failed.")


def compare_state(query: str, state1: str, state2: str, quicksave: bool = True):
    if quicksave:
        save_state("TEMPORARY_STATE", True, True)
    load_state(state1, True)
    print(f"Answer given by save state [{state1}]:")
    get_answer(query)
    load_state(state2, True)
    print(f"Answer given by save state [{state2}]:")
    get_answer(query)
    if quicksave:
        load_state("TEMPORARY_STATE", True)
        delete_state("TEMPORARY_STATE", True)


# Main function
def main():
    print(f"Current model: {str(tg_model)}")
    print(f"Vector DB: {db.VECTOR_ID}, User DB: {db.USER_DB_ID}")
    stream = False
    while True:
        query = input("Ask the bot a question:\n")
        match query.lower():
            case "exit":
                exit()
            case "print":
                with open(dt.TEXTGEN_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(print_debug())
            # # FINE TUNING
            # case "process":
            #     try:
            #         ft_df = pd.read_csv(ch.TUNING_DATA_CSV).dropna(subset=["Question"])[
            #             ["Question", "Answer"]
            #         ]
            #     except:
            #         error_filenotfound("Fine tuning training data", ch.TUNING_DATA_CSV)
            #         return False
            #     json_list = ft.process_ft_input(tg.convert_df(ft_df))
            #     with open(ch.TUNING_DATA_JSON, "w") as f:
            #         for obj in json_list:
            #             json.dump(obj, f)
            #             f.write("\n")
            #     print("Fine tuning training data processed to JSON list.")
            # case "tuning":
            #     with open(ch.TUNING_DATA_JSON, "r") as f:
            #         tuning_data = []
            #         for line in f:
            #             tuning_data.append(json.loads(line))
            #     print("Generating new fine tuning job...")
            #     ft.generate_ft_model(tuning_data)
            # # SAVE STATE
            # case "save":
            #     new_save_state()
            # case "load":
            #     load_state(get_save_state())
            # case "list":
            #     for state in get_state_list():
            #         print(state)
            # case "delete":
            #     delete_state(input("State ID: "))
            # case "compare":
            #     save1 = get_save_state("State 1: ")
            #     save2 = get_save_state("State 2: ")
            #     query = input("Provide a query: ")
            #     compare_state(query, save1, save2)
            case "stream":
                stream = not stream
                print(f"Streamed response is now {'' if stream else 'in'}active.")
            case "clear":
                db.clear_cache()
                print("Cleared cache & log.")
            case "log":
                print(
                    f"Log print is now {'on' if tg.gen_log.toggle_log_print() else 'off'}."
                )
            case "debug":
                print("Entering debug mode...")
                debug_main()
            case "prompt":
                if gen.GPT_INSTRUCTIONS:
                    gen.GPT_INSTRUCTIONS = ""
                    print("Prompt is now empty.")
                else:
                    gen.GPT_INSTRUCTIONS = gen.tg_env.GPT_INSTRUCTIONS
                    print("Prompt has returned.")
            case _:
                (
                    stream_answer(query, CONVERSATION)
                    if stream
                    else get_answer(query, CONVERSATION)
                )
                with open(dt.TEXTGEN_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(print_debug(True))
                with open(dt.TEXTGEN_HISTORY, "w") as f:
                    json.dump(TEXTGEN_HISTORY, f, default=str, indent=4)


if __name__ == "__main__":
    main()
