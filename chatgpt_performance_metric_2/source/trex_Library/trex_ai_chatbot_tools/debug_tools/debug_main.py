import json
import pandas as pd
from . import DEBUG_INPUT, BULKGEN_CSV, COSINE_MATRIX, write_csv
from .embedding import cosine_matrix
from .chunker import db_stats
from .generator import bulk_generate
from .prompt import prompt_main

# from .url_scoring import url_main


def debug_interface(command: str) -> bool:
    match command.lower().split(" ")[0]:
        case "exit":
            print("Ending debug mode. Returning to main interface...")
            return False
        case "bulk":
            print(f"Bulk generating responses from [{DEBUG_INPUT}]...")
            with open(DEBUG_INPUT, encoding="utf-8") as f:
                questions = json.load(f)
            df = pd.concat(
                [
                    pd.DataFrame(columns=["query", "history"]),
                    pd.DataFrame(bulk_generate(questions)),
                ],
                ignore_index=True,
            )
            write_csv(df, BULKGEN_CSV)
            print(f"Bulk generation results saved to [{BULKGEN_CSV}].")
        case "chunks":
            db_stats()
        case "cosine":
            with open(DEBUG_INPUT, "r", encoding="utf-8") as f:
                questions = json.load(f)
            print(f"Generating cosine matrix using questions from [{DEBUG_INPUT}]...")
            df = cosine_matrix(pd.DataFrame(questions))
            write_csv(df, COSINE_MATRIX)
            print(f"Cosine matrix saved to [{COSINE_MATRIX}].")
        case "prompt":
            prompt_main(command.split(" ")[1:])
        # case "url":
        #     url_main(command.split(" ")[1:])
        case _:
            print(f"[{command}] is not a valid command.")
    return True


def debug_main():
    while True:
        command = input("Give a command: ")
        if not debug_interface(command):
            break
