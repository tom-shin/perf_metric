

## Usage
```
docker run -it --name ragas --gpus all \
    -v /dir/to/perf_metric:/workspace \
    -v /dir/to/ollama:/root/.ollama \
    nvcr.io/nvidia/pytorch:24.06-py3
```
```
usage: cli.py [-h] -m MODEL_DIR -d DATA_DIR TEST_NAME [TEST_NAME ...]

Test Chatbot

positional arguments:
  TEST_NAME             a test to run

options:
  -h, --help            show this help message and exit
  -m MODEL_DIR, --model_dir MODEL_DIR
                        the location of test models
  -d DATA_DIR, --data_dir DATA_DIR
                        the location of test data
```
