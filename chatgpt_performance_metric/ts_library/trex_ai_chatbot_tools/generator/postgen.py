import pandas as pd
from . import LINK_COUNT, LINK_FILTER, IMAGE_FILTER
from .ChatData import ChatData
from .. import SERVER_URL, relevancy_score
from ..embedding import get_embedding


LINK_WEIGHT = {
    "CosineDist": LINK_FILTER["QueryWeight"],
    "ResponseDist": LINK_FILTER["ResponseWeight"],
}
LINK_NORM = sum(LINK_WEIGHT.values())
IMAGE_WEIGHT = {
    "CosineDist": IMAGE_FILTER["QueryWeight"],
    "ResponseDist": IMAGE_FILTER["ResponseWeight"],
    "FileDist": IMAGE_FILTER["FilenameWeight"],
}
IMAGE_NORM = sum(IMAGE_WEIGHT.values())


def generate_features(data: ChatData):
    if not data.check:
        data.set_features([], [], {})
        return
    if data.cache_similar:
        data.set_features(
            data.cache["hyperlinks"], data.cache["link_scores"], data.cache["image"]
        )
        return
    data.df["ResponseDist"] = data.df["Embedding"].apply(
        lambda x: relevancy_score(x, data.re)
    )
    data.df = data.df.sort_values(by="ResponseDist")
    data.set_features(*filter_pages(data.df), get_image(data))


def filter_pages(df: pd.DataFrame, fullpage: bool = False) -> list[str]:
    def scoring(row: pd.Series) -> float:
        return sum(row[col] * w for col, w in LINK_WEIGHT.items()) / LINK_NORM

    sects = []
    urls = []
    link_df = df.dropna(subset="URL")[["URL"] + list(LINK_WEIGHT.keys())]
    link_df["Section"] = link_df["URL"].apply(lambda url: url.split("#")[0])
    link_df["Score"] = link_df.apply(scoring, axis=1)
    link_df = link_df.sort_values(by="Score")
    for _, row in link_df.iterrows():
        if row["Section"] not in sects:
            sects.append(row["Section"])
            urls.append(
                {
                    "link": SERVER_URL + (row["Section"] if fullpage else row["URL"]),
                    "score": row["Score"],
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

    data.df["Image"] = data.df.dropna(subset="Metadata")["Metadata"].apply(
        lambda x: x.get("ImageData")
    )
    df = (
        data.df[["Image", "CosineDist", "ResponseDist"]]
        .dropna(subset="Image")
        .explode("Image")
        .reset_index(drop=True)
    )

    if df.empty:
        return {}
    df["FileDist"] = df.apply(
        lambda row: relevancy_score(
            get_embedding(
                f'Name: {row["Image"]["alt_text"]}\nFile: {row["Image"]["file_name"]}'
            ),
            data.re,
        ),
        axis=1,
    )
    df["Score"] = df.apply(scoring, axis=1)
    idx = df["Score"].idxmin()
    score = df.loc[idx]["Score"]
    if score > IMAGE_FILTER["PassScore"]:
        return {}
    return df.loc[idx]["Image"].update({"score": score}) or df.loc[idx]["Image"]
