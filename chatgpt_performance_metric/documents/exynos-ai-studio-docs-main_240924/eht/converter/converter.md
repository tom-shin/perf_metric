# Converter

Converter enables model conversion between various intermediate representations (IRs). Through this converter, users can apply the EHT module's optimization features to their PyTorch and TensorFlow models, and ultimately convert their optimized CNNX model into an SNC model.

This module consists of the four parts below:
- PyTorch2ONNX Converter
  - Converts (exports) a PyTorch model to ONNX.
  - Requires input dimension information:
    - Input shapes to export the model.
    - Dynamic axes to remain dynamic after the export. 
  - Requires an ONNX opset for exporting.
- TF2ONNX Converter
  - Converts a TF (or TFLITE) model to ONNX.
  - Requires an ONNX opset for exporting.
- ONNX2CNNX Converter
  - Converts an ONNX model to CNNX.
  - Requires specification of both the output model path and the output encodings path.
- CNNX2SNC Converter
  - Converts a CNNX model to SNC.


Example codes to use them:
```python
from converter import api
cnnx_to_snc_params = api.Cnnx2SncParameters(
    input_model_path = "/path/to/model.onnx",
    input_encodings_path = "/path/to/model.encodings",
    output_model_path = "/output/path/for/model.snc"
    )

api.Converter.cnnx_to_snc(cnnx_to_snc_params)

tflite_to_onnx_params = api.TfLite2OnnxParameters(
    input_model_path = "/path/to/model.tflite",
    output_model_path = "./output/path/for/model.onnx",
    )

api.Converter.tflite_to_onnx(tflite_to_onnx_params)
```
