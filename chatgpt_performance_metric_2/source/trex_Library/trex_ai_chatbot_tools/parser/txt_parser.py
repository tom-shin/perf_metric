from pandas import DataFrame
from trex_ai_chatbot_tools import InputType

def read_txt(path: str, id: str = None):
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    data = [[InputType.TXT, id, line, None, None, line] for line in lines]
    return DataFrame(
        data,
        columns=["InputType", "ID", "Data", "URL", "Section", "Content"]
    )

    