# Support Matrix
The support matrices provide information about the models that are compatible with ENN SDK.

## Supported Models
ENN SDK supports the following models:
- TensorFlow Lite
    - It is recommended to convert TFLite models using MLIR (Multi-Level Intermediate Representation) version 1.14 or higher.
- Tensors up to four dimensions
- Models with a maximum size of 1 GB

Additionally, for **NPU**, the models must be quantized.

## Supported Operators
ENN SDK supports the following operators    
| **Index** | **Operator_Name**                  | **TFLite**                  | **NPU** | **DSP** | **GPU** | **CPU** |
| ----- | ------------------------------ | ----------------------- | --- | --- | --- | --- |
| 1     | ABS                            | ABS                     |     | O   | O   | O   |
| 2     | ADD                            | ADD                     |     |     | O   | O   |
| 3     | ARGMAX                         | ARG_MAX                 |     | O   | O   | O   |
| 4     | ARGMIN                         | ARG_MIN                 |     | O   | O   | O   |
| 5     | AVGPOOL                        | AVERAGE_POOL_2D         | O   | O   | O   | O   |
| 6     | BATCH_NORMALIZATION            | -                       | O   |     |     |     |
| 7     | CEIL                           | CEIL                    | O   | O   | O   | O   |
| 8     | CONCATENATION                  | CONCATENATION           | O   | O   | O   | O   |
| 9     | CONSTANT                       | -                       | O   |     |     |     |
| 10    | CONVOLUTION                    | CONV_2D                 | O   | O   | O   | O   |
| 11    | COS                            | COS                     |     |     | O   | O   |
| 12    | CROP                           | STRIDED_SLICE           |     | O   | O   | O   |
| 13    | DECONVOLUTION                  | TRANSPOSE_CONV          | O   | O   | O   | O   |
| 14    | DEPTH_TO_SPACE                 | DEPTH_TO_SPACE          | O   | O   | O   | O   |
| 15    | DEPTHWISE_CONVOLUTION          | DEPTHWISE_CONV_2D       | O   | O   | O   | O   |
| 16    | DEPTHWISE_DECONVOLUTION        | TRANSPOSE_CONV          | O   | O   | O   | O   |
| 17    | DEPTHWISE_DILATION_CONVOLUTION | DEPTHWISE_CONV_2D       | O   | O   | O   | O   |
| 18    | DEQUANTIZE                     | DEQUANTIZE              | O   | O   | O   | O   |
| 19    | DILATION_CONVOLUTION           | CONV_2D                 | O   | O   | O   | O   |
| 20    | DIV                            | DIV                     |     |     | O   | O   |
| 21    | DYNAMIC_CONVOLUTION            | -                       | O   |     |     |     |
| 22    | DYNAMIC_FC                     | -                       | O   |     |     |     |
| 23    | ELEMENTWISE_DIV                | DIV                     |     | O   | O   | O   |
| 24    | ELEMENTWISE_MUL                | MUL                     | O   | O   | O   | O   |
| 25    | ELEMENTWISE_SUB                | SUB                     | O   | O   | O   | O   |
| 26    | ELEMENTWISE_SUM                | ADD                     | O   | O   | O   | O   |
| 27    | EXP                            | EXP                     |     | O   | O   | O   |
| 28    | UNSQUEEZE                      | EXPAND_DIMS             |     |     |     | O   |
| 29    | FLATTEN                        | -                       | O   | O   | O   | O   |
| 30    | FLOOR                          | FLOOR                   |     | O   | O   | O   |
| 31    | FLOOR_DIV                      | FLOOR_DIV               |     | O   |     | O   |
| 32    | FULLY_CONNECTED                | FULLY_CONNECTED         | O   | O   | O   | O   |
| 33    | GATHER                         | GATHER                  |     |     | O   | O   |
| 34    | GLOBAL_AVGPOOL                 | -                       | O   |     | O   | O   |
| 35    | GLOBAL_MAXPOOL                 | -                       | O   | O   | O   | O   |
| 36    | GROUP_CONVOLUTION              | CONV_2D                 | O   | O   | O   | O   |
| 37    | HARD_SWISH                     | HARD_SWISH              | O   | O   | O   | O   |
| 38    | L2_NORMALIZATION               | L2_NORMALIZATION        |     | O   | O   | O   |
| 39    | LEAKY_RELU                     | LEAKY_RELU              | O   | O   | O   | O   |
| 40    | LOG                            | LOG                     |     |     | O   | O   |
| 41    | LOGISTIC                       | LOGISTIC                | O   | O   | O   | O   |
| 42    | MAXIMUM                        | MAXIMUM                 |     | O   | O   | O   |
| 43    | MAXPOOL                        | MAX_POOL_2D             | O   | O   | O   | O   |
| 44    | MEAN                           | MEAN                    |     | O   | O   | O   |
| 45    | MINIMUM                        | MINIMUM                 |     | O   | O   | O   |
| 46    | MIRROR_PAD                     | MIRROR_PAD              | O   | O   | O   | O   |
| 47    | MUL                            | MUL                     |     |     | O   | O   |
| 48    | NEG                            | NEG                     | O   | O   | O   | O   |
| 49    | PACK                           | PACK                    |     |     | O   | O   |
| 50    | PAD                            | PAD                     | O   | O   | O   | O   |
| 51    | PADV2                          | PADV2                   | O   |     | O   | O   |
| 52    | PERMUTE                        | TRANSPOSE               | O   |     | O   | O   |
| 53    | POW                            | POW                     |     |     | O   | O   |
| 54    | PRELU                          | PRELU                   | O   | O   | O   | O   |
| 55    | QUANTIZE                       | QUANTIZE                | O   | O   | O   | O   |
| 56    | REDUCE_MAX                     | REDUCE_MAX              | O   | O   | O   | O   |
| 57    | REDUCE_MEAN                    | REDUCE_MEAN             | O   | O   | O   | O   |
| 58    | REDUCE_MIN                     | REDUCE_MIN              | O   | O   | O   | O   |
| 59    | REDUCE_SUM                     | SUM                     | O   |     | O   | O   |
| 60    | RELU                           | RELU                    | O   | O   | O   | O   |
| 61    | RELU_0_TO_1                    | RELU_0_TO_1             |     | O   | O   | O   |
| 62    | RELU6                          | RELU6                   | O   | O   | O   | O   |
| 63    | RELUN                          | RELUN                   |     | O   |     |     |
| 64    | RESHAPE                        | RESHAPE                 | O   | O   | O   | O   |
| 65    | RESIZE_BILINEAR                | RESIZE_BILINEAR         | O   | O   | O   | O   |
| 66    | RESIZE_BILINEAR_DS             | RESIZE_BILINEAR         |     | O   |     | O   |
| 67    | RESIZE_NEAREST_NEIGHBOR        | RESIZE_NEAREST_NEIGHBOR | O   | O   | O   | O   |
| 68    | RESIZE_NEAREST_NEIGHBOR_DS     | RESIZE_NEAREST_NEIGHBOR |     | O   |     | O   |
| 69    | REVERSE                        | REVERSE_V2              |     |     |     | O   |
| 70    | REVERSE_V2                     | REVERSE_V2              |     |     | O   | O   |
| 71    | ROUND                          | ROUND                   |     |     | O   | O   |
| 72    | RSQRT                          | RSQRT                   |     | O   | O   | O   |
| 73    | SCALE                          | -                       | O   | O   | O   | O   |
| 74    | SCATTER_ND                     | SCATTER_ND              |     |     |     | O   |
| 75    | SELECT                         | SELECT                  |     |     |     | O   |
| 76    | SHIFT_CLAMP                    | -                       | O   | O   |     |     |
| 77    | SIN                            | SIN                     |     |     | O   | O   |
| 78    | SLICE                          | SLICE                   | O   | O   | O   | O   |
| 79    | SOFTMAX                        | SOFTMAX                 |     | O   | O   | O   |
| 80    | SPACE_TO_BATCH_ND              | SPACE_TO_BATCH_ND       |     |     |     | O   |
| 81    | SPACE_TO_DEPTH                 | SPACE_TO_DEPTH          | O   | O   | O   | O   |
| 82    | SPLIT                          | SPLIT                   | O   |     | O   | O   |
| 83    | SPLIT_V                        | SPLIT_V                 | O   |     |     | O   |
| 84    | SQRT                           | SQRT                    |     | O   | O   | O   |
| 85    | SQUARED_DIFFERENCE             | SQUARED_DIFFERENCE      |     |     | O   | O   |
| 86    | SQUEEZE                        | SQUEEZE                 |     |     | O   | O   |
| 87    | STRIDED_SLICE                  | STRIDED_SLICE           | O   | O   | O   | O   |
| 88    | SUB                            | SUB                     |     |     | O   | O   |
| 89    | TANH                           | TANH                    | O   | O   | O   | O   |
| 90    | TILE                           | TILE                    | O   |     | O   | O   |
| 91    | TRANSPOSE                      | TRANSPOSE               | O   | O   | O   | O   |
| 92    | UNPACK                         | UNPACK                  |     |     | O   | O   |
| 93    | SHAPE                          | SHAPE                   |     |     |     | O   |
| 94    | CLIP                           | -                       | O   | O   |     |     |
| 95    | CAST                           | CAST                    | O   |     | O   | O   |
| 96    | BATCH_TO_SPACE_ND              | BATCH_TO_SPACE_ND       |     |     |     | O   |
| 97    | EQUAL                          | EQUAL                   |     |     | O   | O   |
| 98    | NEQUAL                         | NOT_EQUAL               |     |     | O   |     |
| 99    | LESS                           | LESS                    |     |     | O   | O   |
| 100   | GREATER                        | GREATER                 |     |     | O   | O   |
| 101   | GREATER_EQUAL                  | GREATER_EQUAL           |     |     | O   | O   |
| 102   | LESS_EQUAL                     | LESS_EQUAL              |     |     | O   | O   |
| 103   | ADD_N                          | ADD_N                   |     |     | O   | O   |
| 104   | TOPK_V2                        | TOPK_V2                 |     |     |     | O   |
| 105   | LOG_SOFTMAX                    | LOG_SOFTMAX             |     |     | O   | O   |
| 106   | FLOOR_MOD                      | FLOOR_MOD               |     |     | O   | O   |
| 107   | SEGMENT_SUM                    | SEGMENT_SUM             |     |     | O   | O   |
| 108   | GELU                           | GELU                    |     |     | O   | O   |

## Hardware Features 

| Operator_Name                  | Kernel Size | Padding  | Strides  | Dilation  | Boost Mode |
| ------------------------------ | ----------- | -------- | -------- | --------- | ---------- |
| CONVOLUTION                    | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | -          |
| DEPTHWISE_CONVOLUTION          | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | {1 ~ 27}   |
| DECONVOLUTION                  | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | -          |
| DEPTHWISE_DECONVOLUTION        | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | -          |
| DILATION_CONVOLUTION           | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | -          |
| DEPTHWISE_DILATION_CONVOLUTION | {1 ~ 4095}  | {1 ~ 7}  | {1 ~ 7}  | {1 ~ 63}  | -          |
| AVGPOOL                  | {1 ~ 31}    | {1 ~ 15} | {1 ~ 15} | {1 ~ 127} | -          |
| MAXPOOL                   | {1 ~ 31}    | {1 ~ 15} | {1 ~ 15} | {1 ~ 127} | -          |

For `AVGPOOL` and `MAXPOOL`, when the kernel size is larger than the supported size, it is split into multiple pooling layers as the origin.