# **Backend API**

The backend API accepts inputs defined by schemas using Pydantic. When calling the API, you should create schema objects as described below.
## **Simulator**

### `run_inference`

**InferenceRunnerParameters schema details**

**input_model_path : string**

Specifies the file path of the input model. It should point to a file, not a parent folder.

---

**input_encondings_path : string**

Indicates the file path for the encodings file of the cnnx model.

---

**input_data_path : string**

Specifies the path to the folder containing data required for inference.

---

**use_cuda : bool**

Determines the inference method: when true, uses GPU for inference; when false, performs inference using CPU only.

---

**layerwise_check_name : list**

Accepts input values to retrieve intermediate featuremap information along with the output during inference. When featuremap names are provided, the inference runner's return value includes the values of those featuremaps appended.

---

**Example of run_inference API**

```python
from simulator.schema.base import InferenceRunnerParameters
from simulator.api import Simulator

params = InferenceRunnerParameters(
        input_model_path={input_model_path}
        input_encodings_path={input_encodings_path},
        input_data_path={input_data_path},
        )

res = Simulator.run_inference(params)
```

---

### `get_inference_session`


**GetInferenceSessionParameters schema details**

**input_model_path : string**

Specifies the file path of the input model. It should point to a file, not a parent folder.

---

**input_encondings_path : string**

Indicates the file path for the encodings file of the cnnx model.

---

**use_cuda : bool**

Determines the inference method: when true, uses GPU for inference; when false, performs inference using CPU only.

---
**Example of run_inference API**
```python
from simulator.schema.base import InferenceSessionParameters
from simulator.api import Simulator


params = InferenceSessionParameters(
        input_model_path={input_model_path}
        input_encodings_path={input_encodings_path},
        use_cuda={input_data_path},
        )

res = Simulator.get_inference_session(params)

```


---

### `compare_model_by_inference`

**InferenceCheckerParameters object details**

**input_model_path0 : string**

The onnx model file path to be compared.

---

**input_encondings_path_0 : string**

The model encodings file path for the onnx model 0.

---

**input_model_path_1 : string**

The onnx model file path to be compared.

---

**input_encondings_path_1 : string**

The model encodings file path for the onnx model 1.

---

**input_data_path : string**

Specifies the path to the folder containing data required for inference.

---

**meric : string**

Metric in which the error is calculated (“snr”, “rmse”, …)

---

**threshold : float**

The threshold by  which two models are considered as equivalent.

---

**use_cuda : bool**

Determines the inference method: when true, uses GPU for inference; when false, performs inference using CPU only.

---

**Example of compare_model_by_inference API**

```python
from simulator.schema.base import InferenceCheckerParameters
from simulator.api import Simulator

params = InferenceCheckerParameters(
            input_data_path = "/path/to/data/dir/",
            input_model_path_0 = "/path/to/model_0.onnx",
            input_encodings_path_0 = "/path/to/model_0.encodings",
            input_model_path_1 = "/path/to/model_1.onnx",
            input_encodings_path_1 = "/path/to/model_1.encodings",
            metric = "snr",
            threshold = 30,
            use_cuda = True
        )
res = Simulator.compare_model_by_inference(params)
```
