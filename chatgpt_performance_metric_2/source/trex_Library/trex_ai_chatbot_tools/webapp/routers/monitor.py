from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pandas import DataFrame
from .. import APP_URL, json_response
from ...database import log_col

MONITOR_HANDLER = "/monitor"
router = APIRouter(prefix=MONITOR_HANDLER)
MONITOR_URL = APP_URL + MONITOR_HANDLER


@router.get("/keys", response_class=JSONResponse)
def get_keys():
    log = log_col.find_one({})
    if log:
        return json_response(list(log.keys()))
    return json_response([])


@router.get("/exectime", response_class=JSONResponse)
def get_times():
    logs = log_col.find({})
    if not logs:
        return json_response([])
    df = DataFrame(logs)
    return json_response(df["ExecTime"].to_dict())
