from datetime import datetime, timezone
from itertools import islice
from openai import Stream
from openai.types.chat import ChatCompletionChunk
from pandas import DataFrame
from . import CACHE_SIM, CACHE_EQ
from ..embedding import get_embedding


class ChatData:
    def __init__(
        self,
        query: str = "",
        history: list[dict] = [],
        time: datetime = datetime.now(tz=timezone.utc),
    ) -> None:
        self._qe: list[float] = []
        self.base_dict: dict = {"query": query, "history": history, "asked": time}

    @property
    def query(self) -> str:
        return self.base_dict["query"]

    @property
    def history(self) -> list[dict]:
        return self.base_dict["history"]

    @history.setter
    def history(self, history: list[dict]):
        self.base_dict.update({"history": history})

    @property
    def qe(self) -> list[float]:
        if not self._qe:
            self._qe = get_embedding(self.query)
        return self._qe

    def set_mod(self, flagged: bool):
        self.dna = flagged

    def set_cache(
        self, cache: dict, score: float, conversation: str, embedding: list[float]
    ):
        self._qe = embedding
        self.cache_similar: bool = score < CACHE_SIM
        self.cache_equivalent: bool = score < CACHE_EQ
        self.cache_dict: dict = {
            "conversation": conversation,
            "cache": cache,
            "cache_score": score,
        }

    @property
    def cache(self) -> dict:
        return self.cache_dict["cache"]

    def set_context(
        self, df: DataFrame, c_list: list[str], context: str, relevancy: float
    ):
        self.df = df
        self.context_dict: dict = {
            "context": context,
            "list": c_list,
            "relevancy": relevancy,
        }

    @property
    def context(self) -> str:
        return self.context_dict["context"]

    def set_response(self, response: str):
        self._re = []
        self.ans_dict: dict = {"mode": "response", "response": response}

    def set_stream(self, stream: Stream[ChatCompletionChunk], cache: bool = False):
        self.strmode = True
        self.stream = stream
        self.cache_stream = cache
        self.standby = True

    async def get_stream(self):
        if not self.standby:
            raise SystemError("Stream is not set yet")
        self.standby = False
        if self.cache_stream:
            for chunk in self.stream:
                yield chunk
            self.ans_dict: dict = {"mode": "stream", "response": self.cache["response"]}
            return
        chunks = []
        for chunk in self.stream:
            delta = chunk.choices[0].delta.content
            if delta == None:
                break
            chunks.append(delta)
            yield delta
        usage = chunk.usage
        while not usage:
            usage = next(self.stream).usage
        self._re = []
        self.ans_dict: dict = {
            "mode": "stream",
            "response": "".join(chunks),
            "token": dict(islice(dict(usage).items(), 3)),
        }

    @property
    def check(self) -> bool:
        return not (self.df.empty and not self.cache_similar) and (
            "seed.ai@samsung.com" not in self.ans_dict["response"]
        )

    @property
    def re(self) -> list[float]:
        if not self._re:
            self._re = get_embedding(self.ans_dict["response"])
        return self._re

    def set_features(self, links: list[str], scores: list[tuple], img: dict):
        self.feat_dict: dict = {
            "hyperlinks": links,
            "link_scores": scores,
            "image": img,
        }

    def export(self) -> dict:
        if self.dna:
            return self.base_dict | {
                "success": False,
                "response": "Failed moderation check",
            }
        return (
            {"success": True}
            | self.base_dict
            | self.cache_dict
            | self.context_dict
            | self.ans_dict
            | self.feat_dict
            | {"embedding": self.qe}
        )
