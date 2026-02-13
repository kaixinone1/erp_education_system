## 问题原因

`import_routes.py` 调用了 `validation_service.validate_data()` 方法，但我重写的 `validation_service.py` 中没有这个方法，只有：
- `validate_row()` - 验证单行
- `validate_all()` - 验证所有数据

## 解决方案

在 `ValidationService` 类中添加 `validate_data` 方法，兼容原有的调用方式。

## 修改内容

在 `validation_service.py` 的 `ValidationService` 类中添加：

```python
def validate_data(self, data: List[Dict], field_configs: List[Dict], 
                  validation_level: int = 3, reference_data: Optional[Dict] = None) -> Dict[str, Any]:
    """验证数据（兼容旧接口）"""
    # 调用 validate_all 进行验证
    results = self.validate_all(data, field_configs)
    
    # 转换结果为旧格式
    errors = []
    for i, result in enumerate(results):
        for error in result.errors:
            errors.append({
                "row": i + 1,
                "field": error.field,
                "message": error.message,
                "level": error.level
            })
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "total_rows": len(data),
        "error_count": len(errors)
    }
```

请确认后开始修改。