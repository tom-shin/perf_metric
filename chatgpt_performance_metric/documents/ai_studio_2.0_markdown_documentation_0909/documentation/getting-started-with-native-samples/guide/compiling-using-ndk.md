# Compiling Using NDK
This section describes the method to use NDK to compile the native program.
The process comprises of two main steps such as setting up the Makefile and initiating the build process with NDK.

## Creating the Makefile
The Makefile is a crucial component in the build process.
It instructs the compiler on how to build the program.
The Makefile for this project is divided into two parts such as `Android.mk` and `Application.mk`.

### Android.mk
The `Android.mk` file defines the module and its properties.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/nnc-model-tester/jni/Android.mk)):
```cmake
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := enn_public_api_ndk_v1
LOCAL_SRC_FILES := ${LOCAL_PATH}/lib64/libenn_public_api_ndk_v1.so
include $(PREBUILT_SHARED_LIBRARY)

include $(CLEAR_VARS)
LOCAL_MODULE := enn_nnc_model_tester

LOCAL_C_INCLUDES += \
                    ${LOCAL_PATH} \
                    ${LOCAL_PATH}/include

LOCAL_LDLIBS := -llog
LOCAL_CFLAGS += -Wall -std=c++14 -O3
LOCAL_CPPFLAGS += -fexceptions -frtti

LOCAL_SRC_FILES := enn_nnc_model_tester.cpp
LOCAL_SHARED_LIBRARIES := enn_public_api_ndk_v1
include $(BUILD_EXECUTABLE)
```

### Application.mk:
The `Application.mk` file specifies the Application Binary Interface (ABI) and the Standard Template Library (STL) variant that must be used.

([example](https://github.com/exynos-eco/enn-sdk-samples-9925/blob/main/nnc-model-tester/jni/Application.mk)):
```cmake
APP_ABI := arm64-v8a
APP_STL := c++_static
```


## Build Using NDK
After the Makefile is set up, the build process with NDK can be initiated. 
- Windows
    ```shell
    %ANDROID_NDK_HOME%\ndk-build.cmd -C .\jni
    ```
- Linux
    ```shell
    $ANDROID_NDK_HOME/ndk-build -C ./jni
    ```

This command instructs NDK to start the build process in the current directory.

## Verifying the Build
After the build process is complete, the compiled program can be verified by checking the `libs` directory:
- Windows
    ```shell
    dir libs\arm64-v8a\
    ```
- Linux
    ```shell
    ls libs/arm64-v8a/
    ```
The compiled program (`enn_nnc_model_tester`) is visible in the output.

## Troubleshooting
If you encounter any issues during the build process, ensure the following:

- The `NDK_PROJECT_PATH` environment variable is correctly set.
- The `ANDROID_NDK_HOME` environment variable points to the correct location of the NDK installation.
- The paths in the `Android.mk` file are correct.