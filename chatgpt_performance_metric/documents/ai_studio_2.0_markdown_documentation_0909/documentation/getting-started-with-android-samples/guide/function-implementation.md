# Implementing Function

## Introduction

Following classes are required to create the sample application:

- `executor`
    - `ModelExecutor.kt`: Includes methods for processing images and return classification results.
- `fragments`
    - `CameraFragment.kt`: Handles user interactions and updates the UI in Camera mode.
    - `ImageFragment.kt`: Handles user interactions and updates the UI in Image mode.
- `enn_type`
    - `BufferSetInfo`: Data class that holds information about the buffer set and number of input/output layers

For additional information, refer to the [Class Information](#a-class-information).

### Application Flow
After the sample application is launched, you can select either the camera model or image mode.
Depending on the choice, `CameraFragment` or `ImageFragment` is loaded.
Both fragments implement a [listener interface](#listener-interface) from `ModelExecutor.kt`.
This interface enables the return of inference results to the fragments.

When a fragment receives input, it invokes the `process` function in `ModelExecutor.kt`.
After the inference process is completed, this `process` function triggers the `onResults` function of the listener.
The `onResults` function then uses these results to update the user interface of the fragment.

## Listener Interface

### Implementation
The `ExecutorListener` interface in `ModelExecutor.kt` is a custom listener that provides two methods such as `onError` and `onResults`.

- `onError`: Triggered when an error occurs during image classification. It logs the error or displays an error message.
- `onResults`: Triggered when image classification is successfully completed. It updates the UI with the classification results and the time taken for classification.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/executor/ModelExecutor.kt#L258)):
```kotlin
interface ExecutorListener {
	fun onError(error: String)
	fun onResults(
		result: Map<String, Float>, inferenceTime: Long
	)
}
```

Implement the interface in the `fragment` class. 
The `onError` method logs the error and the `onResults` method updates the UI.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/CameraFragment.kt#L185)):

```kotlin
class SampleFragment : Fragment(), ImageClassifierHelper.ClassifierListener {
	...
    override fun onError(error: String) {
        Log.e(TAG, "ModelExecutor error: $error")
    }

    override fun onResults(
        result: Map<String, Float>, inferenceTime: Long
    ) {
        activity?.runOnUiThread {
            binding.processData.inferenceTime.text = "$inferenceTime ms"
            updateUI(result)
        }
    }
}
```

### Usage
Create the `ModelExecutor` object in the `fragment` class with the current context and the fragment as `executorListener`. The `process` method of `modelExecutor` is called to start the image classification.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/CameraFragment.kt#L53)):
```kotlin
modelExecutor = ModelExecutor(
	context = requireContext(), executorListener = this
)
...
modelExecutor.process(bitmapBuffer)
```

In the `ModelExecutor.kt` class, the `process` method processes the image and calls the `onResults` method of `executorListener` to pass the results back to the fragment.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/executor/ModelExecutor.kt#L76)):
```kotlin
fun process(image: Bitmap) {
	...
	
	executorListener?.onResults(
		result, inferenceTime
	)
}
```

## Processing Data

### Converting Input Data to Bitmap

#### Camera Data

The `setImageAnalyzer` function sets an `ImageAnalysis` object to process the camera feed. 
It creates a bitmap buffer and processes each image frame.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/CameraFragment.kt#L100)):
```kotlin
private fun setImageAnalyzer() {
	imageAnalyzer =
	ImageAnalysis.Builder()
		.setTargetRotation(binding.viewFinder.display.rotation)
		.setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
		.setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_RGBA_8888)
		.build().also {
			it.setAnalyzer(cameraExecutor) { image ->
				if (!::bitmapBuffer.isInitialized) {
					bitmapBuffer = Bitmap.createBitmap(
						image.width, image.height, Bitmap.Config.ARGB_8888
					)
				}
				process(image)
			}
		}
}
```

The `setCamera` function introduced [here](getting-started-with-android-samples/setting-necessary-ui#camera-preview) is updated to include the `setImageAnalyzer` method. 
This inclusion allows the camera feed to be analyzed and processed.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/CameraFragment.kt#L65)):
```kotlin
cameraProviderFuture.addListener(
	{
		...
		setPreview()
		setImageAnalyzer()

		try {
			cameraProvider.unbindAll()
			camera = cameraProvider.bindToLifecycle(
				this, cameraSelector, preview, imageAnalyzer
			)
			preview?.setSurfaceProvider(binding.viewFinder.surfaceProvider)
		}
		...
	},
	...
)
```

#### Image Data
The `ActivityResult` object `getContent` retrieves an image from the device media.
The selected image is displayed in an ImageView and converted to a bitmap.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/ImageFragment.kt#L28)):
```kotlin
private val getContent =
	registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
		uri?.let {
			binding.imageView.setImageURI(it)
			binding.buttonProcess.isEnabled = true
			
			bitmapBuffer = ImageDecoder.decodeBitmap(
				ImageDecoder.createSource(
					requireContext().contentResolver,
					it
				)
			) { decoder, _, _ ->
				decoder.setTargetColorSpace(ColorSpace.get(ColorSpace.Named.SRGB))
				decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
				decoder.setTargetSampleSize(1)
			}
		}
	}
```

Click **Load** to launch the `ActivityResult`.
It allows the user to select an image from their device.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/ImageFragment.kt#L69)):
```kotlin
binding.buttonLoad.setOnClickListener {
	getContent.launch("image/*")
}
```

#### Process Image
Click **Process** to crop and process the image.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/fragments/CameraFragment.kt#L126)):
```kotlin
private fun processImage(image: Bitmap): Bitmap {
	val rotatedCroppedImage = createCroppedBitmap(image)

	return Bitmap.createScaledBitmap(
		rotatedCroppedImage, INPUT_SIZE_W, INPUT_SIZE_H, true
	)
}

private fun createCroppedBitmap(image: Bitmap): Bitmap {
	val matrix = Matrix().apply { postRotate(90F) }
	val cropDim = calculateCropDimensions(image)

	return Bitmap.createBitmap(
		image, cropDim[0], cropDim[1], cropDim[2], cropDim[2], matrix, true
	)
}
```

#### Converting Image to Input Data
The `preProcess` function converts the processed image to input data. 
This data is casted as byte array and copied to the buffer of model.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/executor/ModelExecutor.kt#L90)):
```kotlin
private fun preProcess(image: Bitmap): ByteArray {
	val byteArray = when (INPUT_DATA_TYPE) {
		DataType.UINT8 -> {
			convertBitmapToUByteArray(image, INPUT_DATA_LAYER).asByteArray()
		}

		DataType.FLOAT32 -> {
			val data = convertBitmapToFloatArray(image, INPUT_DATA_LAYER)
			val byteBuffer = ByteBuffer.allocate(data.size * Float.SIZE_BYTES)
			byteBuffer.order(ByteOrder.nativeOrder())
			byteBuffer.asFloatBuffer().put(data)
			byteBuffer.array()
		}

		else -> {
			throw IllegalArgumentException("Unsupported input data type: ${INPUT_DATA_TYPE}")
		}
	}

	return byteArray
}
```

### Processing Output Data
The `postProcess` function processes the output from the neural network model. 
It converts the quantized output values to percentile scores, matches the index with the label, filters items that exceed the score threshold, and sorts them in descending order. 
The filtered items provide the final classification results.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/executor/ModelExecutor.kt#L112)):
```kotlin
private fun postProcess(modelOutput: ByteArray): Map<String, Float> {
	val output = when (OUTPUT_DATA_TYPE) {
		DataType.UINT8 -> {
			modelOutput.asUByteArray().mapIndexed { index, value ->
				labelList[index] to dequantizedValues[((value.toInt()
						- OUTPUT_CONVERSION_OFFSET)
						/ OUTPUT_CONVERSION_SCALE).toInt()]
			}.filter { it.second >= threshold }.sortedByDescending { it.second }.toMap()
		}

		DataType.FLOAT32 -> {
			val byteBuffer = ByteBuffer.wrap(modelOutput).order(ByteOrder.nativeOrder())
			val floatBuffer = byteBuffer.asFloatBuffer()
			val data = FloatArray(floatBuffer.remaining())

			floatBuffer.get(data)
			data.mapIndexed { index, value ->
				labelList[index] to ((value
						- OUTPUT_CONVERSION_OFFSET)
						/ OUTPUT_CONVERSION_SCALE)
			}.filter { it.second >= threshold }.sortedByDescending { it.second }.toMap()
		}

		else -> {
			throw IllegalArgumentException("Unsupported output data type: ${OUTPUT_DATA_TYPE}")
		}
	}

	return output
}
```

## Preparing NNC Model
Use `copyNNCFromAssetsToInternalStorage` function to copy the NNC model file from the asset directory of app to its internal storage. 
It is necessary to copy the NNC model file because the model file needs to be accessed from the internal storage when used by the ENN Framework.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/executor/ModelExecutor.kt#L231)):
```kotlin
private fun copyNNCFromAssetsToInternalStorage(filename: String) {
	try {
		val inputStream = context.assets.open(filename)
		val outputFile = File(context.filesDir, filename)
		val outputStream = FileOutputStream(outputFile)
		val buffer = ByteArray(2048)
		var bytesRead: Int

		while (inputStream.read(buffer).also { bytesRead = it } != -1) {
			outputStream.write(buffer, 0, bytesRead)
		}
		inputStream.close()
		outputStream.close()
	} catch (e: IOException) {
		e.printStackTrace()
	}
}
```

## Data Class

### BufferSetInfo
The `BufferSetInfo` data class holds the information about the buffer set used in the neural network model. 
It includes the memory location of the buffer set (`buffer_set`), the number of input buffers (`n_in_buf`), and the number of output buffers (`n_out_buf`).
Use the data class to return this information from the JNI library.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/image-classification/app/src/main/java/com/samsung/imageclassification/enn_type/BufferSetInfo.kt)):
```kotlin
class BufferSetInfo {
	var buffer_set: Long = 0
	var n_in_buf: Int = 0
	var n_out_buf: Int = 0
}
```

## Appendix
### A. Class Information
#### A.1 Data Classes (`data` package)
- `DataType.kt`: An enum class for input/output buffer data types.
- `LayerType.kt`: An enum class for defining data formats.
- `ModelConstants.kt`: An object class that contains model parameters.

#### A.2 ENN JNI Class (`enn_type` package)
- `BufferSetInfo.kt`: A class for receiving buffer data from the JNI interface.

#### A.3 Executor Class (`executor` package)
- `ModelExecutor.kt`: A class for executing the ENN SDK and processing input and output data.

	| Function | Details |
	| -------- | ------- |
	| `setupENN` | Initializes the ENN SDK framework, opens and allocates buffers of the model. |
	| `process` | Calls the data preprocess function, executes the model, and calls the postprocess function. |
	| `closeENN` | Releases allocated buffers, closes the model, and deinitializes the ENN SDK framework. |
	| `preProcess` | Converts bitmap images to input data byte arrays. |
	| `postProcess` | Converts output data byte arrays to a mapping of index and score. |

#### A.4 Fragment Classes (`fragments` package)
- `CameraFragment.kt`: A fragment class responsible for the camera mode UI.

	| Function | Details |
	| -------- | ------- |
	| `onCreateView` | Called when the fragment is created. |
	| `onViewCreated` | Called immediately after `onCreateView` to set up UI components. |
	| `setCamera` | Sets up the camera for preview and model input. |
	| `setPreview` | Establishes the camera preview. |
	| `setImageAnalyzer` | Configures the image analyzer for the camera feed. |
	| `process` | Invokes the `process` method from the `ModelExecutor` class. |
	| `processImage` | Adjusts the image to match the input size of the model. |
	| `setUI` | Initializes UI components. |
	| `updateUI` | Updates the UI after model execution is completed. |


- `ImageFragment.kt`: A fragment class responsible for the image mode UI.

	| Function | Details |
	| -------- | ------- |
	| `onCreateView` | Called when the fragment is created. |
	| `onViewCreated` | Called immediately after `onCreateView` to set up UI components. |
	| `getContent` | Loads the image for processing. |
	| `setUI` | Initializes UI components. |
	| `process` | Invokes the `process` method from the `ModelExecutor` class. |
	| `processImage` | Adjusts the image to match the input size of the model. |
	| `updateUI` | Updates the UI after model execution is completed. |

- `SelectFragment.kt`: A fragment class responsible for the mode selection UI.