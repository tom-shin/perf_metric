import os
import json
import time
import logging
import pandas as pd
from . import CONFIG, LAMBDA_ENV

if LAMBDA_ENV:
    LOG_DIR = ""
else:
    LOG_DIR = CONFIG["DEBUG"]["LOGGER"]
    os.makedirs(LOG_DIR, exist_ok=True)


def get_time() -> str:
    return f"{time.strftime('%Y/%m/%d %H:%M:%S')}:{int((time.time()%1)*10000):04d}"


class Log:
    def __init__(self, checklist: list[str], silent: bool = True):
        logging.basicConfig(
            filename=os.path.join(
                LOG_DIR,
                f"{get_time().replace('/','').replace(':','').replace(' ','')}.log",
            ),
            level=logging.INFO,
            format="[%(asctime)s] %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
        )
        self.total = len(checklist)
        self.task_list = checklist
        self._log_print = not silent

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, st: float):
        self._start = st
        self._end = None
        self._time = None

    @property
    def end(self) -> float:
        return self._end

    @end.setter
    def end(self, et: float):
        if self._end is not None:
            raise SystemError("Process has already ended. Start a new process.")
        self.write(f"End process at {get_time()}")
        self._end = et

    @property
    def time(self) -> float:
        if not self._time:
            if self.end is None:
                self.end = time.perf_counter()
            self._time = self._end - self.start
        return self._time

    def begin(self):
        self.time_list = [0.0] * self.total
        self.prev_step = -1
        self.write(f"Begin process at {get_time()}")

        self.start = time.perf_counter()
        self.prev = self.start

    def log(self, task: str):
        try:
            step = self.task_list.index(task)
        except:
            raise SystemError(
                "There are no steps left to log. Check the checklist and try again."
            )
        if step < self.prev_step:
            raise SystemError(
                f"{task} is trying to perform after {self.task_list[self.prev_step]} has already been performed. Check the checklist and try again."
            )
        now = time.perf_counter()
        elapsed = now - self.prev
        self.time_list[step] = elapsed
        self.write(
            f"Step {step+1}/{self.total} ({task}): {(elapsed):.4f}s/{(now-self.start):.4f}s"
        )
        self.prev_step = step
        if step + 1 == self.total:
            self.end = now
        else:
            self.prev = now

    def summary(self, result: dict):
        # Execution time
        if self.end is None:
            self.end = time.perf_counter()
        df = pd.DataFrame({"Task": self.task_list, "Time": self.time_list})
        df["Percentage"] = df["Time"].apply(lambda t: t * 100 / self.time)
        result.update({"ExecTime": df.to_dict("records")})
        # Query results
        for attr in ["context", "embedding"]:
            if result.get(attr):
                result.pop(attr)
        if result.get("cache"):
            result["cache"] = {
                k: result["cache"][k]
                for k in ["_id", "success", "query", "history", "asked", "conversation"]
            }
        self.write(json.dumps(result, default=str, indent=4))

    @property
    def log_print(self) -> bool:
        return self._log_print

    @log_print.setter
    def log_print(self, log_print: bool):
        self._log_print = log_print

    def toggle_log_print(self) -> bool:
        self._log_print = not self._log_print
        return self._log_print

    def write(self, text: str):
        if self.log_print:
            print(text)
        logging.info(text)
