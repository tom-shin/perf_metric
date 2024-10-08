---
title: Memory Handling

---

# Memory Handling



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnCreateBuffer](Modules/group__api__memory.md#function-enncreatebuffer)**([EnnBufferPtr](Classes/struct__enn_buffer.md) * out, const uint32_t req_size, const bool is_cached =true)<br>Create Buffer with request size support ION or dmabufheap which can be used in a device(DSP/CPU/NPU/GPU)  |
| EnnReturn | **[EnnAllocateAllBuffers](Modules/group__api__memory.md#function-ennallocateallbuffers)**(const EnnModelId model_id, [EnnBufferPtr](Classes/struct__enn_buffer.md) ** out_buffers, [NumberOfBuffersInfo](Classes/struct___number_of_buffers_info.md) * buf_info, const int session_id =0, const bool do_commit =true)<br>Allocate all buffers which a caller should allocate.  |
| EnnReturn | **[EnnReleaseBuffers](Modules/group__api__memory.md#function-ennreleasebuffers)**([EnnBufferPtr](Classes/struct__enn_buffer.md) * buffers, const int32_t numOfBuffers)<br>Release buffer array from EnnAllocatedAllBuffers() This API includes releasing all elements in the array.  |
| EnnReturn | **[EnnReleaseBuffer](Modules/group__api__memory.md#function-ennreleasebuffer)**([EnnBufferPtr](Classes/struct__enn_buffer.md) buffer)<br>release buffer from [EnnCreateBuffer()](Modules/group__api__memory.md#function-enncreatebuffer) |


## Functions Documentation

### function EnnCreateBuffer

```
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

### function EnnAllocateAllBuffers

```
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

### function EnnReleaseBuffers

```
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

### function EnnReleaseBuffer

```
EnnReturn EnnReleaseBuffer(
    EnnBufferPtr buffer
)
```

release buffer from [EnnCreateBuffer()](Modules/group__api__memory.md#function-enncreatebuffer)

**Parameters**: 

  * **buffer** [IN] buffer object from [EnnCreateBuffer()](Modules/group__api__memory.md#function-enncreatebuffer)


**Return**: EnnReturn result, 0 is success 





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900