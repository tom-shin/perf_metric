FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY ./library/dist/evaltools-0.0.2-py3-none-any.whl ${LAMBDA_TASK_ROOT}
RUN pip install evaltools-0.0.2-py3-none-any.whl

COPY ./lambda_function.py ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.handler" ]
