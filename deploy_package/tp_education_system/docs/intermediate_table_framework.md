# 通用中间表组件框架设计

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                        通用中间表框架                            │
├─────────────────────────────────────────────────────────────────┤
│  核心思想：配置驱动，代码复用，一次开发，多次使用                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   配置文件      │    │   通用后端引擎   │    │   通用前端组件   │
│  (JSON/YAML)    │───→│  (Python/FastAPI)│───→│   (Vue3)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ↓                       ↓                       ↓
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ - 表结构定义     │    │ - 数据聚合      │    │ - 数据表格      │
│ - 字段映射       │    │ - CRUD操作      │    │ - 编辑表单      │
│ - 数据源配置     │    │ - 导出功能      │    │ - 导出按钮      │
│ - 计算规则       │    │ - 计算引擎      │    │ - 计算弹窗      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 2. 配置文件结构

```json
{
  "table_name": "retirement_report_data",
  "chinese_name": "退休呈报数据",
  "description": "职工退休呈报表数据中间表",
  
  "fields": [
    {
      "name": "姓名",
      "type": "VARCHAR",
      "length": 50,
      "required": true,
      "source": {
        "table": "teacher_basic_info",
        "field": "name"
      }
    },
    {
      "name": "性别",
      "type": "VARCHAR",
      "length": 10,
      "source": {
        "table": "teacher_basic_info",
        "field": "gender"
      }
    },
    {
      "name": "工作年限",
      "type": "INTEGER",
      "calculated": true,
      "formula": "work_years_calculation"
    }
  ],
  
  "calculations": {
    "work_years_calculation": {
      "type": "retirement",
      "inputs": ["出生日期", "性别", "个人身份", "参加工作时间"],
      "outputs": ["原退休日期", "延迟月数", "现退休日期", "工作年限"]
    }
  },
  
  "features": {
    "crud": true,
    "export": ["excel", "word", "pdf"],
    "calculator": true,
    "import": false
  }
}
```

## 3. 后端通用引擎

### 3.1 核心类设计

```python
class IntermediateTableEngine:
    """通用中间表引擎"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.table_name = self.config['table_name']
    
    def aggregate_data(self, teacher_id: int) -> dict:
        """从多个源表聚合数据"""
        pass
    
    def calculate_fields(self, data: dict) -> dict:
        """计算派生字段"""
        pass
    
    def save_to_intermediate_table(self, data: dict):
        """保存到中间表"""
        pass
    
    def export_data(self, format: str, filters: dict) -> bytes:
        """导出数据"""
        pass
```

### 3.2 自动路由生成

```python
def create_intermediate_table_routes(config: dict) -> APIRouter:
    """根据配置自动生成API路由"""
    router = APIRouter(prefix=f"/api/intermediate/{config['table_name']}")
    
    @router.get("/list")
    async def list_data():
        pass
    
    @router.post("/create")
    async def create_data():
        pass
    
    @router.put("/update/{id}")
    async def update_data():
        pass
    
    @router.delete("/delete/{id}")
    async def delete_data():
        pass
    
    @router.post("/calculate")
    async def calculate():
        pass
    
    @router.get("/export/{format}")
    async def export_data():
        pass
    
    return router
```

## 4. 前端通用组件

### 4.1 核心组件设计

```vue
<!-- IntermediateTableManager.vue -->
<template>
  <div class="intermediate-table-manager">
    <!-- 通用按钮栏 -->
    <CommonActionBar 
      :features="config.features"
      @create="handleCreate"
      @export="handleExport"
    />
    
    <!-- 数据表格 -->
    <DataTable 
      :fields="config.fields"
      :data="tableData"
      @edit="handleEdit"
      @delete="handleDelete"
      @calculate="handleCalculate"
    />
    
    <!-- 编辑弹窗 -->
    <EditDialog 
      v-model="editDialogVisible"
      :fields="config.fields"
      :data="currentRow"
      @save="handleSave"
    />
    
    <!-- 计算弹窗 -->
    <CalculatorDialog 
      v-model="calculatorVisible"
      :config="config.calculations"
      :teacher-id="selectedTeacherId"
      @saved="handleRefresh"
    />
  </div>
</template>
```

### 4.2 配置驱动渲染

```typescript
// 根据配置自动生成表格列
const generateColumns = (fields: FieldConfig[]) => {
  return fields.map(field => ({
    prop: field.name,
    label: field.name,
    width: field.length > 20 ? 200 : 120,
    sortable: true
  }))
}

// 根据配置自动生成表单字段
const generateFormFields = (fields: FieldConfig[]) => {
  return fields.map(field => ({
    ...field,
    component: getComponentByType(field.type)
  }))
}
```

## 5. 使用示例

### 5.1 创建新的中间表

**步骤1：创建配置文件**

```json
// config/intermediate_tables/salary_calculation.json
{
  "table_name": "salary_calculation_data",
  "chinese_name": "工资核算数据",
  "fields": [...],
  "calculations": {...}
}
```

**步骤2：后端注册（一行代码）**

```python
# main.py
from intermediate_table_framework import register_intermediate_table

register_intermediate_table("config/intermediate_tables/salary_calculation.json")
```

**步骤3：前端使用（一行代码）**

```vue
<template>
  <IntermediateTableManager table-name="salary_calculation_data" />
</template>
```

## 6. 框架优势

1. **开发效率提升10倍**
   - 新中间表只需配置，无需写代码
   - 从几天缩短到几分钟

2. **维护成本降低**
   - 功能升级只需修改框架
   - 所有中间表自动受益

3. **一致性保证**
   - 统一的UI风格
   - 统一的操作逻辑
   - 统一的导出格式

4. **灵活扩展**
   - 支持自定义计算规则
   - 支持自定义导出模板
   - 支持自定义验证规则
