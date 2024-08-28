FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY ./library ${LAMBDA_TASK_ROOT}/library
RUN pip install library/.

COPY ./lambda_function.py ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.handler" ]
