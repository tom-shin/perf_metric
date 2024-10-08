## Quick Start

To load an ONNX file, use:

```python
from model_editor import onnx_model
model = onnx_model.OnnxModel.load_model(<MODEL_PATH>)

for node in model.nodes:
    print(node) # print all nodes
```

To load an CNNX file, use:

```python
from model_editor import cnnx_model
model = cnnx_model.CnnxModel.load_model(<MODEL_PATH>, <ENCODINGS_PATH>)
for node in model.nodes:
    print(node) # print all nodes
```

## Creating a Model in Model Editor

1. Define a node and its inputs, outputs, and attributes.

```python
import numpy as np
from model_editor import onnx_model

input01 = onnx_model.OnnxInOut(
    name="input01",
    shape=[240, 240, 3],
    type=onnx_model.OnnxDtype.FLOAT,
)
input02 = onnx_model.OnnxInOut(
    name="input02",
    shape=[4],
    type=onnx_model.OnnxDtype.INT64,
    data=np.ndarray([1, 240, 240, 3], np.int64),
)
output01 = onnx_model.OnnxInOut(
    name="output01",
    shape=[1, 240, 240, 3],
    type=onnx_model.OnnxDtype.FLOAT,
)
attribute = onnx_model.OnnxAttribute(data=0, name="allowzero")
node = onnx_model.OnnxNode(
    name="node",
    op_type=onnx_model.OnnxOperator.Reshape,
    inputs=[input01, input02],
    outputs=[output01],
    attributes=[attribute],
)
```

The input and output of a node is defined using the `onnx_model.OnnxInOut` class. `OnnxInOut` has the following properties: name, shape, type, and data.
- `name` is the unique ID of the input and output.
- `type` is an enum from `onnx_model.OnnxDtype`.
- `data` is an np.ndarrary value.

The attribute of a node is defined using the `onnx_model.OnnxAttribute` class.

In `onnx_model.OnnxNode`, enter a `name`, `op_type`, `inputs`, `outputs` and `attributes`. `name` is the unique ID of the Node. `op_type` is an enum from `onnx_model.OnnxOperator`.

2. Define a graph and the corresponding model, and save the ONNX file.

```python
graph = onnx_model.OnnxGraph(
    name="graph",
    nodes=[node],
    inputs=[input01],
    outputs=[output01],
)
properties = onnx_model.OnnxProperties(
    ir_version=6,
    opset_import=[onnx_model.OperatorSetId("", 10)],
)
model = onnx_model.OnnxModel(
    graph=graph,
    properties=properties,
)
model.save_model("example.onnx")
```

## Nodes API

This section describes the API for editing graphs.

### append

```python
new_node = OnnxNode("new_node", op_type=OnnxOperator.Add, inputs=[...], outputs=[...])
model.nodes.append(new_node)
```

### extend

```python
new_node01 = OnnxNode("new_node01", op_type=OnnxOperator.Add, inputs=[...], outputs=[...])
new_node02 = OnnxNode("new_node02", op_type=OnnxOperator.Add, inputs=[...], outputs=[...])
model.nodes.extend([new_node01, new_node02])
```

### find

```python
find_node = model.nodes.find("node_name")
```

### remove

```python
find_node = model.nodes.find("node_name")
model.nodes.remove(find_node)
```

### replace

```python
find_node = model.nodes.find("node_name")
new_node01 = OnnxNode("new_node01", op_type=OnnxOperator.Add, inputs=[...], outputs=[...])
new_node02 = OnnxNode("new_node02", op_type=OnnxOperator.Add, inputs=[...], outputs=[...])
model.nodes.replace(find_node, [new_node01, new_node02])
```
