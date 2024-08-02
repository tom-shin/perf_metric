import json
import os
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import CharacterTextSplitter

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

    def load_txt(data_path):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            length_function=len,
            is_separator_regex=False,
        )

        with open(data_path, 'r') as file:
            data_string = file.read().split("\n")
            domain = os.path.splitext(os.path.basename(data_path))[0]
            metadata = [{"domain":domain} for _ in data_string]
            return text_splitter.create_documents(
                data_string,
                metadata
            )

    def dump_json(dump_data, dump_path):
        with open(dump_path, 'w+') as file:
            json.dump(dump_data, file, indent=4)


    def load_general(base_dir):
        data = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if ".txt" in file:
                    data += DataLoader.load_txt(os.path.join(root,file))

        return data
    
    def load_document(base_dir):
        data = []
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if ".md" in file:
                    data += DataLoader.load_markdown(os.path.join(root,file))

        return data