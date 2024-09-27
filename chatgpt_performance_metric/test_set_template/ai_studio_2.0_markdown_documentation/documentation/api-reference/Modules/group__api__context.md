---
title: Context initialize / deinitialize

---

# Context initialize / deinitialize



## Functions

|                | Name           |
| -------------- | -------------- |
| EnnReturn | **[EnnInitialize](Modules/group__api__context.md#function-enninitialize)**(void )<br>Initialize Enn Framework. Framework generates context in a caller's process. Context counts initialize/deinitialize pair.  |
| EnnReturn | **[EnnDeinitialize](Modules/group__api__context.md#function-enndeinitialize)**(void )<br>Deinitialize Enn Framework. Framework degenerates context in a caller's process.  |


## Functions Documentation

### function EnnInitialize

```
EnnReturn EnnInitialize(
    void 
)
```

Initialize Enn Framework. Framework generates context in a caller's process. Context counts initialize/deinitialize pair. 

**Return**: EnnReturn result, 0 is success 

### function EnnDeinitialize

```
EnnReturn EnnDeinitialize(
    void 
)
```

Deinitialize Enn Framework. Framework degenerates context in a caller's process. 

**Return**: EnnReturn result, 0 is success 





-------------------------------

Updated on 2023-08-11 at 16:24:05 +0900