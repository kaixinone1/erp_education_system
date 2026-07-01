# Debug Session: auto-fill-no-data

## Status: [OPEN]

## Symptom
- 通用模板系统 → 配置映射 → 配置字段 → 自动填报 → 没有获取到数据

## Expected Behavior
- 自动填报应根据字段映射从数据库查询到数据并填充模板

## Environment
- Backend: http://localhost:8000 (Python FastAPI)
- Frontend: http://localhost:5173 (Vue + Vite)
- Date: 2026-05-27

## Hypotheses

### H1: 字段映射的 convert_chinese_to_english_fields 转换失败
数据源字段名（中文）无法在 merged_schema_mappings.json 中找到映射，导致转换返回空值，SQL 查询条件为空。

### H2: 数据库查询返回空结果
字段映射正确，但数据库表中确实没有匹配的数据。

### H3: 最近修改 merged_schema_mappings.json 导致字段类型不匹配
之前修正 dict_salary_dictionary 和 personal_dict_salary_dictionary 时可能引入了格式问题。

### H4: 前端自动填报请求参数不正确
前端构建的请求参数（模板ID、查询条件、统计范围等）不完整或格式错误。

### H5: 模板引擎 load_field_mappings 读取的映射数据不完整
保存的字段映射缺少关键字段（如数据源、行号、列号等），导致后端无法执行查询。

---

## Log Collection Plan
- 插桩点1: `/api/universal-template/fill` 入口 — 记录请求参数
- 插桩点2: `convert_chinese_to_english_fields` — 记录转换前后对照
- 插桩点3: SQL 查询生成 — 记录生成的SQL和参数
- 插桩点4: 数据库查询结果 — 记录返回行数
- 插桩点5: 前端API响应 — 记录后端返回的完整数据

## Timeline
- 2026-05-27 开始调试