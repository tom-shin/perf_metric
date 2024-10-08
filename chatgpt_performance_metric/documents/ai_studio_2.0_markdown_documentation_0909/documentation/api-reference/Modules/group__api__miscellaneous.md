---
title: Security, preference, get meta information..

---

# Security, preference, get meta information..



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnSetPreferencePresetId](Modules/group__api__miscellaneous.md#function-ennsetpreferencepresetid)**(const uint32_t val)<br>Setting Preset ID for operation performance.  |
| EnnReturn | **[EnnSetPreferencePerfConfigId](Modules/group__api__miscellaneous.md#function-ennsetpreferenceperfconfigid)**(const uint32_t val)<br>Setting PerfConfig ID for operation performance.  |
| EnnReturn | **[EnnSetPreferencePerfMode](Modules/group__api__miscellaneous.md#function-ennsetpreferenceperfmode)**(const uint32_t val)<br>Setting Performance Mode.  |
| EnnReturn | **[EnnSetPreferenceTimeOut](Modules/group__api__miscellaneous.md#function-ennsetpreferencetimeout)**(const uint32_t val)<br>Setting Preset ID for time out.  |
| EnnReturn | **[EnnSetPreferencePriority](Modules/group__api__miscellaneous.md#function-ennsetpreferencepriority)**(const uint32_t val)<br>Setting priority value for NPU.  |
| EnnReturn | **[EnnSetPreferenceCoreAffinity](Modules/group__api__miscellaneous.md#function-ennsetpreferencecoreaffinity)**(const uint32_t val)<br>Setting affinity to set NPU core operation.  |
| EnnReturn | **[EnnGetPreferencePresetId](Modules/group__api__miscellaneous.md#function-enngetpreferencepresetid)**(uint32_t * val_ptr)<br>Get current information for Preset ID.  |
| EnnReturn | **[EnnGetPreferencePerfConfigId](Modules/group__api__miscellaneous.md#function-enngetpreferenceperfconfigid)**(uint32_t * val_ptr)<br>Get current information for PerfConfig ID.  |
| EnnReturn | **[EnnGetPreferencePerfMode](Modules/group__api__miscellaneous.md#function-enngetpreferenceperfmode)**(uint32_t * val_ptr)<br>Get current information for Performance Mode.  |
| EnnReturn | **[EnnGetPreferenceTimeOut](Modules/group__api__miscellaneous.md#function-enngetpreferencetimeout)**(uint32_t * val_ptr)<br>Get current information for Time Out.  |
| EnnReturn | **[EnnGetPreferencePriority](Modules/group__api__miscellaneous.md#function-enngetpreferencepriority)**(uint32_t * val_ptr)<br>Get current information for NPU Priority.  |
| EnnReturn | **[EnnGetPreferenceCoreAffinity](Modules/group__api__miscellaneous.md#function-enngetpreferencecoreaffinity)**(uint32_t * val_ptr)<br>Get current information for NPU Core affinity.  |
| EnnReturn | **[EnnGetMetaInfo](Modules/group__api__miscellaneous.md#function-enngetmetainfo)**(const EnnMetaTypeId info_id, const EnnModelId model_id, char output_str[ENN_INFO_GRAPH_STR_LENGTH_MAX])<br>Get Meta Information.  |
| EnnReturn | **[EnnSetExecMsgAlwaysOn](Modules/group__api__miscellaneous.md#function-ennsetexecmsgalwayson)**()<br>Set frequency of execution message print.  |


## Functions Documentation

### function EnnSetPreferencePresetId

```
EnnReturn EnnSetPreferencePresetId(
    const uint32_t val
)
```

Setting Preset ID for operation performance. 

**Parameters**: 

  * **val** [IN] value to set preset ID


**Return**: EnnReturn result, 0 is success 

### function EnnSetPreferencePerfConfigId

```
EnnReturn EnnSetPreferencePerfConfigId(
    const uint32_t val
)
```

Setting PerfConfig ID for operation performance. 

**Parameters**: 

  * **val** [IN] value to set PerfConfig ID


**Return**: EnnReturn result, 0 is success 

### function EnnSetPreferencePerfMode

```
EnnReturn EnnSetPreferencePerfMode(
    const uint32_t val
)
```

Setting Performance Mode. 

**Parameters**: 

  * **val** [IN] value to set Performance Mode


**Return**: EnnReturn result, 0 is success 

### function EnnSetPreferenceTimeOut

```
EnnReturn EnnSetPreferenceTimeOut(
    const uint32_t val
)
```

Setting Preset ID for time out. 

**Parameters**: 

  * **val** [IN] value to set time out


**Return**: EnnReturn result, 0 is success 

**Note**: in second 

### function EnnSetPreferencePriority

```
EnnReturn EnnSetPreferencePriority(
    const uint32_t val
)
```

Setting priority value for NPU. 

**Parameters**: 

  * **val** [IN] value to set NPU job priority


**Return**: EnnReturn result, 0 is success 

### function EnnSetPreferenceCoreAffinity

```
EnnReturn EnnSetPreferenceCoreAffinity(
    const uint32_t val
)
```

Setting affinity to set NPU core operation. 

**Parameters**: 

  * **val** [IN] value to set affinity


**Return**: EnnReturn result, 0 is success 

**Note**: in second 

### function EnnGetPreferencePresetId

```
EnnReturn EnnGetPreferencePresetId(
    uint32_t * val_ptr
)
```

Get current information for Preset ID. 

**Parameters**: 

  * **val** [OUT] current value of Preset ID


**Return**: EnnReturn result, 0 is success 

### function EnnGetPreferencePerfConfigId

```
EnnReturn EnnGetPreferencePerfConfigId(
    uint32_t * val_ptr
)
```

Get current information for PerfConfig ID. 

**Parameters**: 

  * **val** [OUT] current value of PerfConfig ID


**Return**: EnnReturn result, 0 is success 

### function EnnGetPreferencePerfMode

```
EnnReturn EnnGetPreferencePerfMode(
    uint32_t * val_ptr
)
```

Get current information for Performance Mode. 

**Parameters**: 

  * **val** [OUT] current value of Performance Mode


**Return**: EnnReturn result, 0 is success 

### function EnnGetPreferenceTimeOut

```
EnnReturn EnnGetPreferenceTimeOut(
    uint32_t * val_ptr
)
```

Get current information for Time Out. 

**Parameters**: 

  * **val** [OUT] current value of Time Out


**Return**: EnnReturn result, 0 is success 

### function EnnGetPreferencePriority

```
EnnReturn EnnGetPreferencePriority(
    uint32_t * val_ptr
)
```

Get current information for NPU Priority. 

**Parameters**: 

  * **val** [OUT] current value of NPU Priority


**Return**: EnnReturn result, 0 is success 

### function EnnGetPreferenceCoreAffinity

```
EnnReturn EnnGetPreferenceCoreAffinity(
    uint32_t * val_ptr
)
```

Get current information for NPU Core affinity. 

**Parameters**: 

  * **val** [OUT] current value of NPU Core affinity


**Return**: EnnReturn result, 0 is success 

### function EnnGetMetaInfo

```
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


### function EnnSetExecMsgAlwaysOn

```
EnnReturn EnnSetExecMsgAlwaysOn()
```

Set frequency of execution message print. 

**Parameters**: 

  * **rate** if rate is N, the exe msg shows every {1, N+1, 2N+1..} times.


**Return**: EnnReturn 





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900