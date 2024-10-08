# Converter

Converter enables model conversion between various intermediate representations (IRs). Through this converter, users can apply the EHT module's optimization features to their PyTorch and TensorFlow models, and ultimately convert their optimized CNNX model into an SNC model.

This module consists of the four parts below:
- PyTorch2ONNX Converter
  - Converts (exports) a PyTorch model to ONNX.
  - Requires input dimension information:
    - Input shapes to export the model.
    - Dynamic axes to remain dynamic after the export. 
  - Requires an ONNX opset for exporting.
- TF2ONNX Converter (TBD)
  - This module is not released as of July; it is to be released.
  - Converts a TF (or TFLITE) model to ONNX.
- ONNX2CNNX Converter
  - Converts an ONNX model to CNNX.
  - Requires specification of both the output model path and the output encodings path.
- CNNX2SNC Converter
  - Converts a CNNX model to SNC.