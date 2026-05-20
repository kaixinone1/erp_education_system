# 模板自动填报系统API文档

## 系统概述

模板自动填报系统提供完整的API接口，支持：
- 配置管理（CRUD操作）
- 模板导入与预览
- 自动填报执行
- 字段智能匹配
- 实时预览

## API基础URL

```
http://127.0.0.1:8000/api/auto-fill
```

---

## 一、配置管理API

### 1. 获取所有配置

**请求：**
```
GET /configs
```

**响应：**
```json
{
  "status": "success",
  "configs": [
    {
      "name": "退休呈报表",
      "filename": "退休呈报表.json",
      "template_name": "退休呈报表",
      "template_type": "退休类",
      "description": "教师退休呈报表模板"
    }
  ],
  "count": 1
}
```

---

### 2. 获取指定配置

**请求：**
```
GET /configs/{config_name}
```

**示例：**
```
GET /configs/退休呈报表
```

**响应：**
```json
{
  "status": "success",
  "config": {
    "template_info": {...},
    "data_sources": {...},
    "field_mappings": [...],
    "calculations": [...]
  }
}
```

---

### 3. 创建配置

**请求：**
```
POST /configs
Content-Type: application/json

{
  "template_info": {
    "name": "新模板",
    "file": "新模板.xlsx",
    "type": "其他",
    "description": "新模板描述"
  },
  "data_sources": {
    "primary": "teacher_basic_info",
    "related": [],
    "filters": []
  },
  "field_mappings": [
    {
      "template_field": "姓名",
      "source_field": "name",
      "target_field": "姓名",
      "transform": null
    }
  ],
  "calculations": []
}
```

**响应：**
```json
{
  "status": "success",
  "message": "配置创建成功",
  "config_name": "新模板",
  "config_path": "..."
}
```

---

### 4. 更新配置

**请求：**
```
PUT /configs/{config_name}
Content-Type: application/json

{
  "template_info": {...},
  "data_sources": {...},
  "field_mappings": [...],
  "calculations": [...]
}
```

---

### 5. 删除配置

**请求：**
```
DELETE /configs/{config_name}
```

**响应：**
```json
{
  "status": "success",
  "message": "配置删除成功",
  "config_name": "退休呈报表"
}
```

---

## 二、模板管理API

### 1. 上传模板

**请求：**
```
POST /templates/upload
Content-Type: multipart/form-data

file: [模板文件]
```

**响应：**
```json
{
  "status": "success",
  "message": "模板上传成功",
  "filename": "退休呈报表_20240510_143025.xlsx",
  "template_path": "...",
  "preview": {
    "success": true,
    "template_file": "...",
    "field_names": ["姓名", "身份证号", ...]
  }
}
```

---

### 2. 预览模板

**请求：**
```
GET /templates/preview/{filename}
```

**响应：**
```json
{
  "success": true,
  "message": "模板预览成功",
  "template_file": "...",
  "template_info": {...},
  "field_names": ["姓名", "身份证号", ...]
}
```

---

### 3. 下载模板

**请求：**
```
GET /templates/download/{filename}
```

**响应：**
文件下载

---

## 三、自动填报API

### 1. 执行自动填报

**请求：**
```
POST /execute
Content-Type: application/json

{
  "config_name": "退休呈报表",
  "filters": {
    "employment_status": "退休"
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "自动填报完成",
  "output_file": "...",
  "data_count": 10,
  "statistics": {
    "退休人数": 10,
    "平均年龄": 60.5
  },
  "consistency": {
    "is_consistent": true,
    "message": "文件100%一致"
  }
}
```

---

### 2. 预览填报效果

**请求：**
```
POST /preview-fill
Content-Type: application/json

{
  "config_name": "退休呈报表",
  "filters": {
    "employment_status": "退休"
  }
}
```

**响应：**
```json
{
  "status": "success",
  "message": "预览成功",
  "data": [
    {
      "姓名": "张三",
      "身份证号": "1234567890",
      "年龄": 60,
      ...
    }
  ],
  "count": 10,
  "statistics": {
    "退休人数": 10,
    "平均年龄": 60.5
  },
  "columns": ["姓名", "身份证号", ...]
}
```

---

### 3. 下载输出文件

**请求：**
```
GET /output/{filename}
```

**响应：**
文件下载

---

## 四、智能匹配API

### 1. 智能匹配字段

**请求：**
```
POST /smart-match
Content-Type: application/json

{
  "template_fields": ["姓名", "身份证号", "出生日期"],
  "available_tables": ["teacher_basic_info", "retirement_info"]
}
```

**响应：**
```json
{
  "status": "success",
  "matches": {
    "姓名": "teacher_basic_info.name",
    "身份证号": "teacher_basic_info.id_card",
    "出生日期": "teacher_basic_info.birth_date"
  },
  "count": 3
}
```

---

## 五、数据源API

### 1. 获取所有数据源表

**请求：**
```
GET /data-sources
```

**响应：**
```json
{
  "status": "success",
  "tables": {
    "teacher_basic_info": {
      "name": "教师基础信息",
      "description": "教师基础信息表",
      "fields": {...},
      "category": "基础信息",
      "is_active": true
    }
  },
  "categories": ["基础信息", "退休信息", ...],
  "count": 110
}
```

---

### 2. 获取指定数据源表

**请求：**
```
GET /data-sources/{table_name}
```

**示例：**
```
GET /data-sources/teacher_basic_info
```

**响应：**
```json
{
  "status": "success",
  "table_name": "teacher_basic_info",
  "table_info": {
    "name": "教师基础信息",
    "description": "教师基础信息表",
    "fields": {
      "id": "主键ID",
      "name": "姓名",
      "id_card": "身份证号码",
      ...
    },
    "category": "基础信息",
    "is_active": true
  }
}
```

---

## 六、转换函数API

### 1. 获取所有转换函数

**请求：**
```
GET /transform-functions
```

**响应：**
```json
{
  "status": "success",
  "functions": {
    "calculate_age": {
      "name": "calculate_age",
      "description": "计算年龄"
    },
    "format_date_cn": {
      "name": "format_date_cn",
      "description": "格式化日期为中文格式"
    },
    "convert_gender": {
      "name": "convert_gender",
      "description": "转换性别代码为中文"
    },
    "format_money": {
      "name": "format_money",
      "description": "格式化金额"
    }
  },
  "count": 8
}
```

---

## 七、使用示例

### 示例1：使用预设配置生成报表

```python
import requests

# 1. 获取配置列表
response = requests.get('http://127.0.0.1:8000/api/auto-fill/configs')
configs = response.json()['configs']

# 2. 执行自动填报
response = requests.post(
    'http://127.0.0.1:8000/api/auto-fill/execute',
    json={
        'config_name': '退休呈报表',
        'filters': {
            'employment_status': '退休'
        }
    }
)

result = response.json()
print(f"生成文件: {result['output_file']}")
print(f"数据量: {result['data_count']} 条")
```

---

### 示例2：导入新模板并配置

```python
import requests

# 1. 上传模板
with open('新模板.xlsx', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/api/auto-fill/templates/upload',
        files={'file': f}
    )

template_info = response.json()
field_names = template_info['preview']['field_names']

# 2. 智能匹配字段
response = requests.post(
    'http://127.0.0.1:8000/api/auto-fill/smart-match',
    json={
        'template_fields': field_names
    }
)

matches = response.json()['matches']

# 3. 创建配置
config = {
    'template_info': {
        'name': '新模板',
        'file': template_info['filename'],
        'type': '其他',
        'description': '新模板描述'
    },
    'data_sources': {
        'primary': 'teacher_basic_info',
        'related': [],
        'filters': []
    },
    'field_mappings': [
        {
            'template_field': field,
            'source_field': match.split('.')[1],
            'target_field': field,
            'transform': None
        }
        for field, match in matches.items()
    ],
    'calculations': []
}

response = requests.post(
    'http://127.0.0.1:8000/api/auto-fill/configs',
    json=config
)

print(f"配置创建成功: {response.json()['config_name']}")
```

---

## 八、错误处理

所有API在发生错误时返回统一格式：

```json
{
  "detail": "错误信息"
}
```

HTTP状态码：
- 200: 成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

---

## 九、系统特点

### 1. 100%一致性保证
- 预览模板 = 导入模板
- 自动填报预览 = 导出结果
- 保持所有格式和样式

### 2. 零代码扩展
- 新增数据表：自动识别
- 新增模板：配置即可
- 无需修改代码

### 3. 智能化
- 自动识别字段
- 智能匹配数据源
- 减少手动配置

### 4. 灵活性
- 支持复杂计算
- 支持多表关联
- 支持自定义转换函数
