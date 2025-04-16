import os
import json
import pandas as pd
from trex_ai_chatbot_tools.embedding import generate
from trex_ai_chatbot_tools.data_parser import chunk_md


def read_input_data(
    path: str = None, id: str = None, columns: list = ["Content"]
) -> pd.DataFrame:
    df = pd.DataFrame(columns=["ID", "Data", "URL", "Section", "Content"])
    if os.path.isdir(path):
        df = pd.concat([df, read_DocRepo(path, id)], ignore_index=True)
    elif os.path.isfile(path):
        if path[-4:] == ".csv":
            df = pd.concat(
                [df, read_CSV(pd.read_csv(path), id, columns)], ignore_index=True
            )
        else:
            df = pd.concat([df, read_txt(path, id)], ignore_index=True)
    return generate(df)


def read_DocRepo(path: str, id: str) -> pd.DataFrame:
    # Get all URLs
    with open(path + "/document.json", "r") as f:
        document_json = json.load(f)

    def get_name_slug_pair(obj: dict, pair_dict: dict = {}) -> dict:
        """{FILE PATH: [FILE NAME, FILE URL]}"""
        for json_obj in obj:
            pair_dict[json_obj["fileName"]] = [json_obj["name"], json_obj["slug"]]
            if json_obj.get("childs") is not None:
                pair_dict = get_name_slug_pair(json_obj["childs"], pair_dict)
        return pair_dict

    fileDict = get_name_slug_pair(document_json)
    # Read all .md files
    json_cells = []
    for file_path, file_pair in fileDict.items():
        file_path = path + "/" + file_path
        # Format .md files by headers
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            print(f"MARKDOWN FILE NOT FOUND ({file_pair[0]}): {file_path}")
            continue
        chunk_list = chunk_md(content, file_pair[0], file_pair[1])
        for data_cell in chunk_list:
            json_cell = {
                "ID": id,
                "URL": "development/enn-sdk/document/" + data_cell.url,
                "Section": [sect[1] for sect in data_cell.section],
                "Content": data_cell.data,
                "Data": (
                    f"Section: {data_cell.getHeader()}\nContent:\n{data_cell.data}"
                    if data_cell.section
                    else f"Content:\n{data_cell.data}"
                ),
            }
            if data_cell.split_data:
                json_cell.update({"SplitIndex": data_cell.split_data})
            json_cells.append(json_cell)
    return pd.DataFrame(json_cells)


def read_CSV(
    df: pd.DataFrame, id: str = None, columns: list[str] = ["Content"]
) -> pd.DataFrame:
    df = df.dropna(subset=[columns[0]])[columns]
    df.insert(0, "ID", id)
    if "URL" in columns:
        df["Content"] = df.apply(
            lambda row: chunk_md(row["Content"], row["Title"], row["URL"]),
            axis=1,
        )
        df = df.explode("Content").reset_index(drop=True)
        df["URL"] = df["Content"].apply(lambda x: x.url)
        df["Section"] = df["Content"].apply(lambda x: x.getHeader())
        df["Content"] = df["Content"].apply(lambda x: x.data)
    df["Data"] = df.apply(
        lambda row: "\n".join([col + ": " + row[col] for col in columns]),
        axis=1,
    )
    return df


def read_txt(path: str, id: str = None):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    data = [[id, line, None, None, line] for line in lines]
    return pd.DataFrame(data)
