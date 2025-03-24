from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pandas import DataFrame
from .. import APP_URL, json_return
from ...database import log_col

MONITOR_HANDLER = "/monitor"
router = APIRouter(prefix=MONITOR_HANDLER)
MONITOR_URL = APP_URL + MONITOR_HANDLER


@router.get("/keys", response_class=JSONResponse)
def get_keys():
    log = log_col.find_one({})
    if log:
        return json_return(list(log.keys()))
    return json_return([])


@router.get("/exectime", response_class=JSONResponse)
def get_times():
    logs = log_col.find({})
    if not logs:
        return json_return([])
    df = DataFrame(logs)
    return json_return(df["ExecTime"].to_dict())
