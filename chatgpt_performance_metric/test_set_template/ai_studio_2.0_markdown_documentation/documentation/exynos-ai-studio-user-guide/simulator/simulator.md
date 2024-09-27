# Simulator

Simulator conducts inference on a CNNX model, which contains an ONNX model file and a quantization information encodings file. It can check output and intermediate tensors during execution. 

Quantized inference is performed using *simulated quantization*. Simulated quantization provides the capability to mimic the effects of quantized operations. Floating point values are clipped and divided into several ranges, and values within each range are converted to the same value, simulating the quantization process.

Simulator includes the following features:
  - `get_quantization_sim`: Attain a CNNX quantization simulation session for manual run.
  - `load_input_data`: Load the input data from the given dataset path.
  - `run_inference`: Conduct inference on a CNNX model.
  - `compare_model_by_inference`: Compare two CNNX models on their inference outputs. Currently, the SNR value is used for the comparison metric.
  - `compare_model_by_layer` (TBD): Compare two CNNX models on intermediate tensors for each layer. To be released.
