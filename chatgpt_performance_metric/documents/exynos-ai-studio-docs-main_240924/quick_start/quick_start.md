# Quick Start

## Run docker container

```bash
docker run -it --gpus all 
--name exynos_ai_studio_container \
-v {LOCAL_DATASET_DIR}:{CONTAINER_DATASET_DIR} \
exynos_ai_studio:0.1.0
```

## RUN tutorial

```bash
mkdir my_workspace
cp {CONTAINER_DATASET_DIR}/my_workspace.onnx my_workspace/
cd my_workspace
enntools init
```

```bash
mkdir my_workspace
cp {CONTAINER_DATASET_DIR}/dataset.h5 my_workspace/DATA/
```

modify config file and set mode

```bash
enntools conversion
```



