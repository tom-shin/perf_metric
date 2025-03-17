import sys
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import json
import chardet
from collections import OrderedDict
from PyQt5.QtCore import QThread, QCoreApplication


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
    def __init__(self, base_dir, q_lists, drive, gpt_xpath, source_result_file):
        super().__init__()

        self.running = True

        self.base_dir = base_dir
        self.q_list = q_lists
        self.edge_drive = drive
        self.chatbot_answer = []
        self.gpt_xpath = gpt_xpath
        self.filepath = source_result_file

        ret, self.json_result_data = json_load_f(file_path=self.filepath.replace("\\", "/"))

    def send_text_to_browser(self, question):
        """PyQt5에서 입력된 텍스트를 Edge 브라우저의 특정 필드에 입력 후 Enter 키 전달"""
        text_to_copy = question

        try:
            # 입력 필드가 나타날 때까지 기다림 (최대 10초)
            input_field = WebDriverWait(self.edge_drive, 60).until(
                EC.presence_of_element_located((By.XPATH, self.gpt_xpath["text_input"]))
            )
            input_field.clear()
            input_field.send_keys(text_to_copy)
            time.sleep(0.7)
            input_field.send_keys(Keys.RETURN)  # 'Enter' 키 입력

        except TimeoutException:
            print("Error: 입력 필드를 찾을 수 없습니다. 페이지 로딩을 확인하세요.")
        except NoSuchElementException as e:
            print(f"Error: Element not found - {e}")

    def get_web_data(self, cnt):
        """브라우저에서 특정 <p> 요소들의 내용을 가져와 출력"""
        start_time = time.time()  # 시작 시간 기록
        timeout = 3600  # 최대 대기 시간
        final_text = ""

        formular = 2 * cnt + 3

        k = 0
        while True:

            try:
                # 현재 시간 - 시작 시간이 timeout을 초과하면 종료
                if time.time() - start_time > timeout:
                    traceback.print_exc()  # 예외 상세 정보 출력
                    sys.exit(0)  # 프로그램 정상 종료 (0: 정상 종료)

                    # return final_text

                # self.xpath_gpt_answer 아래에 있는 <p> 태그 리스트 가져오기
                current_x_path = self.gpt_xpath["gpt_answer"].replace("ThunderSoft", str(formular))
                k += 1
                # print(current_x_path, k, formular)

                parent_element = self.edge_drive.find_element(By.XPATH, current_x_path)
                p_elements = parent_element.find_elements(By.TAG_NAME, "p")

                # <p> 태그가 하나 이상 존재하고, 적어도 하나의 <p>가 비어 있지 않다면 처리
                if p_elements and any(p.text.strip() for p in p_elements):
                    extracted_texts = [p.text.strip() for p in p_elements if p.text.strip()]

                    # # 가져올 텍스트를 필터링하는 로직 적용
                    # if len(extracted_texts) == 1:
                    #     final_text = extracted_texts[0]  # 1개면 그대로 사용
                    # elif len(extracted_texts) in [2, 3]:
                    #     final_text = extracted_texts[1]  # 2~3개면 두 번째 요소만 사용
                    # elif len(extracted_texts) >= 4:
                    #     final_text = "\n".join(extracted_texts[1:-1])  # 첫 번째와 마지막 제외
                    final_text = "\n".join(extracted_texts)

                    return final_text  # 성공적으로 데이터 가져왔으면 함수 종료

            except NoSuchElementException:
                pass  # 요소가 없으면 계속 확인

            QCoreApplication.processEvents()
            time.sleep(1)  # 1초 대기 후 다시 체크

    def run(self):
        try:

            # last_valid_idx = None  # 마지막으로 존재한 요소의 인덱스를 저장할 변수
            #
            # for idx in range(1, 1000):
            #     class_path = f"/html/body/div/div/div[2]/div/div/div[{idx}]"
            #
            #     try:
            #         input_field = self.edge_drive.find_element(By.XPATH, class_path)
            #         last_valid_idx = idx  # 마지막으로 찾은 유효한 idx 저장
            #     except NoSuchElementException:
            #         break  # 요소가 없으면 루프 종료

            # print("last_valid_idx",last_valid_idx)  # 마지막으로 존재한 idx만 출력

            total = self.q_list.count()
            for i in range(total):
                if not self.running:
                    # print("Terminated")
                    break

                text_to_copy = self.q_list.item(i).text()

                self.send_text_to_browser(question=text_to_copy)
                answer = self.get_web_data(i)
                self.chatbot_answer.append((text_to_copy, answer))

                print(f"[{i + 1}/{total}].  {text_to_copy}  : Done")
                self.single_data_merge(question=text_to_copy, answer=answer)
                time.sleep(1)

            # self.result_data_merge()
            print("\nFinished Chatbot Evaluation\n")

        except TimeoutException:
            print("Error: 입력 필드를 찾을 수 없습니다. 페이지 로딩을 확인하세요.")
        except NoSuchElementException as e:
            print(f"Error: Element not found - {e}")

    def single_data_merge(self, question, answer):
        #     self.chatbot_answer:
        # self.json_result_data
        # cnt = 0

        for data in self.json_result_data:
            # user_input 키에 해당하는 질문만 리스트에 추가
            if isinstance(data, dict) and "user_input" in data:
                if data["user_input"] == question:
                    data["chatbot_response"] = answer

        json_dump_f(file_path=self.filepath.replace("\\", "/"), data=self.json_result_data)

    def result_data_merge(self):
        #     self.chatbot_answer:
        # self.json_result_data
        # cnt = 0

        for chatbot in self.chatbot_answer:
            question = chatbot[0]
            answer = chatbot[1]

            for data in self.json_result_data:
                # user_input 키에 해당하는 질문만 리스트에 추가
                if isinstance(data, dict) and "user_input" in data:
                    if data["user_input"] == question:
                        data["chatbot_response"] = answer

        json_dump_f(file_path=self.filepath.replace("\\", "/"), data=self.json_result_data)

    def stop(self):
        self.running = False
        self.quit()
        self.wait(3000)
