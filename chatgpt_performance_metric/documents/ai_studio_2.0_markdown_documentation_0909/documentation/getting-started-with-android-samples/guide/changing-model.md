# Changing the Model in an Android Sample Application

This guide provides a step-by-step process to replace the model in an Android sample application.

## Updating the Model in Android Studio
To update the model in your Android project, do the following:
1. Place the new model file in the `assets` directory of your Android Studio project.
2. In the `ModelConstants.kt` file, update the specifications to match the new model.
3. If the new model uses a different set of labels, add the corresponding label text file to the `assets` directory.
4. If the new model requires different input and output formats, modify the `preProcess()` and `postProcess()` functions in the code.

> **Notes:**
> 
> - The `assets` directory is located at `${APP_ROOT}/app/src/main`.
> - The `preProcess()` and `postProcess()` functions are located in the  `executor/ModelExecutor.kt` file.

## Example: Switching to MobileNet V3
### Preparing the Model
To integrate a new model, do the following:
1. Download MobileNet V3 `.tflite` model from [here](https://www.kaggle.com/models/google/mobilenet-v3/frameworks/tfLite/variations/large-100-224-classification).
2. Upload  the `.tflite` model downloaded in Step 1 to ENN SDK service. 
3. Then, follow the process described in the [ENN SDK service guide](getting-started-with-android-samples/enn-sdk-service), and select **Default** as the hardware type  to convert the `.tflite`  model to `.nnc` format.
4. After the conversion is completed, download the model from ENN SDK service and then rename it as  `mobilenet-v3.nnc`.

### Updating the Android Project
1. Copy the `mobilenet-v3.nnc` model file to `assets` directory of your Andriod project.
2. Update `ModelConstants.kt` with the new input/output data types and sizes:
    ```kotlin
    object ModelConstants {
        const val MODEL_NAME = "mobilenet-v3.nnc"

        val INPUT_DATA_TYPE = DataType.FLOAT32
        val INPUT_DATA_LAYER = LayerType.HWC

        const val INPUT_SIZE_W = 224
        const val INPUT_SIZE_H = 224
        const val INPUT_SIZE_C = 3

        const val INPUT_CONVERSION_SCALE = 256F
        const val INPUT_CONVERSION_OFFSET = 0F

        val OUTPUT_DATA_TYPE = DataType.FLOAT32

        const val OUTPUT_CONVERSION_SCALE = 1F
        const val OUTPUT_CONVERSION_OFFSET = 0F

        const val LABEL_FILE = "labels1001.txt"
    }
    ```
3. Adjust the `postProcess()` function for the output of the new model, which is a logits-vector instead of $[0,1]$ scores:
    ```kotlin
    private fun postProcess(modelOutput: ByteArray): Map<String, Float> {
        val output = when (OUTPUT_DATA_TYPE) {
            DataType.FLOAT32 -> {
                val byteBuffer = ByteBuffer.wrap(modelOutput).order(ByteOrder.nativeOrder())
                val floatBuffer = byteBuffer.asFloatBuffer()
                val data = FloatArray(floatBuffer.remaining())

                floatBuffer.get(data)
                data.mapIndexed { index, value ->
                    labelList[index] to (1.0 / (1.0 + kotlin.math.exp(-value.toDouble()))).toFloat()
                }.filter { it.second >= threshold }.sortedByDescending { it.second }.toMap()
            }

            else -> {
                throw IllegalArgumentException("Unsupported output data type: ${OUTPUT_DATA_TYPE}")
            }
        }

        return output
    }
    ```
