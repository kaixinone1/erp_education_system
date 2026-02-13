## 实施计划

### 第一步：扩展前端上传组件
修改 `FileSelectionPanel.vue`：
- 将 `accept=".xlsx,.xls,.csv"` 改为 `accept=".xlsx,.xls,.csv,.doc,.docx"`
- 更新提示文字

### 第二步：增强后端文件解析服务
修改 `backend/services/file_parser.py`：
- 安装 `python-docx` 库
- 添加 `parse_word_document()` 函数
- 提取 Word 表格数据并转换为标准结构

### 第三步：配置报表模板
创建 `report_definitions.json`：
- 定义退休呈报表等 Word 模板
- 配置页面设置（页边距、纸张方向等）
- 使用 python-docx 渲染模板

## 检查点
1. 前端可以选择 .doc/.docx 文件
2. 后端能正确解析 Word 表格数据
3. 导出时格式规范、页面设置正确