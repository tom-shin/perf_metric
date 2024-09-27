---
title: Commit Buffer

---

# Commit Buffer



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnBufferCommit](Modules/group__api__commit.md#function-ennbuffercommit)**(const EnnModelId model_id, const int session_id =0)<br>Send buffer-set to service core. session_id indicates which buffer space should be sent. The committed buffers are released if a caller calls CloseModel()  |


## Functions Documentation

### function EnnBufferCommit

```
EnnReturn EnnBufferCommit(
    const EnnModelId model_id,
    const int session_id =0
)
```

Send buffer-set to service core. session_id indicates which buffer space should be sent. The committed buffers are released if a caller calls CloseModel() 

**Parameters**: 

  * **model_id** [IN] model ID from load_model


**Return**: EnnReturn result, 0 is success 





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900