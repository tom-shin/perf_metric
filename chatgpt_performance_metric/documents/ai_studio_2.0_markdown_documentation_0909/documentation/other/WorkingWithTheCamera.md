## Camera Integration in Android using CameraX Library

### Introduction
The CameraX library, an integral component of Android Jetpack, has been designed to simplify camera operations across various Android devices. It offers a consistent and intuitive API, ensuring developers face minimal challenges when incorporating camera functionalities. This documentation delves deeper into the integration process: from initializing the hardware to intricately binding the camera's lifecycle.

#### Prerequisites:
1. Proficiency with Android application development.
2. A configured Android Studio environment.
3. CameraX library integrated into your project's Gradle dependencies.

### 1. Accessing Camera Hardware

**Objective**: Understand the necessary steps to access and initialize the camera hardware in your application.

**Class Utilized**: `ProcessCameraProvider` - A class that manages camera devices' lifecycle. It acts as a bridge between your application and the camera hardware.

#### Code Implementation:
```kotlin
private var preview: Preview? = null
private var camera: Camera? = null

private fun setCamera() {
    cameraExecutor = Executors.newSingleThreadExecutor()
    val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
    
    cameraProviderFuture.addListener(
    {
        val cameraProvider = cameraProviderFuture.get()
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
        setPreview()
        
        try {
            cameraProvider.unbindAll()
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview)
            preview?.setSurfaceProvider(binding.viewFinder.surfaceProvider)
        } catch (exc: java.lang.Exception) {
            Log.e(TAG, "Camera binding failed", exc)
        }
    },
    ContextCompat.getMainExecutor(requireContext())
    )
}
```
**Annotations**:
- `cameraExecutor`: A dedicated executor ensuring that camera operations run on a separate background thread, avoiding any UI slowdowns.
- `cameraProviderFuture`: An asynchronous task to fetch an instance of `ProcessCameraProvider`. This instance helps control and manage camera devices.
- `cameraSelector`: Utilized to specify preferences for camera initialization. Here, we select the device's default back camera.

### 2. Generating Camera Feed Preview

**Objective**: Offer a real-time view of the camera feed to users, enabling them to see what the camera lens captures.

**Class Utilized**: `Preview` - A class designed to handle and showcase the real-time camera feed.

#### Code Implementation:
```xml
<androidx.constraintlayout.widget.ConstraintLayout>
    ...
    <androidx.camera.view.PreviewView
        android:id="@+id/viewFinder"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
    ...
</androidx.constraintlayout.widget.ConstraintLayout>
```

```kotlin
private fun setPreview() {
    preview = Preview.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_4_3)
                .setTargetRotation(binding.viewFinder.display.rotation)
                .build()
}
```

**Annotations**:
- Declare the component that will output the preview image, such as "PreviewView".
- The `Preview.Builder` facilitates the configuration of the live feed properties. 
  - `setTargetAspectRatio(AspectRatio.RATIO_4_3)`: Configures the aspect ratio of the camera preview. Here, a 4:3 ratio is selected.
  - `setTargetRotation()`: Aligns the camera feed's rotation with the device's current display rotation, ensuring the feed orientation is consistent with user expectations.

### 3. Lifecycle Binding

**Objective**: To harmonize the camera's operations with the Fragment's lifecycle. Such synchronization guarantees the camera's optimal performance, ensuring that it doesn't run unnecessarily, conserving both CPU cycles and battery life.

**Methods Utilized**:
- `unbindAll()`: Clears any previous bindings, ensuring a fresh slate for binding. This step is crucial to prevent potential conflicts.
- `bindToLifecycle()`: Merges the camera's lifecycle with the fragment's lifecycle. 

#### Code Implementation:
```kotlin
cameraProviderFuture.addListener(
    {
        ...
        try {
            cameraProvider.unbindAll()
            camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview)
            preview?.setSurfaceProvider(binding.viewFinder.surfaceProvider)
        } catch (exc: java.lang.Exception) {
            Log.e(TAG, "Camera binding failed", exc)
        }
    },
    ContextCompat.getMainExecutor(requireContext())
    )
```
**Annotations**:
- This binding approach ensures that the camera activates or deactivates in conjunction with the Fragment's lifecycle events. For instance, the camera initiates when the Fragment starts and ceases when the Fragment stops.


### 4. Capture Image

**Objective**: Capture the screen and save it as a jpeg. 

**Methods Utilized**:
- `imageCapture.takePicture()`: Call takePicture() on the imageCapture object. Pass in outputOptions, an executor, and a callback for when the image is saved. Then write the callback. 

#### Code Implementation:
```kotlin
private fun takePhoto() {
    val imageCapture = imageCapture ?: return

    ...

    val contentValues = ContentValues().apply {
        put(MediaStore.MediaColumns.DISPLAY_NAME, name)
        put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
        if(Build.VERSION.SDK_INT > Build.VERSION_CODES.P) {
            put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/CameraX-Image")
        }
    }

    val outputOptions = ImageCapture.OutputFileOptions
        .Builder(contentResolver, MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)
        .build()

    imageCapture.takePicture(
        outputOptions,
        ContextCompat.getMainExecutor(this),
        object : ImageCapture.OnImageSavedCallback {
            override fun onImageSaved(output: ImageCapture.OutputFileResults){
                <Success Capture to run for your code>
            }
            override fun onError(exc: ImageCaptureException) {
                <Fail Capture to run for your code>
            }
        }
    )
}
```
**Annotations**:
- This allows you to capture an image and save it to your device.
  - `outputOptions`: You can specify how you want the output to appear. Additionally, you can set the save name, MIMETYPE, and more in `ContentValues`.
  - When the image capture function finishes executing, "OnImageSavedCallback" is executed based on the result.
    - `onImageSaved()`: Function executed on successful capture. 
    - `onError()`: Function executed on failed capture.

# Disclaimer
This document is a draft for the ENN SDK guide. 
It is intended solely for internal review and is not meant for external release.
