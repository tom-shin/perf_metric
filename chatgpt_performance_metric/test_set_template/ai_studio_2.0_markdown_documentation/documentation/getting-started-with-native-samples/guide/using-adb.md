# Using Adb to Execute
This section provides the detailed information on using the ADB to execute the native program on the ERD board.
This process comprises of two main steps such as copying data to the board and executing the native program on the ERD board.

## Copying Data to ERD Board
The following commands copy the necessary files to the ERD board:

```shell
adb push libs/arm64-v8a/enn_nnc_model_tester /data/local/tmp/
adb push libs/arm64-v8a/libenn_public_api_ndk_v1.so /data/local/tmp/
adb push example/model.nnc /data/local/tmp/
adb push example/input.bin /data/local/tmp/
adb push example/golden.bin /data/local/tmp/
```

These commands perform the following actions:

- `adb push` is used to copy the model file (`model.nnc`), input data file (`input.bin`), golden data file (`golden.bin`), library file (`libenn_public_api_ndk_v1.so`), and the native program (`enn_nnc_model_tester`) to the `/data/vendor/enn/` directory on the ERD board.

## Executing Native Program on the ERD Board
After copying the necessary files to the ERD board, execute the native program using the following commands: 

```shell
adb shell
cd /data/local/tmp/
export LD_LIBRARY_PATH=/data/local/tmp 
./enn_nnc_model_tester --model model.nnc --input input.bin --golden golden.bin --threshold 0.0001
```

> When nnc_model_tester is built from Windows, execute permission must be provided.
>   ```shell
>   adb shell "chmod +x /data/local/tmp/enn_nnc_model_tester"
>   ```

These commands perform the following actions:

- `adb shell` starts a shell session on the board.
- `cd /data/local/tmp/` changes the current directory to `/data/local/tmp/`, where the necessary files are available.
- The `LD_LIBRARY_PATH` environment variable sets the directory that contains `libenn_public_api_ndk_v1.so`.
- The native program is executed with the `--model`, `--input`, `--golden`, and `--threshold` parameters, which specify the model file, input data file, golden data file, and threshold value, respectively.