import pandas as pd
from tqdm import tqdm
from ..embedding import generate, sort_relevancy


def cosine_matrix(df: pd.DataFrame) -> pd.DataFrame:
    df = generate(df.dropna(subset="query"), "query")
    for i, qe in tqdm(
        enumerate(df["embedding"]), total=len(df), desc="Generating cosine matrix"
    ):
        cosine_df = sort_relevancy(qe, df)
        cosine_df = cosine_df.rename(columns={"cosineDist": i})
        df = pd.concat([df, cosine_df[i]], axis=1)
    df = df.drop(columns=["embedding", "cosineDist"])
    return df
