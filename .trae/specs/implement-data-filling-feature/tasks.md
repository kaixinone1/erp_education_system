# Tasks

## 第一阶段：完善前端组件
- [ ] Task 1: 完善DataFilling.vue组件
  - [ ] SubTask 1.1: 实现模板选择功能，从API获取模板列表
  - [ ] SubTask 1.2: 实现统计类型切换（单位/个人）
  - [ ] SubTask 1.3: 集成UnitTreeSelect组件，实现单位多选功能
  - [ ] SubTask 1.4: 实现教师搜索功能（姓名/身份证/教师ID）
  - [ ] SubTask 1.5: 实现步骤导航（上一步/下一步）
  - [ ] SubTask 1.6: 实现表单验证逻辑

- [ ] Task 2: 完善FieldMapping.vue组件
  - [ ] SubTask 2.1: 实现字段映射列表显示
  - [ ] SubTask 2.2: 实现添加映射功能
  - [ ] SubTask 2.3: 实现编辑映射功能（对话框）
  - [ ] SubTask 2.4: 实现删除映射功能
  - [ ] SubTask 2.5: 实现自动生成映射（从模板元数据）
  - [ ] SubTask 2.6: 实现数据源表选择下拉框
  - [ ] SubTask 2.7: 实现统计方式选择下拉框

- [ ] Task 3: 完善UnitTreeSelect.vue组件
  - [ ] SubTask 3.1: 实现树形结构显示（5级层级）
  - [ ] SubTask 3.2: 实现复选框多选功能
  - [ ] SubTask 3.3: 实现搜索过滤功能
  - [ ] SubTask 3.4: 实现全选/反选/清空功能
  - [ ] SubTask 3.5: 实现已选择单位显示和删除功能
  - [ ] SubTask 3.6: 实现层级标签显示（省/地级市/县/镇/校）

## 第二阶段：完善后端API
- [ ] Task 4: 完善fill_service.py服务
  - [ ] SubTask 4.1: 实现获取字段映射配置方法
  - [ ] SubTask 4.2: 实现保存字段映射配置方法
  - [ ] SubTask 4.3: 实现数据提取方法（单位统计）
  - [ ] SubTask 4.4: 实现数据提取方法（个人统计）
  - [ ] SubTask 4.5: 实现数据填报方法
  - [ ] SubTask 4.6: 实现统计计算方法（求和、计数、平均等）

- [ ] Task 5: 完善unified_template_routes.py路由
  - [ ] SubTask 5.1: 完善字段映射配置API
  - [ ] SubTask 5.2: 实现数据提取API
  - [ ] SubTask 5.3: 实现数据填报API
  - [ ] SubTask 5.4: 实现预览数据API

## 第三阶段：实现数据填报逻辑
- [ ] Task 6: 实现数据提取功能
  - [ ] SubTask 6.1: 根据字段映射配置构建SQL查询
  - [ ] SubTask 6.2: 实现多表关联查询
  - [ ] SubTask 6.3: 实现字段计算和转换
  - [ ] SubTask 6.4: 实现日期格式化
  - [ ] SubTask 6.5: 实现字典值转换

- [ ] Task 7: 实现数据填报功能
  - [ ] SubTask 7.1: 加载模板文件
  - [ ] SubTask 7.2: 根据字段位置填入数据
  - [ ] SubTask 7.3: 处理合并单元格
  - [ ] SubTask 7.4: 保存填报后的文件

## 第四阶段：实现预览和确认
- [ ] Task 8: 实现预览功能
  - [ ] SubTask 8.1: 实现填报结果预览显示
  - [ ] SubTask 8.2: 实现提取数据详情显示
  - [ ] SubTask 8.3: 实现模板预览（已填入数据）

- [ ] Task 9: 实现确认和保存
  - [ ] SubTask 9.1: 实现确认填报功能
  - [ ] SubTask 9.2: 实现保存填报记录
  - [ ] SubTask 9.3: 实现生成填报文件
  - [ ] SubTask 9.4: 实现取消操作功能

## 第五阶段：测试和优化
- [ ] Task 10: 功能测试
  - [ ] SubTask 10.1: 测试单位统计流程
  - [ ] SubTask 10.2: 测试个人统计流程
  - [ ] SubTask 10.3: 测试字段映射配置
  - [ ] SubTask 10.4: 测试数据提取和填报
  - [ ] SubTask 10.5: 测试预览和确认

- [ ] Task 11: 性能优化
  - [ ] SubTask 11.1: 优化大数据量查询性能
  - [ ] SubTask 11.2: 优化前端渲染性能
  - [ ] SubTask 11.3: 添加加载提示和进度显示

# Task Dependencies
- Task 2 depends on Task 1
- Task 4 depends on Task 1
- Task 5 depends on Task 4
- Task 6 depends on Task 4
- Task 7 depends on Task 6
- Task 8 depends on Task 7
- Task 9 depends on Task 8
- Task 10 depends on Task 9
- Task 11 depends on Task 10
