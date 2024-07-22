import json
from langchain_text_splitters import MarkdownHeaderTextSplitter

class DataLoader:
    def load_json(data_path):
        with open(data_path, 'r') as file:
            data = json.load(file)

        return data
    
    def load_markdown(data_path):
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )


        with open(data_path, 'r') as file:
            data_string = file.read()
            return markdown_splitter.split_text(data_string)
            

    def dump_json(dump_data, dump_path):
        with open(dump_path, 'w+') as file:
            json.dump(dump_data, file, indent=4)