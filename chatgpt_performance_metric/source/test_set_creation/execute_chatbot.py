import sys
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import json
import chardet
from collections import OrderedDict
import datetime
import tiktoken
import traceback  # 맨 위에 추가

from PyQt5.QtCore import QThread, QCoreApplication, QMutex, QWaitCondition


def json_load_f(file_path, use_encoding=False):
    if file_path is None:
        return False, False

    if use_encoding:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
    else:
        encoding = "utf-8"

    with open(file_path, "r", encoding=encoding) as f:
        json_data = json.load(f, object_pairs_hook=OrderedDict)

    return True, json_data


def json_dump_f(file_path, data, use_encoding=False, append=False):
    if file_path is None:
        return False

    if not file_path.endswith(".json"):
        file_path += ".json"

    if use_encoding:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
    else:
        encoding = "utf-8"

    if append:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)  # 기존 데이터 로드
        else:
            existing_data = []  # 파일이 없거나 비어있으면 빈 리스트로 초기화

        # 새로운 데이터 추가
        if isinstance(existing_data, list):
            existing_data.append(data)  # 리스트라면 추가
        elif isinstance(existing_data, dict):
            existing_data.update(data)  # 딕셔너리라면 업데이트

        # JSON 파일에 다시 저장 (덮어쓰기)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
    else:
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=False)

    return True


class ChatBotGenerationThread(QThread):
    def __init__(self, base_dir, q_lists, drive, gpt_xpath, source_result_file, startIdx=0):
        super().__init__()

        self.running = True
        self.suspended = False

        self.base_dir = base_dir
        self.q_list = q_lists
        self.edge_drive = drive
        self.chatbot_answer = []
        self.gpt_xpath = gpt_xpath
        self.filepath = source_result_file
        self.start_idx = int(startIdx)

        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

        ret, self.json_result_data = json_load_f(file_path=self.filepath.replace("\\", "/"))

    def send_text_to_browser(self, question):
        try:
            input_field = WebDriverWait(self.edge_drive, 60).until(
                EC.presence_of_element_located((By.XPATH, self.gpt_xpath["text_input"]))
            )
            input_field.clear()
            input_field.send_keys(question)
            time.sleep(0.7)
            input_field.send_keys(Keys.RETURN)
        except TimeoutException:
            print("Error: 입력 필드를 찾을 수 없습니다. 페이지 로딩을 확인하세요.")
        except NoSuchElementException as e:
            print(f"Error: Element not found - {e}")

    def get_web_data(self, cnt):
        start_time = time.time()
        timeout = 3600
        final_text = ""

        formular = 2 * cnt + 3

        while True:
            self.check_pause()  # <<<< 일시중지 상태 체크

            try:
                if time.time() - start_time > timeout:
                    traceback.print_exc()
                    sys.exit(0)

                current_x_path = self.gpt_xpath["gpt_answer"].replace("ThunderSoft", str(formular))
                parent_element = self.edge_drive.find_element(By.XPATH, current_x_path)
                p_elements = parent_element.find_elements(By.TAG_NAME, "p")

                if p_elements and any(p.text.strip() for p in p_elements):
                    extracted_texts = [p.text.strip() for p in p_elements if p.text.strip()]
                    final_text = "\n".join(extracted_texts)
                    return final_text

            except NoSuchElementException:
                pass

            QCoreApplication.processEvents()
            time.sleep(1)

    def run(self):
        try:
            total = self.q_list.count()
            answer = ''
            text_to_copy = ""
            token_count = 0
            enc = tiktoken.get_encoding("cl100k_base")  # 밖에서 한 번만 호출
            xpath_start = 0

            for i in range(total):

                if not self.running:
                    break

                if i < self.start_idx:
                    continue

                text_to_copy = self.q_list.item(i).text()
                print(f"Send: {text_to_copy}")
                self.send_text_to_browser(question=text_to_copy)

                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Send 완료 및 답변 대기 시작: {formatted_time}")

                s = time.time()
                answer = self.get_web_data(xpath_start)
                xpath_start += 1

                # 질문 + 답변 쌍만 토큰화하여 누적
                combined_text = f"Q: {text_to_copy}\nA: {answer}"
                tokens = enc.encode(combined_text)
                pair_token_count = len(tokens)
                token_count += pair_token_count

                with open("accumulated_text.txt", "a+", encoding="utf-8") as file:
                    file.write(combined_text)

                print(
                    f"[{i + 1}/{total}].  Chatbot 답변 완료:   {round(time.time() - s, 2)} sec.   이번 쌍 토큰 수: {pair_token_count}, 누적 토큰 수: {token_count}\n\n")

                self.chatbot_answer.append((text_to_copy, answer))

                self.single_data_merge(question=text_to_copy, answer=answer)

                self.check_pause()  # <<<< 일시중지 상태 체크

                QCoreApplication.processEvents()

                time.sleep(2)

            print("\nFinished Chatbot Evaluation\n")

        except TimeoutException:
            print("Error: 입력 필드를 찾을 수 없습니다. 페이지 로딩을 확인하세요.")
            traceback.print_exc()  # <<< 여기에 추가
        except NoSuchElementException as e:
            print(f"Error: Element not found - {e}")
            traceback.print_exc()  # <<< 여기에 추가

    def check_pause(self):
        """Suspend 상태일 경우 대기"""
        self.mutex.lock()
        while self.suspended:
            self.pause_condition.wait(self.mutex)
        self.mutex.unlock()

    def suspend(self):
        """일시중지"""
        self.mutex.lock()
        self.suspended = True
        self.mutex.unlock()
        print("Thread suspended.")

    def resume(self):
        """재개"""
        self.mutex.lock()
        self.suspended = False
        self.mutex.unlock()
        self.pause_condition.wakeAll()
        print("Thread resumed.")

    def get_current_status(self):
        return self.running

    def stop(self):
        self.running = False
        self.resume()  # 중지시 일시중지 상태라도 해제해야 종료 가능
        self.quit()
        self.wait(3000)

    def single_data_merge(self, question, answer):
        for data in self.json_result_data:
            if isinstance(data, dict) and "user_input" in data:
                if data["user_input"] == question:
                    data["chatbot_response"] = answer

        json_dump_f(file_path=self.filepath.replace("\\", "/"), data=self.json_result_data)

    def result_data_merge(self):
        for question, answer in self.chatbot_answer:
            for data in self.json_result_data:
                if isinstance(data, dict) and "user_input" in data:
                    if data["user_input"] == question:
                        data["chatbot_response"] = answer

        json_dump_f(file_path=self.filepath.replace("\\", "/"), data=self.json_result_data)
