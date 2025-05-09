import pandas as pd
from . import LINK_COUNT, LINK_FILTER, IMAGE_FILTER, log, call
from .ChatData import ChatData
from .. import SERVER_URL, relevancy_score
from ..embedding import get_embedding

LINK_WEIGHT = {
    "cosineDist": LINK_FILTER["QueryWeight"],
    "responseDist": LINK_FILTER["ResponseWeight"],
}
LINK_NORM = sum(LINK_WEIGHT.values())
IMAGE_WEIGHT = {
    "cosineDist": IMAGE_FILTER["QueryWeight"],
    "responseDist": IMAGE_FILTER["ResponseWeight"],
    "fileDist": IMAGE_FILTER["FilenameWeight"],
}
IMAGE_NORM = sum(IMAGE_WEIGHT.values())


@call("OpenAI_embed")
def get_re(data: ChatData):
    data.re


@log("PostGen")
def generate_features(data: ChatData):
    if not data.check:
        data.set_features([], [], {})
        return
    if data.cache_similar:
        data.set_features(
            data.cache["hyperlinks"], data.cache["link_scores"], data.cache["image"]
        )
        return
    get_re(data)
    data.df["responseDist"] = data.df["embedding"].apply(
        lambda x: relevancy_score(x, data.re)
    )
    data.df = data.df.sort_values(by="responseDist")
    data.set_features(*filter_pages(data.df), get_image(data))


def filter_pages(df: pd.DataFrame, fullpage: bool = False) -> list[str]:
    def scoring(row: pd.Series) -> float:
        return sum(row[col] * w for col, w in LINK_WEIGHT.items()) / LINK_NORM

    sects = []
    urls = []
    link_df = df.dropna(subset="URL")[["URL"] + list(LINK_WEIGHT.keys())]
    link_df["section"] = link_df["URL"].apply(lambda url: url.split("#")[0])
    link_df["score"] = link_df.apply(scoring, axis=1)
    link_df = link_df.sort_values(by="score")
    for _, row in link_df.iterrows():
        if row["section"] not in sects:
            sects.append(row["section"])
            urls.append(
                {
                    "link": SERVER_URL + (row["section"] if fullpage else row["URL"]),
                    "score": row["score"],
                }
            )
            if len(urls) >= LINK_COUNT:
                break
    return [
        url["link"] for url in urls if url["score"] <= LINK_FILTER["PassScore"]
    ], urls


def get_image(data: ChatData) -> dict:
    def scoring(row: pd.Series) -> float:
        return sum(row[col] * w for col, w in IMAGE_WEIGHT.items()) / IMAGE_NORM

    data.df["image"] = data.df.dropna(subset="metadata")["metadata"].apply(
        lambda x: x.get("imageData")
    )
    df = (
        data.df[["image", "cosineDist", "responseDist"]]
        .dropna(subset="image")
        .explode("image")
        .reset_index(drop=True)
    )

    if df.empty:
        return {}
    df["fileDist"] = df.apply(
        lambda row: relevancy_score(
            get_embedding(
                f'Name: {row["image"]["alt_text"]}\nFile: {row["image"]["file_name"]}'
            ),
            data.re,
        ),
        axis=1,
    )
    df["score"] = df.apply(scoring, axis=1)
    idx = df["score"].idxmin()
    score = df.loc[idx]["score"]
    if score > IMAGE_FILTER["PassScore"]:
        return {}
    return df.loc[idx]["image"].update({"score": score}) or df.loc[idx]["image"]
