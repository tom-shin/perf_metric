import os
import pymongo
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns
from datetime import datetime

"""
<Usage Guide>

1. vv = VectorVisualizer(cursor)
2. 차원 축소 기법 선택
    2.1. vv.use_TSNE() => TSNE 선택 (default)
    2.2. vv.use_PCA() => PCA 선택택 

3. vv.demension_reduction() ==> 차원 축소
4. vv.generate_chart() ==> 차트 생성
5. vv.save_image() ==> 이미지로 저장
"""

class VectorVisualizer:
    DEFAULT_CHART_SAVE_IMAGE_NAME = "MongoVectorEmbeddingsVisualization.png"

    support_demension_reduction_rule = ["TSNE", "PCA"]
    use_demension_reduction_rule = 0

    vector = None
    ids = None
    embeddings = None
    reduced_embeddings = None
    color_map = None
    plt = None

    def __init__(self, vector:list):
        self.vector = [(document["ID"], np.array(document["Embedding"])) for document in vector]

    def set_vector(vector:list):
        clear()
        self.vector = [(document["ID"], np.array(document["Embedding"])) for document in vector]
        
    def use_TSNE(self):
        self.__choice_demension_reduction_rule("TSNE")

    def use_PCA(self):
        self.__choice_demension_reduction_rule("PCA")

    def demension_reduction(self):
        self.ids, self.embeddings = self.__split_id_embedding(self.vector)
        
        rule = self.support_demension_reduction_rule[self.use_demension_reduction_rule]
        self.reduced_embeddings = self.__reducer(self.embeddings, rule)

    def generate_chart(self):
        unique_ids = list(set(self.ids))
        self.color_map = self.__id_color_mapping(unique_ids)
        self.plt = self.__generate_chart(
            reduced_embeddings=self.reduced_embeddings, 
            color_map=self.color_map, 
            ids=self.ids, 
            unique_ids=unique_ids)

    def save_image(self, output_file=datetime.today().strftime('%Y%m%d%H%M%S_') + DEFAULT_CHART_SAVE_IMAGE_NAME):
        self.plt.savefig(output_file, dpi=300, bbox_inches="tight")
        self.plt.close()

    def show_image(self):
        self.plt.show()

    def __choice_demension_reduction_rule(self, demension_reduction_name:str):
        self.use_demension_reduction_rule = self.support_demension_reduction_rule.index(demension_reduction_name)

    def __split_id_embedding(self, vector):
        ids, embeddings = zip(*vector)
        embeddings = np.vstack(embeddings)
        return ids, embeddings

    def __reducer(self, embeddings:list, rule:str):
        if rule == "TSNE":
            reducer = TSNE(n_components=2, random_state=42)
        elif rule == "PCA":
            reducer = PCA(n_components=2)
        else:
            raise TypeError("It is not support_demension_reduction_rule")

        return reducer.fit_transform(embeddings)

    def __id_color_mapping(self, unique_ids:list):
        palette = sns.color_palette("hsv", len(unique_ids))
        color_map = {uid: palette[i] for i, uid in enumerate(unique_ids)}
        return color_map

    def __generate_chart(self, reduced_embeddings:list, color_map:dict, ids:list, unique_ids:list):
        colors = [color_map[uid] for uid in ids]

        plt.figure(figsize=(10, 8))
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1],
                    c=colors, alpha=0.7, edgecolors="k")
        
        for uid in unique_ids:
            plt.scatter([], [], c=[color_map[uid]], label=str(uid))
        plt.legend(title="ID", bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.title("MongoDB Vector Embeddings Visualization")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.grid(True)
        return plt

    def get_reducer_embedding():
        return self.reduced_embeddings

    def get_ids():
        return self.ids

    def get_color_map():
        return self.color_map

    def clear(self, force=False):
        self.ids = None
        self.embeddings = None
        self.reduced_embeddings = None
        self.color_map = None
        self.use_demension_reduction_rule = 0
        
        if force:
            self.vector = None
