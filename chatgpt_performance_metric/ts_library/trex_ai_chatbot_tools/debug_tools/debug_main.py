import json
import pandas as pd
from . import DEBUG_INPUT, BULKGEN_CSV, COSINE_MATRIX
from .embedding import cosine_matrix
from .chunker import db_stats
from .generator import bulk_generate
from .. import file_write
from ..text_gen import gen_log


def debug_main():
    while True:
        command = input("Give a command: ")
        match command.lower():
            case "exit":
                print("Ending debug mode. Returning to main interface...")
                break
            case "bulk":
                print(f"Bulk generating responses from [{DEBUG_INPUT}]...")
                revert = gen_log.log_print
                if revert:
                    gen_log.log_print = False
                with open(DEBUG_INPUT, encoding="utf-8") as f:
                    questions = json.load(f)
                df = pd.DataFrame(bulk_generate(questions))
                file_write(df.to_csv, BULKGEN_CSV, index=False)
                if revert:
                    gen_log.log_print = True
                print(f"Bulk generation results saved to [{BULKGEN_CSV}].")
            case "chunks":
                db_stats()
            case "cosine":
                with open(DEBUG_INPUT, "r", encoding="utf-8") as f:
                    questions = json.load(f)
                print(
                    f"Generating cosine matrix using questions from [{DEBUG_INPUT}]..."
                )
                df = cosine_matrix(pd.DataFrame(questions))
                file_write(df.to_csv, COSINE_MATRIX, encoding="utf-8", index=False)
                print(f"Cosine matrix saved to [{COSINE_MATRIX}].")
            case _:
                print(f"{command} is not a valid command.")
