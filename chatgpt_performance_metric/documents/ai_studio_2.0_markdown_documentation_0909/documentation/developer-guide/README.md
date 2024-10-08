# ENN SDK Developer Guide

## Abstract
This guide describes the method to use Exynos Neural Network Software Development Kit (ENN SDK).
It provides instructions for converting Neural Network (NN) models to Neural Network Container (NNC) models.
It also provides information about the ENN framework, providing input to the model, executing the model, and obtaining the output.

## 1. Introduction
[ENN SDK](https://soc-developer.semiconductor.samsung.com/development/enn-sdk) allows users to convert trained [TensorFlow Lite](https://www.tensorflow.org/lite) neural network models to a format that can run efficiently in [Samsung Exynos](https://semiconductor.samsung.com/processor/) hardware.

This guide is applicable for users who want to test or construct an application to run inference on ENN SDK.

### Structure of Documentation
- [Chapter 1](#1-introduction) introduces ENN SDK and its eco-system.
- [Chapter 2](#2-features) provides information on the features of ENN SDK.
- [Chapter 3](#3-tools) provides information on tools provided with ENN SDK.
- [Chapter 4](#4-enn-tensor-framework-apis) provides information on ENN framework API.
- The subsequent chapters provide additional information on ENN SDK.

### Samples
The list of samples for ENN SDK is available in [ENN SDK Samples](enn-sdk-samples).

### Support
Support materials including forums, FAQs, and others are available at the [Exynos Developer Society web page](https://soc-developer.semiconductor.samsung.com/).

### Reporting Bugs
To report a bug or issue, follow the instructions described in the [Reporting ENN SDK Issues](#reporting-enn-sdk-issues).

## 2. Features
This chapter provides a general overview of the features that are provided by ENN SDK.

### Workflow of ENN SDK
Using ENN SDK involves the following two steps: 
1. The user converts NN models to NNC models. 
    NNC is an NN model format that can run efficiently in Samsung Exynos hardware.
1. The user executes the converted model for inference.

#### Model Conversion
Use one of the [tools](#3-tools) that is provided to convert NN models.

To convert a model:
1. Prepare a pre-trained NN model.
1. Set parameters for tools.
1. Execute tools for conversion.

#### Model Execution
Executing converted models is performed by the ENN framework.

When using the ENN framework:
1. Initialize ENN framework.
1. Load the converted model to ENN framework.
1. Allocate and commit all the necessary buffers for the model.

Then:
1.	Copy input data to input buffers.
2.	Execute model on ENN framework.
3.	Use data on output buffers.
> To execute the model multiple times, repeat this process.

Finally, perform the following steps:
1.	Uncommit and release buffers allocated to the model.
2.	Unload the model.
3.	De initialize ENN framework.

ENN framework APIs support language binding for C++.

### Supported Neural Network Models

ENN SDK supports the following NN models:
- TensorFlow Lite
- Tensors with up to four dimensions
- Models with a maximum size of 1 GB

For more information on supported TensorFlow Lite operations, refer to the [Support Matrix](support-matrix).

## 3. Tools

### ENN SDK Service
The ENN SDK service is an online platform designed to enable users to convert TFLite models into NNC models. 
To utilize this service:

1. **Access the Exynos Developer Society**:
    - If you are a new user, [sign up](https://soc-developer.semiconductor.samsung.com/register) to create an account.
    - If you are an existing user, log in to Exynos Developer Society.
1. **Navigate to the Service**:
    - Visit the [ENN SDK service](https://soc-developer.semiconductor.samsung.com/development/enn-sdk/project/) page.
1. **Provide Project Information**:
    1. Enter a descriptive title for your project.
    1. Use the provided interface to upload your TFLite model.
1. **Choose Hardware Preferences**:
    - **Default**: Utilizes only the CPU and GPU.
    - **Accelerate**: Engages the NPU as an additional accelerator.
        > ***Warning***: The NPU does not support all layers.
        Using unsupported layers may lead to complications.
        For more information on the detailed list, refer to [Support Matix](support-matrix).
1. **Initiate the Conversion**:
    1. Click **Confirm** to verify your selections.
    1. Click **Convert** to start the model conversion process.
1. **Download the Converted Model**:
    1. If the conversion is successful, the **NNC Download** button is enabled.
    1. Click NNC Download to download the NNC model.
    1. Integrate the downloaded NNC model into your application required.

## 4. ENN tensor Framework APIs

### Data Type References
For more information on the list of data types, refer to [API Reference](api-reference/#data-type-references).

### API Functions
For more information on the list of API functions, refer to [API Reference](api-reference/#api-functions).

## 5. Advanced Topics

### Model Design Tips
#### Channel Alignment
Maintaining a channel number that aligns with the specified architecture ensures effective utilization of NPU resources.

| Architecture | Channel Alignment |
| -- | -- |
| Gen-4 | 32 | 

#### Bilinear Resize Parameters
To ensure optimal image resizing using bilinear interpolation, configure the following settings:

- **Option A**:
    - Aligned corner: `False`
    - Half pixel centers: `False`
    - Performance: High speed
- **Option B**:
    - Aligned corner: `True`
    - Half pixel centers: `False`
    - Compatibility: Gen-4 and later NPUs
    - Performance: Medium speed
- **Option C**:
    - Aligned corner: `False`
    - Half pixel centers: `True`
    - Note: Requires workaround
    - Performance: Reduced speed

#### Data Processing Procedures
- **Pre-processing** and **Post-processing**: Implement these tasks outside the main model computation.
For efficient execution, it is recommended to use parallel processing on GPU or CPU.
- **Memory Alignment**: Includes data transformation operations such as `split` and `reshape` during the pre-processing phase to ensure proper data alignment.

#### Layer Adjustments
To enhance performance, it is recommended to exclude the dropout layer.

#### PReLU
Use the `PReLU` activation function for optimal performance.
Although `LeakyReLU` is functional, it may not provide the same level of efficiency.

#### Sharing IFM and OFM Recursively
Merge successive concatenate layers that share the same Input Feature Maps (IFM) and Output Feature Maps (OFM).


## 6. Troubleshooting

### FAQs
Following are the responses to some of the most frequently asked questions:

#### 1. How do I use ENN SDK service?
The [ENN SDK service section](#enn-sdk-service) provides detailed information on using the ENN SDK service.

#### 2. How many projects can I create in ENN SDK service?
Users can create a maximum of five projects with the ENN SDK service.

#### 3. Is ENN SDK service a paid service?
The ENN SDK service is currently free.

<!--
### Error Messages
Following are some of the typical error messages that users may encounter, along with potential solutions:

`To Be Updated`
-->
## Reporting ENN SDK Issues
We encourage you to share general questions, feedbacks, or suspected bugs related to the ENN SDK on our [forums](https://soc-developer.semiconductor.samsung.com/community/forum) for public discussion.
If you prefer a more direct approach or need personalized assistance, submit your concerns to our [Contact Us](https://soc-developer.semiconductor.samsung.com/support/qna/contact-us) page.
