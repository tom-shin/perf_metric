# **Dataset preparation**

This is a guideline for preparing the input dataset.

### **Dataset format**

The dataset format must use the .h5 file extension. It is important to ensure that the keys in the h5 dataset match the input names of the model for proper mapping to occur.

Additionally, as the Exynos AI Studio currently only accepts float32 data types, the internal data within the h5 file must be in fp32 format.

The h5 file should be placed directly under the DATA folder, which is generated after executing the 'enntools init' command in the workspace.

# Model Requirements and Constraints


### model format

- Model should be prepared in ONNX format to start optimization.

### opset version

- EHT currently support ONNX opset version 13 ~ 17.
