import asyncio
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from .. import APP_URL, json_return
from ...generator.ChatData import ChatData
from ...text_gen import answer_question, post_generation

STREAM_HANDLER = "/stream"
router = APIRouter(prefix=STREAM_HANDLER)
STREAM_URL = APP_URL + STREAM_HANDLER
queue = asyncio.Queue()


class QueryObj(BaseModel):
    query: str
    history: list[dict] = []


async def response_stream(data: ChatData):
    async for chunk in data.get_stream():
        yield chunk
    await queue.put(post_generation(data))


@router.post("/chat", response_class=StreamingResponse)
async def post_answer_stream(qobj: QueryObj):
    return StreamingResponse(
        response_stream(answer_question(qobj.query, qobj.history, True))
    )


@router.get("/result", response_class=JSONResponse)
async def get_result():
    try:
        result = await asyncio.wait_for(queue.get(), timeout=10)
        return json_return(result)
    except asyncio.TimeoutError:
        raise HTTPException(404, "No result found in history")
