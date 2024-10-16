import pandas as pd
import json
from ast import literal_eval
import trex_ai_chatbot_tools.embedding as emb
import trex_ai_chatbot_tools.text_gen as tg
import trex_ai_chatbot_tools.CSV_handler as ch
from . import error_filenotfound, token_size


def convert_df(q_df: pd.DataFrame) -> pd.DataFrame:
    """
    Use embeddings from e_df["Embedding"]

    Convert all questions from q_df[Question] column into content, save to q_df[Content] column

    Return modified df
    """
    for i, row in q_df.iterrows():
        e_df = tg.get_relevant_embeddings(tg.get_embedding(row["Question"]))
        q_df.loc[i, "Content"] = tg.generate_content(e_df)[0]
        print(f"\rGenerating content...({i+1}/{len(q_df)})", end="", flush=True)
    return q_df


def bulk_generate(answer_filter: float):
    with open(ch.DEBUG_INPUT) as f:
        questions = json.load(f)
    try:
        df = pd.read_csv(ch.EMBED_PATH)
    except:
        error_filenotfound("Embedding CSV", ch.EMBED_PATH)
        return
    df["Embedding"] = df["Embedding"].apply(literal_eval)
    for i, q in enumerate(questions):
        print(f"\rGenerating debug data...({i+1}/{len(questions)})", end="", flush=True)
        score = tg.get_relevant_embeddings(emb.get_embedding(q["Query"]), df).iloc[0][
            "CosineDist"
        ]
        q["CosineScore"] = score
        if score < answer_filter:
            answer = tg.answer_question(q["Query"], q.get("History", []))
            q["Answer"] = answer["response"]
            q["Links"] = answer["hyperlinks"]
    print()
    pd.DataFrame(questions).to_csv(ch.DEBUG_CSV, index=False)


def db_stats():
    try:
        df = pd.read_csv(ch.DOC_PATH)
    except:
        error_filenotfound("Documentation CSV", ch.DOC_PATH)
    df["Size"] = df["Data"].apply(token_size)
    print(df["Size"].describe())
    df = df.sort_values(by="Size", ascending=True)
    rank = 1
    text = ""
    for _, row in df.dropna(subset="Data").iterrows():
        text += f"Size rank: {rank} (Token size = {row['Size']})\n{row['Data']}\n"
        rank += 1
    with open("Output/DataSize.txt", "w") as f:
        f.write(text)
    print("MIN DATA:")
    print(df.loc[df["Size"].idxmin(), "Data"])
    print(df.head())
    df = df.sort_values(by="Size", ascending=False)
    print(df.head())
    print(df["Size"].sum())
    print("MAX DATA:")
    print(df.loc[df["Size"].idxmax(), "Data"])
    print(token_size(df["Data"].str.cat(sep=" ")))


def cosine_matrix():
    with open(ch.DEBUG_INPUT) as f:
        questions = json.load(f)
    df = pd.DataFrame(questions)
    df = emb.generate(df.dropna(subset="Query"), "Query")
    for i, qe in enumerate(df["Embedding"]):
        cosine_df = tg.get_relevant_embeddings(qe, df)
        df[i] = cosine_df["CosineDist"]
    df = df.drop(columns=["Embedding", "CosineDist"])
    df.to_csv("Output/q_matrix.csv", index=False)
