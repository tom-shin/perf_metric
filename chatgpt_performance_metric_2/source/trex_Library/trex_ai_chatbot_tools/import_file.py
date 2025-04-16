import pandas as pd
from pathlib import Path
from enum import Enum
from . import DB_COLS
from .data_parser import chunk_md
from .embedding import generate
from .navigation import is_file, read_file, read_json, read_csv, join_path


class InputType(Enum):
    DIR = "Directory"
    CSV = "CSV"
    TXT = "Text"


class InputData:
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError("Input must be written in dictionary format.")
        if not isinstance(data["path"], str | Path):
            raise ValueError(f"Path '{data['path']}' must be of type str or Path.")
        self.id: str = data["id"]
        self.path: Path = Path(data["path"])
        self.url: str = data.get("url", "")
        match data.get("method", "TXT"):
            case "DIR":
                self.type = InputType.DIR
                if data.get("map", None):
                    self.map: dict = data["map"]
                else:
                    self.map = read_json(join_path(self.path, "document.json"))
            case "CSV":
                self.type = InputType.CSV
            case "TXT":
                self.type = InputType.TXT
            case _:
                raise ValueError(f"Invalid method: {data['method']}")


def read_input_data(
    input_data: str | list | Path,
    id: str = None,
    embed=False,
    doc_json: dict = {},
    columns: list[str] = ["content"],
) -> pd.DataFrame:
    if isinstance(input_data, list):
        input_list = [InputData(el) for el in input_data]
    elif isinstance(input_data, str | Path):
        input_list = [
            InputData(
                {"path": input_data, "id": id, "map": doc_json, "columns": columns}
            )
        ]
    else:
        raise ValueError(f"Input data must be among the types str, list, or Path.")

    df = pd.DataFrame(columns=DB_COLS)
    for data in input_list:
        match data.type:
            case InputType.DIR:
                df = pd.concat([df, chunk_json(data)], ignore_index=True)
            case InputType.CSV:
                df = pd.concat([df, chunk_csv(data)], ignore_index=True)
            case InputType.TXT:
                df = pd.concat([df, chunk_txt(data)], ignore_index=True)
    if embed:
        return generate(
            df,
            filename=input_list[0].id
            + (f"+{len(input_list)-1}" if len(input_list) > 1 else ""),
        )
    return df


def chunk_data(
    id: str, content: str, name: str = "", url: str = "", dir_path: Path = Path()
) -> list[dict]:
    return [{"ID": id, **cell} for cell in chunk_md(content, name, url, dir_path)]


def chunk_json(data: InputData) -> pd.DataFrame:
    def get_name_slug_pair(obj: dict, pair_dict: dict = {}) -> dict:
        for json_obj in obj:
            if json_obj.get("fileName") is not None:
                pair_dict[json_obj["fileName"]] = (json_obj["name"], json_obj["slug"])
            if json_obj.get("childs") is not None:
                pair_dict = get_name_slug_pair(json_obj["childs"], pair_dict)
            if json_obj.get("submenu") is not None:
                pair_dict = get_name_slug_pair(json_obj["submenu"], pair_dict)
        return pair_dict

    json_cells = []
    for file_path, file_pair in get_name_slug_pair(data.map).items():
        file_path = join_path(data.path, file_path)
        if not is_file(file_path):
            print(f"MARKDOWN FILE NOT FOUND ({file_pair[0]}): {file_pair[1]}")
            continue
        content = read_file(file_path)
        json_cells.extend(
            [
                {"method": "DIR", **cell}
                for cell in chunk_data(
                    data.id,
                    content,
                    file_pair[0],
                    (data.url + file_pair[1] if data.url else ""),
                    Path(file_path).parent,
                )
            ]
        )
    return pd.DataFrame(json_cells)


def chunk_csv(data: InputData) -> pd.DataFrame:
    df = read_csv(data.path)
    cols = df.columns
    df = df.dropna(subset=[cols[0]])[cols]
    df.insert(0, "ID", data.id)
    # if "URL" in cols:
    #     df["content"] = df.apply(
    #         lambda row: chunk_data(
    #             data.id, row["content"], url=row["URL"], dir_path=data.path.parent
    #         ),
    #         axis=1,
    #     )
    #     df = df.explode("content").reset_index(drop=True)
    #     df["URL"] = df["content"].apply(lambda x: x["URL"])
    #     df["section"] = df["content"].apply(lambda x: x["section"])
    #     df["data"] = df.apply(
    #         lambda row: "\n".join(
    #             [
    #                 (
    #                     row["content"]["data"]
    #                     if col == "content"
    #                     else col + ": " + row[col]
    #                 )
    #                 for col in cols
    #                 if col != "URL"
    #             ]
    #         ),
    #         axis=1,
    #     )
    #     df["content"] = df["content"].apply(lambda x: x["content"])
    #     df["method"] = ["CSV_CHUNKED" for _ in range(len(df))]
    #     return df[["ID", "method", "data", "URL", "section", "content"]]
    df["data"] = df.apply(
        lambda row: "\n".join(
            [col + ": " + row[col] for col in cols if not pd.isna(row[col])]
        ),
        axis=1,
    )
    df["content"] = df.apply(
        lambda row: {col: row[col] for col in cols},
        axis=1,
    )
    df["method"] = ["CSV_DIRECT" for _ in range(len(df))]
    return df[["ID", "method", "data", "content"]]


def chunk_txt(data: InputData):
    return pd.DataFrame(
        [
            {"method": "TXT", **cell}
            for cell in chunk_data(data.id, read_file(data.path), data.id, data.url)
        ]
    )
