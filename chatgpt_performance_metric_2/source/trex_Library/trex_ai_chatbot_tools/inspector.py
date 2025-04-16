import os
import json
import time
import logging
import pandas as pd
from . import CONFIG, LAMBDA_ENV, str_time

if LAMBDA_ENV:
    LOG_DIR = ""
else:
    LOG_DIR = CONFIG["DEBUG"]["LOGGER"]
    os.makedirs(LOG_DIR, exist_ok=True)


class Log:
    def __init__(self, checklist: list[str], silent: bool = True):
        logging.basicConfig(
            filename=os.path.join(LOG_DIR, f"{str_time(True)}.log"),
            level=logging.INFO,
            format="[%(asctime)s] %(message)s",
            datefmt="%Y/%m/%d %H:%M:%S",
        )
        self.total = len(checklist)
        self.task_list = checklist
        self.silent = silent

    @property
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, st: float):
        self._start: float = st
        self._end: float = None
        self._time: float = None
        self.stopwatch: dict[str, list] = None
        self.categories: dict[str, list] = {}

    @property
    def end(self) -> float:
        return self._end

    @end.setter
    def end(self, et: float):
        if self._end is not None:
            raise SystemError("Process has already ended. Start a new process.")
        self.write(f"End process at {str_time()}")
        self._end = et

    @property
    def time(self) -> float:
        if not self._time:
            if self.end is None:
                self.end = time.perf_counter()
            self._time = self.end - self.start
        return self._time

    def begin(self):
        self.time_list = [0.0] * self.total
        self.prev_step = -1
        self.write(f"Begin process at {str_time()}")

        self.start = time.perf_counter()
        self.prev = self.start

    def log(self, task: str):
        try:
            step = self.task_list.index(task)
        except:
            raise SystemError(
                f"Task [{task}] doesn't exist. Check the checklist and try again."
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

    def start_watch(self, id: str):
        if self.stopwatch:
            raise SystemError(
                "A category is already being watched. Only one category can be watched at a time."
            )
        if self.categories.get(id) == None:
            self.categories[id] = []
        self.stopwatch = {"id": id, "time": time.perf_counter()}

    def stop_watch(self):
        process = time.perf_counter() - self.stopwatch["time"]
        self.write(f"External call ({self.stopwatch['id']}): {process}")
        if not self.stopwatch:
            raise SystemError("The stopwatch hasn't started.")
        self.categories[self.stopwatch["id"]].append(process)
        self.stopwatch = None

    def summary(self):
        if self.end is None:
            self.end = time.perf_counter()
            self.time_list[self.prev_step] += self.end - self.prev
        result = {
            "Tasks": {
                task: {
                    "Time": self.time_list[i],
                    "Percentage": self.time_list[i] * 100 / self.time,
                }
                for i, task in enumerate(self.task_list)
            }
        }
        df = pd.DataFrame(result["Tasks"]).T
        df.loc["Total"] = df.sum()
        self.write(df)
        if self.categories:
            categories = {}
            for tag, times in self.categories.items():
                categories[tag] = sum(times)
            ext_time = sum([t for _, t in categories.items()])
            result["Categories"] = {
                "Summary": {
                    "Total_time": self.time,
                    "External_time": ext_time,
                    "Internal_time": self.time - ext_time,
                    "External_percentage": ext_time * 100 / self.time,
                },
                "Categories": {
                    item: {
                        "Calls": len(self.categories[item]),
                        "Time_total": data,
                        "Time_average": data / len(self.categories[item]),
                        "Percentage": data * 100 / ext_time,
                    }
                    for item, data in categories.items()
                },
            }
            self.write(
                json.dumps(result["Categories"]["Summary"], default=str, indent=4)
            )
            self.write(pd.DataFrame(result["Categories"]["Categories"]).T.sort_index())
        return result

    def write(self, text: str):
        if not self.silent:
            print(text)
        logging.info(text)

    def quiet_log(self, text: str):
        logging.info(text)
