# Simulator

Simulator conducts inference on a CNNX model, which contains an ONNX model file and a quantization information encodings file. It can check output and intermediate tensors during execution. 

Quantized inference is performed using *simulated quantization*. Simulated quantization provides the capability to mimic the effects of quantized operations. Floating point values are clipped and divided into several ranges, and values within each range are converted to the same value, simulating the quantization process.

Simulator includes the following features(with example codes):
  - `get_quantization_sim`: Attain a CNNX quantization simulation session for manual run.
```python
from simulator imoprt api
output_names = [LIST_OF_ONNX_OUTPUTS]
input_dict = {"input_0": NUMPY_ARRAY_0, "input_1": NUMPY_ARRAY_1]
quantsim = api.get_quantization_sim(params)
inference_session = quantsim.session
result = session.run(output_names, input_dict)
print(result)
```

  - `load_input_data`: Load the input data from the given dataset path.

  - `run_inference`: Conduct inference on a CNNX model.

  - `compare_model_by_inference`: Compare two CNNX models on their inference outputs. Currently, the SNR value is used for the comparison metric.

  - `compare_model_by_layer` : Compare two CNNX models on intermediate tensors for each layer.
```python
from simulator imoprt api

    params = api.LayerwiseCheckerParameters(
        input_data_path = "/path/to/input/data/,
        input_model_path_0 = "/path/to/model/0.onnx",
        input_encodings_path_0 = "/path/to/model/0.encodings",
        input_model_path_1 = "/path/to/model/0.onnx",
        input_encodings_path_1 = "/path/to/model/0.encodings",
        metric = "snr",
        threshold = 100,
        use_cuda = False,
        layer_match_info = [("featuremap_0", "featuremap_0"), ("featuremap_1","featuremap_1")]
        export_featuremap = True,
        export_featuremap_path = "/path/to/save/exported/featuremap"
    )
    res = api.compare_model_by_layer(params)
    print("Layerwise check")
    for input_name, result in res.items():
        _, result_dict = result
        for output_name, snr_value in result_dict.items():
            print(f"{output_name}: {snr_value}")
```
