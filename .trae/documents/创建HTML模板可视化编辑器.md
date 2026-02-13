## 计划：创建HTML模板可视化编辑器

### 功能描述
创建一个可视化编辑器，让用户可以在HTML表格上点击需要填写的位置，自动生成input元素。

### 实现步骤

#### 1. 创建HTML模板编辑器组件
- 路径：`frontend/src/views/html-template-editor/index.vue`
- 功能：
  - 左侧：HTML预览（iframe或div）
  - 右侧：字段列表
  - 点击HTML中的单元格，弹出对话框输入字段名称
  - 自动在该位置插入input元素

#### 2. 添加编辑器路由
- 在 `router/index.ts` 中添加 `/html-template-editor/:id` 路由

#### 3. 修改模板管理页面
- HTML文件点击"标记字段"时跳转到新的HTML编辑器

#### 4. 后端API
- 创建 `/api/templates/{id}/html-fields` 接口保存字段配置
- 创建 `/api/templates/{id}/generate-form` 接口生成可填写HTML

#### 5. 实现点击添加输入框功能
- 在iframe中加载HTML
- 捕获点击事件，获取点击的td元素
- 弹出对话框让用户输入字段名称
- 在td中插入input元素

#### 6. 实现保存功能
- 保存字段配置到数据库
- 生成新的可填写HTML文件

### 预计时间
约30-40分钟完成