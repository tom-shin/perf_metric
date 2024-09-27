# **Frontend API**

### `optimize`

An api that takes models such as onnx, cnnx as input, processes them through modules including optimization, quantization, simulator, and converter, and outputs an snc model.

### **optimization yaml file**

The optimization file contains optimization information. It allows you to set the locations of input and output models and detailed configurations for each module. Optimization is performed differently depending on the model type.

### **Detailed explanation for optimization yaml file**

---

**input_model_path : string**

Specify the file path of the input model. You must specify the file, not the parent folder.

---

**output_folder_path : string**

This is the path where the output will be saved.

---

**model_type : string**

Specify the type of the input model. Optimization is performed differently depending on the model type, with details as follows

- CV
- LVM
- LLM

---

**quantizer : dict**

- **precision_weight : int** : precision of weight
- **precision_activation : int** : precision of activation
- **mpq_operator_dict : dict** : When performing mixed precision quantization, input the operators and precision to be quantized with a precision different from the values specified in precision_weight and precision_activation above.
- **alpha : float** : smoothquant migration strength
- **calibration_data_path : string** : The path to the representative data to be used for calibration
- **calibration_args : dict :** Arguments for processing calibration
  - **samples : int** : How many calibration data samples to use
  - **seed : int** : A value set as a seed for random selection

---

**simulator : dict**

- **metric : string**: The metric to be used for measurement
- **threshold : float** : The threshold value of the metric that determines agreement / disagreement
- **input_data_path : string**: The path to the dataset for model inference

---

**optimizer : dict**

- **skip_4_dim_conversion : bool** : If true, it does not convert to 4 dimensions before optimization; if false, it proceeds with the conversion.
- **overwrite_input_shapes : dict** : Enter the input shape for models with undefined input shapes.
- **custom_template_path : dict**: Enter the templates to apply for optimization. Use the path of the Python file containing the template as the key, and the template within it as the value.

### **How to use optimization API**

Execute by putting the path to the file written above in the -f option

```bash
python3 api.py -f sample.yaml
```

[**CV sample yaml**](../model_optimization_flow/model_optimization_flow.md#cv)

```yaml
input_model_path: {INPUT_MODEL_PATH}
output_folder_path: {OUTPUT_MODEL_PATH}
input_model_format: onnx
model_type: CV

quantizer:
  precision_weight: 8
  precision_activation: 8
  calibration_data_path: {CALIBRATION_DATA_PATH}

simulator:
  metric: snr
  threshold: 100
  input_data_path: 
    {INPUT_DATA_PATH}

optimizer:
  skip_4_dim_conversion: False
  custom_template_path:
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_prelu.py:
    - TemplateFoldingPrelu
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_eltwise_concat_conv.py:
    - TemplateReplaceEltwise
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/insert_dwconv_for_act_fold.py:
    - TemplateInsertDWConvForActFold
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/fuse_deconv_bias.py:
    - TemplateFuseDeconvBias
  
```

[**LVM sample yaml**](../model_optimization_flow/model_optimization_flow.md#lvm)

```yaml
input_model_path: {INPUT_MODEL_PATH}
output_folder_path: {OUTPUT_FOLDER_PATH}
model_type: LVM
input_model_format : onnx

quantizer:
  precision_weight: 8
  precision_activation: 8
  alpha: 1.0
  mpq_operator_dict:
    Softmax: int16
  calibration_data_path: {CALIBRATION_DATA_PATH}
  calibration_args:
    reduction: absmax 
    samples: 2
    seed: 42

simulator:
  metric: snr
  threshold: 100
  input_data_path: 
    {INPUT_DATA_PATH}

optimizer:
  skip_4_dim_conversion: False
  overwrite_input_shapes:
    sample : [3,8,64,64]
    timestep : [1]
    encoder_hidden_states: [3, 77, 768]
  custom_template_path:
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_groupnorm.py: 
      - TemplateFoldingGroupNorm
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_silu.py: 
      - TemplateFoldingSiLU
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_layernorm.py: 
      - TemplateFoldingLayerNorm
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_geglu.py: 
      - TemplateFoldingGeGLU
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_matmul2dynamicConv.py:
      - TemplateReplaceMatmulToDynamicConv
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_slice2split.py: 
      - TemplateReplaceSlice2Split 
```

[**LLM Sample yaml**](../model_optimization_flow/model_optimization_flow.md#llm)

```yaml
input_model_path: {INPUT_MODEL_PATH}
input_encodings_path: {INPUT_ENCODINGS_PATH}
output_folder_path: {OUTPUT_FOLDER_PATH}
input_model_format: onnx
model_type: LLM

simulator:
  input_data_path: {INPUT_DATA_PATH}
  metric: snr
  threshold: 100

optimizer:
  skip_4_dim_conversion: False
  custom_template_path:
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/folding_rmsnorm.py: 
     - TemplateFoldingRMSNorm
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/fuse_cast.py: 
     - TemplateFuseCast
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/fuse_math_or_replace_DWConv.py: 
     - TemplateFuseMath
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_eltwise_concat_conv.py: 
     - TemplateReplaceEltwise
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_expand_to_concat.py:
     - TemplateReplaceExpandToConcat
    /usr/local/lib/python3.10/dist-packages/optimizer/core/templates/replace_matmul2dynamicConv.py:
     - TemplateReplaceMatmulToDynamicConv
```
