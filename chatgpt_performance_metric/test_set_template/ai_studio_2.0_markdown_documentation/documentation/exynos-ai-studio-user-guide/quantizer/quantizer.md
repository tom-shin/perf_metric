# Quantizer

Quantizer is a module in EHT that applies basic and advanced quantization methods to input models. Basic methods include fixed precision quantization and mixed precision quantization. Users can apply mixed precision quantization to models by specifying activation names or operators.

## Basic Quantization Methods

### Fixed Precision Quantization
Applies static uniform quantization to both weights and activations. Users can specify the precision (bit-width) for weights and activations. The entire model is quantized to the specified precision

### Mixed Precision Quantization
Allows different parts of the model to use different precisions  
Two approaches are supported:
- Mixed precision by name: Users specify precisions for specific activation or weight names
- Mixed precision by operator: Users define precisions for different types of operators. For example, if set the Add operator to INT4 then all outputs of the Add operators are quantized to INT4

## Advanced Quantization Methods

Currently supported advanced quantization methods are as follows.

- Softmax Bias Correction (https://arxiv.org/abs/2309.01729)
  - A method that add a float bias to Softmax output layer to reduce the performance degradation caused by quantization
- SmoothQuant (https://arxiv.org/abs/2211.10438)
  - A method that smooths the activation outliers by offline migrating the quantization difficulty from activations to weights with a mathematically equivalent transformation
- Cross Layer Equalization (https://arxiv.org/abs/1906.04721)
  - A method that tune the weights range of the channels in one tensor to reduce quantization error