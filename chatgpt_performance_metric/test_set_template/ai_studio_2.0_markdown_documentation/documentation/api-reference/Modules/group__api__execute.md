---
title: Execute Models

---

# Execute Models



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnExecuteModel](Modules/group__api__execute.md#function-ennexecutemodel)**(const EnnModelId model_id, const int session_id =0)<br>Request to service core to execute model with commited buffers.  |
| EnnReturn | **[EnnExecuteModelAsync](Modules/group__api__execute.md#function-ennexecutemodelasync)**(const EnnModelId model_id, const int session_id =0)<br>Request to service core to execute model in background asynchronously.  |
| EnnReturn | **[EnnExecuteModelWait](Modules/group__api__execute.md#function-ennexecutemodelwait)**(const EnnModelId model_id, const int session_id =0)<br>Wait result of calling [EnnExecuteModelAsync()](Modules/group__api__execute.md#function-ennexecutemodelasync) If execution is finished, this function is returned intermediatelly If not, this function would be blocked until the execution finished.  |


## Functions Documentation

### function EnnExecuteModel

```
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

### function EnnExecuteModelAsync

```
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

### function EnnExecuteModelWait

```
EnnReturn EnnExecuteModelWait(
    const EnnModelId model_id,
    const int session_id =0
)
```

Wait result of calling [EnnExecuteModelAsync()](Modules/group__api__execute.md#function-ennexecutemodelasync) If execution is finished, this function is returned intermediatelly If not, this function would be blocked until the execution finished. 

**Parameters**: 

  * **model_id** [IN] model ID from load_model 
  * **session_id** [IN] session ID


**Return**: EnnReturn result, 0 is success 





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900