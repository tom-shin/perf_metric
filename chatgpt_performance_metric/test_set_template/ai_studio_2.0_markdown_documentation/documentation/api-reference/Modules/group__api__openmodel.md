---
title: OpenModel / CloseModel related

---

# OpenModel / CloseModel related



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnOpenModel](Modules/group__api__openmodel.md#function-ennopenmodel)**(const char * model_file, EnnModelId * model_id)<br>OpenModel with model file.  |
| EnnReturn | **[EnnOpenModelFromMemory](Modules/group__api__openmodel.md#function-ennopenmodelfrommemory)**(const char * va, const uint32_t size, EnnModelId * model_id)<br>OpenModel from memory buffer.  |


## Functions Documentation

### function EnnOpenModel

```
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

### function EnnOpenModelFromMemory

```
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





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900