Depth Estimation In Andriod:

This sample application demonstrates the execution of a converted [MiDaS V2](https://www.kaggle.com/models/intel/midas/frameworks/tfLite/variations/v2-1-small-lite/versions/1) model using the ENN framework.
The model is converted using ENN SDK service with the **Default** hardware type option.

## Functionality
The application accepts input from a camera feed or an image file.
A color that represents the estimated distance is overlayed on each pixel, thereby providing a visual representation of depth.
Additionally, the inference time is displayed at the bottom of the application interface.

## Location
The sample is available in the `enn-sdk-samples-9925/depth-estimation` directory within the [Github](https://github.com/exynos-eco/enn-sdk-samples-9925) repository.

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
2.	In the [`ModelConstants.kt`](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/depth-estimation/app/src/main/java/com/samsung/depthestimation/data/ModelConstants.kt) file, update the specifications to match the new model. 
```kotlin
package com.samsung.depthestimation.data

object ModelConstants {
    const val MODEL_NAME = "MiDaS_v2.nnc"

    val INPUT_DATA_TYPE = DataType.FLOAT32
    val INPUT_DATA_LAYER = LayerType.HWC

    const val INPUT_SIZE_W = 256
    const val INPUT_SIZE_H = 256
    const val INPUT_SIZE_C = 3

    const val INPUT_CONVERSION_SCALE = 127.5F
    const val INPUT_CONVERSION_OFFSET = 127.5F

    val OUTPUT_DATA_TYPE = DataType.FLOAT32

    const val OUTPUT_SIZE_W = 256
    const val OUTPUT_SIZE_H = 256

    const val OUTPUT_CONVERSION_SCALE = 1F
    const val OUTPUT_CONVERSION_OFFSET = 0F
}
```
3. If the new model requires different input and output formats, modify the `preProcess()` and `postProcess()` functions in the code. The `preProcess()` and `postProcess()` functions are located in the `executor/ModelExecutor.kt` file.