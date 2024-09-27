# ENN Framwork API Functions

## Context initialize / deinitialize

### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnInitialize](#function-enninitialize)**(void )<br>Initialize Enn Framework. Framework generates context in a caller's process. Context counts initialize/deinitialize pair.  |
| EnnReturn | **[EnnDeinitialize](#function-enndeinitialize)**(void )<br>Deinitialize Enn Framework. Framework degenerates context in a caller's process.  |


### Functions Documentation

#### function EnnInitialize

```cpp
EnnReturn EnnInitialize(
    void 
)
```

Initialize Enn Framework. Framework generates context in a caller's process. Context counts initialize/deinitialize pair. 

**Return**: EnnReturn result, 0 is success 

#### function EnnDeinitialize

```cpp
EnnReturn EnnDeinitialize(
    void 
)
```

Deinitialize Enn Framework. Framework degenerates context in a caller's process. 

**Return**: EnnReturn result, 0 is success 

## OpenModel / CloseModel related



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnOpenModel](#function-ennopenmodel)**(const char * model_file, EnnModelId * model_id)<br>OpenModel with model file.  |
| EnnReturn | **[EnnOpenModelFromMemory](#function-ennopenmodelfrommemory)**(const char * va, const uint32_t size, EnnModelId * model_id)<br>OpenModel from memory buffer.  |
| EnnReturn | **[EnnCloseModel](#function-ennclosemodel)**(const EnnModelId model_id);<br>Close model and free all resources in OpenModel()|


### Functions Documentation

#### function EnnOpenModel

```cpp
EnnReturn EnnOpenModel(
    const char * model_file,
    EnnModelId * model_id
)
```

OpenModel with model file. 

**Parameters**: 

  * **model_file** [IN] model_file, output from graph-gen. A caller should access the file. 
  * **model_id** [OUT] model_id, 64 bit unsigned int 


**Return**: EnnReturn result, 0 is success 

#### function EnnOpenModelFromMemory

```cpp
EnnReturn EnnOpenModelFromMemory(
    const char * va,
    const uint32_t size,
    EnnModelId * model_id
)
```

OpenModel from memory buffer. 

**Parameters**: 

  * **va** [IN] address which a model loaded from 
  * **size** [IN] size of the buffer 
  * **model_id** [OUT] model_id, 64 bit unsigned int 


**Return**: EnnReturn result, 0 is success 


#### function EnnCloseModel

```cpp
EnnReturn EnnCloseModel(
  const EnnModelId model_id
);
```

Close model and free all resources in OpenModel().

**Parameters**: 

  * **model_id** [IN] model_id from OpenModel()


**Return**: EnnReturn result, 0 is success


## Memory Handling



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnCreateBuffer](#function-enncreatebuffer)**([EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) * out, const uint32_t req_size, const bool is_cached =true)<br>Create Buffer with request size support ION or dmabufheap which can be used in a device(DSP/CPU/NPU/GPU)  |
| EnnReturn | **[EnnAllocateAllBuffers](#function-ennallocateallbuffers)**(const EnnModelId model_id, [EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) ** out_buffers, [NumberOfBuffersInfo](api-reference/enn-framework-data-type-references/#_numberofbuffersinfo) * buf_info, const int session_id =0, const bool do_commit =true)<br>Allocate all buffers which a caller should allocate.  |
| EnnReturn | **[EnnReleaseBuffers](#function-ennreleasebuffers)**([EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) * buffers, const int32_t numOfBuffers)<br>Release buffer array from EnnAllocatedAllBuffers() This API includes releasing all elements in the array.  |
| EnnReturn | **[EnnReleaseBuffer](#function-ennreleasebuffer)**([EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) buffer)<br>release buffer from [EnnCreateBuffer()](#function-enncreatebuffer) |


### Functions Documentation

#### function EnnCreateBuffer

```cpp
EnnReturn EnnCreateBuffer(
    EnnBufferPtr * out,
    const uint32_t req_size,
    const bool is_cached =true
)
```

Create Buffer with request size support ION or dmabufheap which can be used in a device(DSP/CPU/NPU/GPU) 

**Parameters**: 

  * **out** [OUT] output buffer pointer. User can get va, size, offset through *out 
  * **req_size** [IN] request size 
  * **is_cached** [IN] flag, the buffer uses cache or not 


**Return**: EnnReturn 

#### function EnnAllocateAllBuffers

```cpp
EnnReturn EnnAllocateAllBuffers(
    const EnnModelId model_id,
    EnnBufferPtr ** out_buffers,
    NumberOfBuffersInfo * buf_info,
    const int session_id =0,
    const bool do_commit =true
)
```

Allocate all buffers which a caller should allocate. 

**Parameters**: 

  * **model_id** model_id from OpenModel() 
  * **out_buffers** [OUT] pointer of EnnBuffer array 
  * **buf_info** [OUT] size of the array 
  * **session_id** [IN] after generate buffer space, user can set this field if session_id > 0 
  * **do_commit** [IN] if true, the framework tries to commit after buffer allocation


**Return**: EnnReturn result, 0 is success 

#### function EnnReleaseBuffers

```cpp
EnnReturn EnnReleaseBuffers(
    EnnBufferPtr * buffers,
    const int32_t numOfBuffers
)
```

Release buffer array from EnnAllocatedAllBuffers() This API includes releasing all elements in the array. 

**Parameters**: 

  * **buffers** [IN] pointer of buffer array 
  * **numOfBuffers** [IN] size of bufefr array


**Return**: EnnReturn result, 0 is success 

#### function EnnReleaseBuffer

```cpp
EnnReturn EnnReleaseBuffer(
    EnnBufferPtr buffer
)
```

release buffer from [EnnCreateBuffer()](#function-enncreatebuffer)

**Parameters**: 

  * **buffer** [IN] buffer object from [EnnCreateBuffer()](#function-enncreatebuffer)


**Return**: EnnReturn result, 0 is success 


## Setters and Getters for model



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnGetBuffersInfo](#function-enngetbuffersinfo)**([NumberOfBuffersInfo](api-reference/enn-framework-data-type-references/#_numberofbuffersinfo) * buffers_info, const EnnModelId model_id)<br>Get buffers information from loaded model.  |
| EnnReturn | **[EnnGetBufferInfoByIndex](#function-enngetbufferinfobyindex)**([EnnBufferInfo](api-reference/enn-framework-data-type-references/#_ennbufferinfo) * out_buf_info, const EnnModelId model_id, const enn_buf_dir_e direction, const uint32_t index)<br>Get one buffer information from loaded model.  |
| EnnReturn | **[EnnGetBufferInfoByLabel](#function-enngetbufferinfobylabel)**([EnnBufferInfo](api-reference/enn-framework-data-type-references/#_ennbufferinfo) * out_buf_info, const EnnModelId model_id, const char * label)<br>Get one buffer information from loaded model.  |
| EnnReturn | **[EnnSetBufferByIndex](#function-ennsetbufferbyindex)**(const EnnModelId model_id, const enn_buf_dir_e direction, const uint32_t index, [EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) buf, const int session_id =0)<br>Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core.  |
| EnnReturn | **[EnnSetBufferByLabel](#function-ennsetbufferbylabel)**(const EnnModelId model_id, const char * label, [EnnBufferPtr](api-reference/enn-framework-data-type-references/#_ennbuffer) buf, const int session_id =0)<br>Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core.  |


### Functions Documentation

#### function EnnGetBuffersInfo

```cpp
EnnReturn EnnGetBuffersInfo(
    NumberOfBuffersInfo * buffers_info,
    const EnnModelId model_id
)
```

Get buffers information from loaded model. 

**Parameters**: 

  * **buffers_info** [OUT] number of in / out buffer which caller should commit. 
  * **model_id** [IN] model id from OpenModel()


**Return**: EnnReturn result, 0 is success 

#### function EnnGetBufferInfoByIndex

```cpp
EnnReturn EnnGetBufferInfoByIndex(
    EnnBufferInfo * out_buf_info,
    const EnnModelId model_id,
    const enn_buf_dir_e direction,
    const uint32_t index
)
```

Get one buffer information from loaded model. 

**Parameters**: 

  * **out_buf_info** [OUT] output buffer information 
  * **model_id** [IN] model ID from load_model 
  * **direction** [IN] direction (IN, OUT) 
  * **index** [IN] buffer's index number in model


**Return**: EnnReturn result, 0 is success 



```cpp
typedef struct _ennBufferInfo {
    bool     is_able_to_update;  // this is not used
    uint32_t n;
    uint32_t width;
    uint32_t height;
    uint32_t channel;
    uint32_t size;
    const char *label;
} EnnBufferInfo;
```

 a caller can identify a buffer as {DIR, Index} such as {IN, 0}


#### function EnnGetBufferInfoByLabel

```cpp
EnnReturn EnnGetBufferInfoByLabel(
    EnnBufferInfo * out_buf_info,
    const EnnModelId model_id,
    const char * label
)
```

Get one buffer information from loaded model. 

**Parameters**: 

  * **out_buf_info** [OUT] output buffer information 
  * **model_id** [IN] model ID from load_model 
  * **label** [IN] label. if .nnc includes redundent label, the framework returns information of the first founded tensor. C-style string type.


**Return**: EnnReturn result, 0 is success 



```cpp
typedef struct _ennBufferInfo {
    bool     is_able_to_update;  // this is not used
    uint32_t n;
    uint32_t width;
    uint32_t height;
    uint32_t channel;
    uint32_t size;
    const char *label;
} EnnBufferInfo;
```

 a caller can identify a buffer as {label} or {tensor name}


#### function EnnSetBufferByIndex

```cpp
EnnReturn EnnSetBufferByIndex(
    const EnnModelId model_id,
    const enn_buf_dir_e direction,
    const uint32_t index,
    EnnBufferPtr buf,
    const int session_id =0
)
```

Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **direction** [IN] Direction (IN/OUT) 
  * **index** [IN] index number of buffer 
  * **buf** [IN] memory object from EnnCreateBufferXXX() 
  * **session_id** [IN] If a caller generates 2 or more buffer space, session_id can be an identifier


**Return**: EnnReturn result, 0 is success 

#### function EnnSetBufferByLabel

```cpp
EnnReturn EnnSetBufferByLabel(
    const EnnModelId model_id,
    const char * label,
    EnnBufferPtr buf,
    const int session_id =0
)
```

Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **label** [IN] label. if .nnc includes redundent label, the framework returns information of the first founded tensor. C-style string type. 
  * **buf** [IN] memory object from EnnCreateBufferXXX() 
  * **session_id** [IN] If a caller generates 2 or more buffer space, session_id can be an identifier


**Return**: EnnReturn result, 0 is success 

## Commit Buffer



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnBufferCommit](#function-ennbuffercommit)**(const EnnModelId model_id, const int session_id =0)<br>Send buffer-set to service core. session_id indicates which buffer space should be sent. The committed buffers are released if a caller calls CloseModel()  |


### Functions Documentation

#### function EnnBufferCommit

```cpp
EnnReturn EnnBufferCommit(
    const EnnModelId model_id,
    const int session_id =0
)
```

Send buffer-set to service core. session_id indicates which buffer space should be sent. The committed buffers are released if a caller calls CloseModel() 

**Parameters**: 

  * **model_id** [IN] model ID from load_model


**Return**: EnnReturn result, 0 is success 


## Execute Models



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnExecuteModel](#function-ennexecutemodel)**(const EnnModelId model_id, const int session_id =0)<br>Request to service core to execute model with commited buffers.  |
| EnnReturn | **[EnnExecuteModelAsync](#function-ennexecutemodelasync)**(const EnnModelId model_id, const int session_id =0)<br>Request to service core to execute model in background asynchronously.  |
| EnnReturn | **[EnnExecuteModelWait](#function-ennexecutemodelwait)**(const EnnModelId model_id, const int session_id =0)<br>Wait result of calling [EnnExecuteModelAsync()](#function-ennexecutemodelasync) If execution is finished, this function is returned intermediatelly If not, this function would be blocked until the execution finished.  |


### Functions Documentation

#### function EnnExecuteModel

```cpp
EnnReturn EnnExecuteModel(
    const EnnModelId model_id,
    const int session_id =0
)
```

Request to service core to execute model with commited buffers. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **session_id** [IN] session ID


**Return**: EnnReturn result, 0 is success 

**Note**: this function runs in block mode 

#### function EnnExecuteModelAsync

```cpp
EnnReturn EnnExecuteModelAsync(
    const EnnModelId model_id,
    const int session_id =0
)
```

Request to service core to execute model in background asynchronously. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **session_id** [IN] session ID


**Return**: EnnReturn result, 0 is success 

#### function EnnExecuteModelWait

```cpp
EnnReturn EnnExecuteModelWait(
    const EnnModelId model_id,
    const int session_id =0
)
```

Wait result of calling [EnnExecuteModelAsync()](#function-ennexecutemodelasync) If execution is finished, this function is returned intermediatelly If not, this function would be blocked until the execution finished. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **session_id** [IN] session ID


**Return**: EnnReturn result, 0 is success 


## Security, preference, get meta information..



### Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnSetPreferencePresetId](#function-ennsetpreferencepresetid)**(const uint32_t val)<br>Setting Preset ID for operation performance.  |
| EnnReturn | **[EnnSetPreferencePerfConfigId](#function-ennsetpreferenceperfconfigid)**(const uint32_t val)<br>Setting PerfConfig ID for operation performance.  |
| EnnReturn | **[EnnSetPreferencePerfMode](#function-ennsetpreferenceperfmode)**(const uint32_t val)<br>Setting Performance Mode.  |
| EnnReturn | **[EnnSetPreferenceTimeOut](#function-ennsetpreferencetimeout)**(const uint32_t val)<br>Setting Preset ID for time out.  |
| EnnReturn | **[EnnSetPreferencePriority](#function-ennsetpreferencepriority)**(const uint32_t val)<br>Setting priority value for NPU.  |
| EnnReturn | **[EnnSetPreferenceCoreAffinity](#function-ennsetpreferencecoreaffinity)**(const uint32_t val)<br>Setting affinity to set NPU core operation.  |
| EnnReturn | **[EnnGetPreferencePresetId](#function-enngetpreferencepresetid)**(uint32_t * val_ptr)<br>Get current information for Preset ID.  |
| EnnReturn | **[EnnGetPreferencePerfConfigId](#function-enngetpreferenceperfconfigid)**(uint32_t * val_ptr)<br>Get current information for PerfConfig ID.  |
| EnnReturn | **[EnnGetPreferencePerfMode](#function-enngetpreferenceperfmode)**(uint32_t * val_ptr)<br>Get current information for Performance Mode.  |
| EnnReturn | **[EnnGetPreferenceTimeOut](#function-enngetpreferencetimeout)**(uint32_t * val_ptr)<br>Get current information for Time Out.  |
| EnnReturn | **[EnnGetPreferencePriority](#function-enngetpreferencepriority)**(uint32_t * val_ptr)<br>Get current information for NPU Priority.  |
| EnnReturn | **[EnnGetPreferenceCoreAffinity](#function-enngetpreferencecoreaffinity)**(uint32_t * val_ptr)<br>Get current information for NPU Core affinity.  |
| EnnReturn | **[EnnGetMetaInfo](#function-enngetmetainfo)**(const EnnMetaTypeId info_id, const EnnModelId model_id, char output_str[ENN_INFO_GRAPH_STR_LENGTH_MAX])<br>Get Meta Information.  |
| EnnReturn | **[EnnSetExecMsgAlwaysOn](#function-ennsetexecmsgalwayson)**()<br>Set frequency of execution message print.  |


### Functions Documentation

#### function EnnSetPreferencePresetId

```cpp
EnnReturn EnnSetPreferencePresetId(
    const uint32_t val
)
```

Setting Preset ID for operation performance. 

**Parameters**: 

  * **val** [IN] value to set preset ID


**Return**: EnnReturn result, 0 is success 

#### function EnnSetPreferencePerfConfigId

```cpp
EnnReturn EnnSetPreferencePerfConfigId(
    const uint32_t val
)
```

Setting PerfConfig ID for operation performance. 

**Parameters**: 

  * **val** [IN] value to set PerfConfig ID


**Return**: EnnReturn result, 0 is success 

#### function EnnSetPreferencePerfMode

```cpp
EnnReturn EnnSetPreferencePerfMode(
    const uint32_t val
)
```

Setting Performance Mode. 

**Parameters**: 

  * **val** [IN] value to set Performance Mode


**Return**: EnnReturn result, 0 is success 

#### function EnnSetPreferenceTimeOut

```cpp
EnnReturn EnnSetPreferenceTimeOut(
    const uint32_t val
)
```

Setting Preset ID for time out. 

**Parameters**: 

  * **val** [IN] value to set time out


**Return**: EnnReturn result, 0 is success 

**Note**: in second 

#### function EnnSetPreferencePriority

```cpp
EnnReturn EnnSetPreferencePriority(
    const uint32_t val
)
```

Setting priority value for NPU. 

**Parameters**: 

  * **val** [IN] value to set NPU job priority


**Return**: EnnReturn result, 0 is success 

#### function EnnSetPreferenceCoreAffinity

```cpp
EnnReturn EnnSetPreferenceCoreAffinity(
    const uint32_t val
)
```

Setting affinity to set NPU core operation. 

**Parameters**: 

  * **val** [IN] value to set affinity


**Return**: EnnReturn result, 0 is success 

**Note**: in second 

#### function EnnGetPreferencePresetId

```cpp
EnnReturn EnnGetPreferencePresetId(
    uint32_t * val_ptr
)
```

Get current information for Preset ID. 

**Parameters**: 

  * **val** [OUT] current value of Preset ID


**Return**: EnnReturn result, 0 is success 

#### function EnnGetPreferencePerfConfigId

```cpp
EnnReturn EnnGetPreferencePerfConfigId(
    uint32_t * val_ptr
)
```

Get current information for PerfConfig ID. 

**Parameters**: 

  * **val** [OUT] current value of PerfConfig ID


**Return**: EnnReturn result, 0 is success 

#### function EnnGetPreferencePerfMode

```cpp
EnnReturn EnnGetPreferencePerfMode(
    uint32_t * val_ptr
)
```

Get current information for Performance Mode. 

**Parameters**: 

  * **val** [OUT] current value of Performance Mode


**Return**: EnnReturn result, 0 is success 

#### function EnnGetPreferenceTimeOut

```cpp
EnnReturn EnnGetPreferenceTimeOut(
    uint32_t * val_ptr
)
```

Get current information for Time Out. 

**Parameters**: 

  * **val** [OUT] current value of Time Out


**Return**: EnnReturn result, 0 is success 

#### function EnnGetPreferencePriority

```cpp
EnnReturn EnnGetPreferencePriority(
    uint32_t * val_ptr
)
```

Get current information for NPU Priority. 

**Parameters**: 

  * **val** [OUT] current value of NPU Priority


**Return**: EnnReturn result, 0 is success 

#### function EnnGetPreferenceCoreAffinity

```cpp
EnnReturn EnnGetPreferenceCoreAffinity(
    uint32_t * val_ptr
)
```

Get current information for NPU Core affinity. 

**Parameters**: 

  * **val** [OUT] current value of NPU Core affinity


**Return**: EnnReturn result, 0 is success 

#### function EnnGetMetaInfo

```cpp
EnnReturn EnnGetMetaInfo(
    const EnnMetaTypeId info_id,
    const EnnModelId model_id,
    char output_str[ENN_INFO_GRAPH_STR_LENGTH_MAX]
)
```

Get Meta Information. 

**Parameters**: 

  * **info_id** info_id can be below: currently, ENN_META_VERSION_FRAMEWORK, ENN_META_VERSION_COMMIT, ENN_META_VERSION_MODEL_COMPILER_NPU is done. 

```cpp
ENN_META_VERSION_FRAMEWORK
ENN_META_VERSION_COMMIT
ENN_META_VERSION_MODEL_COMPILER_NNC
ENN_META_VERSION_MODEL_COMPILER_NPU
ENN_META_VERSION_MODEL_COMPILER_DSP
ENN_META_VERSION_MODEL_SCHEMA
ENN_META_VERSION_MODEL_VERSION
ENN_META_VERSION_DD
ENN_META_VERSION_UNIFIED_FW
ENN_META_VERSION_NPU_FW
ENN_META_VERSION_DSP_FW
```
  * **model_id** 
  * **output_str** 


**Return**: EnnReturn result, 0 is success 

This API includes loaded model information as well as framework information 


#### function EnnSetExecMsgAlwaysOn

```cpp
EnnReturn EnnSetExecMsgAlwaysOn()
```

Set frequency of execution message print. 

**Parameters**: 

  * **rate** if rate is N, the exe msg shows every {1, N+1, 2N+1..} times.


**Return**: EnnReturn 