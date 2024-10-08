# Model Requirements and Constraints

### CNNX model
CNNX model consists of ONNX model and encodings file. Encodings file should contain quantization information and optimization module information according to the given ONNX model in json format.
Example for encodings file is shown below:

```json
{
    "activation_encodings": {
        "/act/a0": [
            {
                "bitwidth": 8,
                "dtype": "int",
                "is_symmetric": "False",
                "max": 0.0,
                "min": 0.0,
                "offset": 0,
                "scale": 0.0
            }
        ],
        "/act/a1": [
            {
                ...
            }
        ],
        "/act/b": [
            {
                ...
            }
        ]      
    },
    "param_encodings": {
        "/param/A0": [
            {
                ...
            }
        ],
        "/param/A1": [
            {
                ...
            }
        ],
        "/param/B0": [
            {
                ...
            }
        ]
    },
    "quantizer_args": {
        "activation_bitwidth":8,
        "dtype": "int",
        "is_symmetric": true,
        "param_bitwidth":8,
        "per_channel_quantization": false,
        "quant_scheme": "post_training_tf_enhanced"
    },
    "version": "0.6.1",
    "modules": {
        "LayerNorm_1": 
        {
            "SNC_OP": "LayerNorm",
            "SNC_params": 
            {
                "param0": 0,
                "param1": 1
            },
            "Elements":
            {
		            "input": [...]
                "activations":["/act/a0",  "/act/a1"],
                "params": ["/param/A0", "/param/A0", "/param/B0"]
                "output": [...],
                "nodes": [...],
                "prev_nodes": [...],
                "next_nodes": [...]
            }
        },
        "LayerNorm_2": 
        {
            "SNC_OP": "LayerNorm",
            "SNC_params": 
            {
                "param0": 0,
                "param1": 1
            },
            "Elements":
            {
		            "input": [...],
                "activations":["/act1/a0",  "/act1/a1"],
                "params": ["/param1/A0", "/param1/A0", "/param1/B0"],
                "output": [...],
                "nodes": [...],
                "prev_nodes": [...],
                "next_nodes": [...]
            }
        },
        "BatchNorm_1": 
        {
            "SNC_OP": "BatchNorm",
            "SNC_params": 
            {
                "param0": 0,
                "param1": 1
            }
        }
    }
}
```

#### activation encodings & param encodings
Encodings information for quantization is given as a json data. For each ONNX activation & params name, bitwidth, dtype, and quantization parameters(min, max, offset, scale, is_symmetric) are given in this part.

#### quantizer_args
Global quantization information is given on this part including per_channel_quantization and quantization scheme.

#### modules
Module information after EHT optimizer is given on this part. Under the module name as a key, SNC layer information(SNC_OP, SNC_params) and ONNX element related to the module(Elements) are given.

### model format

- Model should be prepared in CNNX or ONNX format to start optimization.
- ONNX file should be converted into CNNX format using converter module.
  - EHT accepts ONNX external data for tensors. External data files should be in the same directory as the [.onnx] file.
  - The [.onnx] file size is limited to 2GB. For files larger than 2GB, the model should be saved using external data format.

### opset version

- EHT currently support ONNX opset version ≤ 18, but ≤ 16 for stable usage.
