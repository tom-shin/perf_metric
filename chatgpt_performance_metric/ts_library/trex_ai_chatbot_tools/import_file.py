import pandas as pd
from pathlib import Path
from enum import Enum
from . import DB_COLS
from .data_parser import chunk_md
from .embedding import generate
from .navigation import is_file, read_file, read_csv, join_path


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
                    self.map = read_file(join_path(self.path, "document.json"), True)
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
    columns: list[str] = ["Content"],
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
                df = pd.concat([df, read_JSON(data)], ignore_index=True)
            case InputType.CSV:
                df = pd.concat([df, read_CSV(data)], ignore_index=True)
            case InputType.TXT:
                df = pd.concat([df, read_txt(data)], ignore_index=True)
    if embed:
        return generate(df)
    return df


def chunk_to_JSON(
    id: str, content: str, name: str = "", url: str = "", dir_path: Path = Path()
) -> list[dict]:
    return [{"ID": id, **cell} for cell in chunk_md(content, name, url, dir_path)]


def read_JSON(data: InputData) -> pd.DataFrame:
    def get_name_slug_pair(obj: dict, pair_dict: dict = {}) -> dict:
        for json_obj in obj:
            pair_dict[json_obj["fileName"]] = (json_obj["name"], json_obj["slug"])
            if json_obj.get("childs") is not None:
                pair_dict = get_name_slug_pair(json_obj["childs"], pair_dict)
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
                {"Method": "DIR", **cell}
                for cell in chunk_to_JSON(
                    data.id,
                    content,
                    file_pair[0],
                    (data.url + file_pair[1] if data.url else ""),
                    Path(file_path).parent,
                )
            ]
        )
    return pd.DataFrame(json_cells)


def read_CSV(data: InputData) -> pd.DataFrame:
    df = read_csv(data.path)
    cols = df.columns
    df = df.dropna(subset=[cols[0]])[cols]
    df.insert(0, "ID", data.id)
    if "URL" in cols:
        df["Content"] = df.apply(
            lambda row: chunk_to_JSON(
                data.id, row["Content"], url=row["URL"], dir_path=data.path.parent
            ),
            axis=1,
        )
        df = df.explode("Content").reset_index(drop=True)
        df["URL"] = df["Content"].apply(lambda x: x["URL"])
        df["Section"] = df["Content"].apply(lambda x: x["Section"])
        df["Data"] = df.apply(
            lambda row: "\n".join(
                [
                    (
                        row["Content"]["Data"]
                        if col == "Content"
                        else col + ": " + row[col]
                    )
                    for col in cols
                    if col != "URL"
                ]
            ),
            axis=1,
        )
        df["Content"] = df["Content"].apply(lambda x: x["Content"])
        df["Method"] = ["CSV_CHUNKED" for _ in range(len(df))]
        return df[["ID", "Method", "Data", "URL", "Section", "Content"]]
    df["Data"] = df.apply(
        lambda row: "\n".join(
            [col + ": " + row[col] for col in cols if not pd.isna(row[col])]
        ),
        axis=1,
    )
    df["Content"] = df.apply(
        lambda row: {col: row[col] for col in cols},
        axis=1,
    )
    df["Method"] = ["CSV_DIRECT" for _ in range(len(df))]
    return df[["ID", "Method", "Data", "Content"]]


def read_txt(data: InputData):
    return pd.DataFrame(
        [
            {"Method": "TXT", **cell}
            for cell in chunk_to_JSON(data.id, read_file(data.path), data.id, data.url)
        ]
    )
