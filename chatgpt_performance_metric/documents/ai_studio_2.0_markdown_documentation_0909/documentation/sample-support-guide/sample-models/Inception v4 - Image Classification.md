Image Classification In Android:

This sample application demonstrates the execution of a converted [Inception v4](https://www.kaggle.com/models/tensorflow/inception/frameworks/tfLite/variations/v4-quant/versions/1) model using the ENN framework. The model is converted using ENN SDK service with the **Accelerate** hardware type option.

## Functionality
The sample application accepts input from a camera feed or an image file and classifies the object within the input. The classified items, their corresponding scores, and the inference time are displayed at the bottom of the application interface.

## Location
The sample is available in the `enn-sdk-samples-9925/image-classification` directory within the [Github](https://github.com/exynos-eco/enn-sdk-samples-9925) repository.

## Getting Started
To utilize the sample application:
1.	Download or clone the sample application from this repository.
2.	Open the sample application project in Android Studio.
3.	Connect the ERD board to the computer.
4.	Run the application (using Shift + F10).
5.	Select Camera or Image mode and provide the data for inference.

## Changing the Model in an Android Sample Application
To update the model in your Android project, do the following:
1.	Place the new model file in the assets directory of your Android Studio project. The assets directory is located at `${APP_ROOT}/app/src/main`.
2.	In the [`ModelConstants.kt`](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/data/ModelConstants.kt) file, update the specifications to match the new model. 
    ```kotlin
    package com.samsung.imageclassification.data
    
    object ModelConstants {
        const val MODEL_NAME = "inception_v4_quant.nnc"
    
        val INPUT_DATA_TYPE = DataType.UINT8
        val INPUT_DATA_LAYER = LayerType.HWC
    
        const val INPUT_SIZE_W = 299
        const val INPUT_SIZE_H = 299
        const val INPUT_SIZE_C = 3
    
        const val INPUT_CONVERSION_SCALE = 1F
        const val INPUT_CONVERSION_OFFSET = 0F
    
        val OUTPUT_DATA_TYPE = DataType.UINT8
    
        const val OUTPUT_CONVERSION_SCALE = 1F
        const val OUTPUT_CONVERSION_OFFSET = 0F
    
        const val LABEL_FILE = "labels1001.txt"
    }
    ```
3. If the new model uses a different set of labels, add the corresponding label text file to the assets directory.
4. If the new model requires different input and output formats, modify the `preProcess()` and `postProcess()` functions in the code. The `preProcess()` and `postProcess()` functions are located in the `executor/ModelExecutor.kt` file.