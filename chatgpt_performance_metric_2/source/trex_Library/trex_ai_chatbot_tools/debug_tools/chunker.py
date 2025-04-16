import pandas as pd
from . import CHUNK_STATS
from ..database import vector_col


def db_stats():
    df = pd.DataFrame(
        vector_col.find(
            {"method": {"$ne": "CSV_DIRECT"}, "metadata.sectionIndex.0.1": {"$ne": 1}}
        )
    )
    df = df.drop(columns=["_id", "embedding"])
    print(df["token"].describe())
    df = df.sort_values(by="token", ascending=True)
    text = "\n".join(
        [
            f"Size rank: {i+1} (Token size = {row['token']})\n{row['data']}"
            for i, row in enumerate(
                [row for _, row in df.dropna(subset="data").iterrows()]
            )
        ]
    )
    with open(CHUNK_STATS, "w", encoding="utf-8") as f:
        f.write(text)
    print("MIN DATA:")
    print(df.loc[df["token"].idxmin(), "data"])
    print(df.head())
    df = df.sort_values(by="token", ascending=False)
    print("MAX DATA:")
    print(df.loc[df["token"].idxmax(), "data"])
    print(df.head())
    # print(df["token"].sum())
    # print(token_size(df["data"].str.cat(sep=" ")))
