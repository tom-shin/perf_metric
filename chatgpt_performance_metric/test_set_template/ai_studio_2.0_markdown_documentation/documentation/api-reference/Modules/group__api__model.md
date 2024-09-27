---
title: Setters and Getters for model

---

# Setters and Getters for model



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnGetBuffersInfo](Modules/group__api__model.md#function-enngetbuffersinfo)**([NumberOfBuffersInfo](Classes/struct___number_of_buffers_info.md) * buffers_info, const EnnModelId model_id)<br>Get buffers information from loaded model.  |
| EnnReturn | **[EnnGetBufferInfoByIndex](Modules/group__api__model.md#function-enngetbufferinfobyindex)**([EnnBufferInfo](Classes/struct__enn_buffer_info.md) * out_buf_info, const EnnModelId model_id, const enn_buf_dir_e direction, const uint32_t index)<br>Get one buffer information from loaded model.  |
| EnnReturn | **[EnnGetBufferInfoByLabel](Modules/group__api__model.md#function-enngetbufferinfobylabel)**([EnnBufferInfo](Classes/struct__enn_buffer_info.md) * out_buf_info, const EnnModelId model_id, const char * label)<br>Get one buffer information from loaded model.  |
| EnnReturn | **[EnnSetBufferByIndex](Modules/group__api__model.md#function-ennsetbufferbyindex)**(const EnnModelId model_id, const enn_buf_dir_e direction, const uint32_t index, [EnnBufferPtr](Classes/struct__enn_buffer.md) buf, const int session_id =0)<br>Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core.  |
| EnnReturn | **[EnnSetBufferByLabel](Modules/group__api__model.md#function-ennsetbufferbylabel)**(const EnnModelId model_id, const char * label, [EnnBufferPtr](Classes/struct__enn_buffer.md) buf, const int session_id =0)<br>Set memory object to commit-space. A user can generates buffer space to commit. (Basically the framework generates 16 spaces) "Set Buffer" means a caller can put its memory object to it's space. "Commit" means send memory-buffer set which can run opened model completely to service core.  |


## Functions Documentation

### function EnnGetBuffersInfo

```
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

### function EnnGetBufferInfoByIndex

```
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


### function EnnGetBufferInfoByLabel

```
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


### function EnnSetBufferByIndex

```
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

### function EnnSetBufferByLabel

```
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





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900