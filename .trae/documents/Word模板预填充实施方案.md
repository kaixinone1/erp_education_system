## 功能设计

### 模块结构
```
报表管理（主模块）
├── 模板管理（新增子模块）
│   ├── 上传模板
│   ├── 配置占位符
│   ├── 预览测试
│   └── 删除模板
├── 退休业务（已有子模块）
│   └── 使用模板生成报表
```

### 模板管理功能

1. **模板列表**
   - 显示所有已上传的Word模板
   - 模板名称、类型、创建时间
   - 操作：编辑、删除、下载

2. **上传模板**
   - 上传Word文件（.doc/.docx）
   - 输入模板名称（如"退休呈报表"）
   - 选择模板类型（退休业务、职务升降等）

3. **配置占位符**
   - 自动识别Word中的 `{{xxx}}` 占位符
   - 配置每个占位符对应的数据库字段
   - 示例：
     - `{{姓名}}` → `teacher_name`
     - `{{身份证号}}` → `id_card`

4. **预览测试**
   - 选择教师进行测试
   - 查看填充后的效果
   - 确认配置正确

### 数据库表

```sql
CREATE TABLE document_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,           -- 模板名称
    type VARCHAR(50) NOT NULL,            -- 模板类型（退休业务、职务升降等）
    file_path VARCHAR(255) NOT NULL,      -- Word文件路径
    placeholders JSONB,                   -- 占位符配置
    description TEXT,                     -- 描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 使用流程

1. 进入"报表管理"→"模板管理"
2. 点击"上传模板"
3. 选择退休呈报表Word文件
4. 系统自动识别 `{{xxx}}` 占位符
5. 配置每个占位符对应的数据字段
6. 保存模板
7. 在"退休业务"模块中使用该模板生成报表

您觉得这个设计方案如何？需要我实施吗？