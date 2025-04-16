import json
from fastapi.responses import JSONResponse

APP_URL = "http://127.0.0.1:8000"


def json_response(output: dict) -> JSONResponse:
    return JSONResponse(json.loads(json.dumps(output, default=str)))
