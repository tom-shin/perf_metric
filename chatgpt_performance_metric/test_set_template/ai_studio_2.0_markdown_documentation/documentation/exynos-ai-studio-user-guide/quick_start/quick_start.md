# Quick Start

## Run docker container

```bash
docker run -it --gpus all --name eht_container \
-v {LOCAL_DATASET_DIR}:{CONTAINER_DATASET_DIR} \
eht:0.1.0
```

## Optimize sample model

```bash
python3 api.py -f /home/quick_start.yaml
```

```yaml
input_model_path: /home/sample/models/sample_add_constant.onnx
output_folder_path: /home/results_sample
input_model_format: onnx
model_type: CV

quantizer:
  precision_weight: 8
  precision_activation: 8
  calibration_data_path: /home/sample/datasets/add_constant
  use_cuda: True

simulator:
  metric: snr
  threshold: 100
  input_data_path: 
   /home/sample/datasets/add_constant

optimizer:
  skip_4_dim_conversion: False
  custom_template_path:
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/fuse_math_or_replace_DWConv.py:
    - TemplateFuseMath
```
