import subprocess
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

import logging
import easygui
import site
import shutil
import ctypes
import chardet
import json
from collections import OrderedDict
from datetime import datetime
import pytz
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PyQt5.QtCore import pyqtSignal, QObject, QProcess
from PyQt5 import QtWidgets, QtCore, QtGui

import pandas as pd
import os

output_file = "output_file.md"

with open("../TestSet_Fail.txt", "r", encoding="utf-8") as f_p:
    datas = f_p.readlines()

cnt = 0
with open(output_file, "w", encoding="utf-8") as out_f:
    for file in datas:
        file = file.strip().strip("'\"")  # 개행 + 따옴표 제거
        if ".md" in file or ".txt" in file:
            n_path = file.replace("\\", "/")
            try:
                size = os.path.getsize(n_path)
                if size > 0:
                    with open(n_path, "r", encoding="utf-8") as f:
                        cnt += 1
                        content = f.read()
                        # out_f.write(f"# 파일: {n_path}\n")  # 파일명 주석 추가 (선택)
                        out_f.write(content)
                        out_f.write("\n\n")  # 파일 구분용 빈 줄
            except Exception as e:
                print(f"오류 발생 - 파일: {n_path}, 오류: {e}")

print(cnt)
