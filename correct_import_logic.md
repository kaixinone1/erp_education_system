# 正确的导入逻辑

## 1. 真实字典表分析

### dict_data_dictionary（真实人才类型字典）
- 结构：code, 人才类型, created_at, updated_at
- 数据：
  - code='专业技术人才', 人才类型='专业技术人才'
  - code='技术人才', 人才类型='技术人才'
  - code='管理人员', 人才类型='管理人员'
  - code='退休人员', 人才类型='退休人员'

### dict_data_personal_identity（个人身份字典）
- 结构：id, code, name, sort_order, status, created_at
- 数据：
  - id=1, code='干部', name='干部'
  - id=2, code='工人', name='工人'

## 2. 关联原理

```
Excel中的值 → 值映射 → 字典表.code → 字典表.id/name

例如：
Excel: "1" 
  ↓ 值映射
映射为: "专业技术人才"
  ↓ 查找
字典表: code="专业技术人才" → id=?, 人才类型="专业技术人才"
  ↓ 存储
子表: talent_type_id=?, talent_type_name="专业技术人才", talent_type_code="专业技术人才"
```

## 3. 需要用户配置的值映射

用户需要在字段配置中指定：
- 原始值 `1` 对应字典的哪个code？
- 原始值 `2` 对应字典的哪个code？

例如：
```
1 → 专业技术人才
2 → 技术人才
3 → 管理人员
4 → 退休人员
```

## 4. 关键修改

1. 使用 `dict_data_dictionary` 而不是 `dict_talent_type`
2. 字段名是 `人才类型` 而不是 `name`
3. 需要用户配置值映射关系
