

## Usage
```
usage:

1. module_install.bat 실행

2. cli mode에서 local_models로 이동하여 model_download.py 실행

3. [선택 사항]
   - configuration 아래 model_config.py를 열면 Models가 있는데 필요 없는 것은 # 처리 한다.
     ; 이 파일에서 주석처리 하면 main.py 실행 시 main gui의 metric 항목에 display가 되지 않는다.
       물론 아래 모든 Models 항목에서 주석 처리하지 않으면 main gui에서 아래 모든 항목이 보이게 되고
       해당 항목에서 check 활성화/ 비활성화를 해도 된다.
       아래처럼 항목을 가져간 이유는 혹시 모를 요청 사항이 있을 때 조금씩 우리 쪽에서 릴리즈 속도 조절을 위함.

     Models = {
    "all-MiniLM-L6-v2": None,
    # "all-mpnet-base-v2": None,
    "paraphrase-MiniLM-L6-v2": None,
    ....
     }

4. Refresh 버턴을 눌러 준다
   : scenario 폴더 안에 있는 scenarios.json 파이을 읽어와 위젯을 구성 함

5. 테스트할 Scenario 및 테스트 진행 할 Metric 선택

6. Analyze 버턴으로 실행

7. 평가 종료 후 Save 버턴으로 결과 저장
   
```
