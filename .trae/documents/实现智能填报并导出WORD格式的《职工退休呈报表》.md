## 实施计划

### 阶段1：字段自动提取服务（2-3小时）
1. 安装 pdfplumber 和 pytesseract
2. 创建 services/field_extractor.py
3. 实现PDF文本提取和位置识别
4. 识别表格结构（标签-输入框配对）

### 阶段2：智能匹配引擎（3-4小时）
1. 创建 services/field_matcher.py
2. 实现相似度算法（difflib + fuzzywuzzy）
3. 建立同义词库
4. 返回推荐匹配结果

### 阶段3：人工核准界面（4-5小时）
1. 创建 SmartFieldMapping.vue 组件
2. 三栏拖拽式界面（PDF预览、候选字段、系统字段）
3. 显示匹配置信度
4. 保存匹配配置

### 阶段4：数据填充服务（2-3小时）
1. 根据匹配配置查询数据库
2. 处理字典表转换
3. 生成填充后的PDF

用户已批准，开始实施！