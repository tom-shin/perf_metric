import pandas as pd
from tqdm import tqdm
from ..embedding import generate, get_relevant_embeddings


def cosine_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = generate(df.dropna(subset="Query"), "Query")
    for i, qe in tqdm(
        enumerate(df["Embedding"]), total=len(df), desc="Generating cosine matrix"
    ):
        cosine_df = get_relevant_embeddings(qe, df)
        cosine_df = cosine_df.rename(columns={"CosineDist": i})
        df = pd.concat([df, cosine_df[i]], axis=1)
    df = df.drop(columns=["Embedding", "CosineDist"])
    return df
