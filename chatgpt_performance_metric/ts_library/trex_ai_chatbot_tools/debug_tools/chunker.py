import pandas as pd
from . import CHUNK_STATS
from ..database import vector_col


def db_stats():
    df = pd.DataFrame(
        vector_col.find(
            {"Method": {"$ne": "CSV_DIRECT"}, "Metadata.SectionIndex.0.1": {"$ne": 1}}
        )
    )
    df = df.drop(columns=["_id", "Embedding"])
    print(df["Token"].describe())
    df = df.sort_values(by="Token", ascending=True)
    text = "\n".join(
        [
            f"Size rank: {i+1} (Token size = {row['Token']})\n{row['Data']}"
            for i, row in enumerate(
                [row for _, row in df.dropna(subset="Data").iterrows()]
            )
        ]
    )
    with open(CHUNK_STATS, "w", encoding="utf-8") as f:
        f.write(text)
    print("MIN DATA:")
    print(df.loc[df["Token"].idxmin(), "Data"])
    print(df.head())
    df = df.sort_values(by="Token", ascending=False)
    print("MAX DATA:")
    print(df.loc[df["Token"].idxmax(), "Data"])
    print(df.head())
    # print(df["Token"].sum())
    # print(token_size(df["Data"].str.cat(sep=" ")))
