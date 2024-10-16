import os
import pandas as pd
import openai
import json
import shutil
import trex_ai_chatbot_tools.CSV_handler as ch
import trex_ai_chatbot_tools.data_parser as dp
import trex_ai_chatbot_tools.embedding as emb
import trex_ai_chatbot_tools.text_gen as tg
import trex_ai_chatbot_tools.fine_tune as ft
import trex_ai_chatbot_tools.debug_tools as dt
from . import (
    CONFIG_PATH,
    tg_model,
    error_invalidkey,
    error_filenotfound,
)

EMPTY_HISTORY = "No question has been asked yet."
question = EMPTY_HISTORY
content = EMPTY_HISTORY
answer = EMPTY_HISTORY
history = []


# Main functions
def answer_question(query: str, history: list[dict] = []) -> None:
    """
    Quick answer: print 5 most relevant links relating to the query
    GPT answer: use most relevant data to input into GPT
    """
    try:
        tg_answer = tg.answer_question(query, history)
    except openai.AuthenticationError:
        error_invalidkey()
        return
    global question, content, answer
    question = query
    content = tg_answer["context"]
    answer = tg_answer["response"]
    history.extend(
        [{"role": "user", "content": query}, {"role": "assistant", "content": answer}]
    )
    print(answer)
    if tg_answer["hyperlinks"]:
        print(f'Links: {tg_answer["hyperlinks"]}')
    return answer


def print_debug(silent=False) -> str:
    "Print last generated answer to DEBUG_OUTPUT"
    if content == EMPTY_HISTORY:
        print(EMPTY_HISTORY)
        return ""
    if not silent:
        print("Printing...")
        print(answer)
    return (
        "TEXTGEN_MODEL: "
        + str(tg_model)
        + "\n\n"
        + "--" * 75
        + "\n\nTEXTGEN_INPUT: \n\n"
        + question
        + "\n\n"
        + "--" * 75
        + "\n\nTEXTGEN_OUTPUT: \n\n"
        + answer
        + (
            "\n\n"
            + "--" * 75
            + "\n\nCHAT_HISTORY: \n\n"
            + "\n".join([el["role"] + ": " + el["content"] for el in history[:-2]])
            if len(history) > 2
            else ""
        )
        + "\n\n"
        + "--" * 75
        + "\n\nTEXTGEN_CONTEXT: \n\n"
        + content
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
    answer_question(query, False)
    load_state(state2, True)
    print(f"Answer given by save state [{state2}]:")
    answer_question(query, False)
    if quicksave:
        load_state("TEMPORARY_STATE", True)
        delete_state("TEMPORARY_STATE", True)


# Main function
def main():
    quick = True
    debug_filter = 0
    while True:
        query = input("Ask the bot a question:\n").lower()
        match query:
            case "exit":
                exit()
            case "print":
                with open(ch.DEBUG_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(print_debug())
            case "process":
                try:
                    ft_df = pd.read_csv(ch.TUNING_DATA_CSV).dropna(subset=["Question"])[
                        ["Question", "Answer"]
                    ]
                except:
                    error_filenotfound("Fine tuning training data", ch.TUNING_DATA_CSV)
                    return False
                json_list = ft.process_ft_input(tg.convert_df(ft_df))
                with open(ch.TUNING_DATA_JSON, "w") as f:
                    for obj in json_list:
                        json.dump(obj, f)
                        f.write("\n")
                print("Fine tuning training data processed to JSON list.")
            case "tuning":
                with open(ch.TUNING_DATA_JSON, "r") as f:
                    tuning_data = []
                    for line in f:
                        tuning_data.append(json.loads(line))
                print("Generating new fine tuning job...")
                ft.generate_ft_model(tuning_data)
            case "save":
                new_save_state()
            case "load":
                load_state(get_save_state())
            case "list":
                for state in get_state_list():
                    print(state)
            case "delete":
                delete_state(input("State ID: "))
            case "compare":
                save1 = get_save_state("State 1: ")
                save2 = get_save_state("State 2: ")
                query = input("Provide a query: ")
                compare_state(query, save1, save2)
            case "debug":
                dt.bulk_generate(debug_filter)
            case "data":
                dt.db_stats()
            case "quick":
                quick = not quick
                if quick:
                    debug_filter = 0
                    print("Quick debug enabled.")
                else:
                    debug_filter = float(
                        input("Provide answer filter (1 for no filter): ")
                    )
                    print("Quick debug disabled.")
            case _:
                answer_question(query, history)
                with open(ch.DEBUG_OUTPUT, "w", encoding="utf-8") as f:
                    f.write(print_debug(True))


if __name__ == "__main__":
    main()
