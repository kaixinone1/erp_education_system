# 数据填报功能 Spec

## Why
模板管理系统需要一个完整的数据填报功能，让用户能够根据模板自动从数据库中提取数据并填入模板，支持单位统计和个人统计两种模式，实现模板与数据库字段的智能映射。

## What Changes
- 完善数据填报流程（4个步骤）
- 实现字段映射配置功能
- 实现数据提取和填报逻辑
- 实现预览和确认功能
- 支持单位统计和个人统计
- 支持多种统计方式（直接取值、求和、计数、平均等）

## Impact
- 受影响的功能：模板管理、数据填报、字段映射
- 受影响的代码：
  - `frontend/src/views/template/components/DataFilling.vue`
  - `frontend/src/views/template/components/FieldMapping.vue`
  - `frontend/src/views/template/components/UnitTreeSelect.vue`
  - `backend/services/fill_service.py`
  - `backend/routes/unified_template_routes.py`

## ADDED Requirements

### Requirement: 数据填报流程
系统应提供完整的数据填报流程，包括4个步骤：
1. 选择模板
2. 选择统计类型（单位/个人）
3. 字段映射配置
4. 预览确认

#### Scenario: 单位统计数据填报
- **WHEN** 用户选择"单位统计"模式
- **THEN** 系统应显示单位树形选择器，支持多选单位
- **AND** 系统应自动提取所选单位的所有人员数据
- **AND** 系统应根据字段映射配置填充模板

#### Scenario: 个人统计数据填报
- **WHEN** 用户选择"个人统计"模式
- **THEN** 系统应提供教师搜索功能（姓名/身份证/教师ID）
- **AND** 系统应自动提取所选教师的个人数据
- **AND** 系统应根据字段映射配置填充模板

### Requirement: 字段映射配置
系统应提供灵活的字段映射配置功能：
- 支持手动配置字段映射
- 支持编辑、删除、添加映射
- 支持多种统计方式
- 支持自定义公式

#### Scenario: 字段映射编辑
- **WHEN** 用户点击"编辑"按钮
- **THEN** 系统应打开编辑对话框
- **AND** 显示字段位置、字段名称、数据源表、目标字段、统计方式等选项
- **AND** 用户可以修改配置并保存

#### Scenario: 统计方式选择
- **WHEN** 用户选择统计方式
- **THEN** 系统应提供以下选项：
  - 直接取值
  - 求和
  - 计数
  - 平均
  - 最大值
  - 最小值
  - 格式化日期
  - 格式化数字

### Requirement: 数据提取和填报
系统应根据字段映射配置自动提取数据并填入模板：
- 支持从多个数据源表提取数据
- 支持字段间的计算和转换
- 支持日期格式化
- 支持字典值转换

#### Scenario: 数据提取成功
- **WHEN** 用户完成字段映射配置并点击"下一步"
- **THEN** 系统应根据映射配置从数据库提取数据
- **AND** 系统应将数据填入模板对应位置
- **AND** 系统应显示预览结果

#### Scenario: 数据提取失败
- **WHEN** 数据提取过程中发生错误
- **THEN** 系统应显示错误提示
- **AND** 系统应允许用户修改配置

### Requirement: 预览和确认
系统应提供填报结果预览功能：
- 显示填报后的模板预览
- 显示提取的数据详情
- 支持确认填报或取消操作

#### Scenario: 预览填报结果
- **WHEN** 用户进入预览步骤
- **THEN** 系统应显示填报后的模板预览
- **AND** 显示提取的数据详情
- **AND** 提供"确认填报"和"取消"按钮

#### Scenario: 确认填报
- **WHEN** 用户点击"确认填报"按钮
- **THEN** 系统应保存填报记录
- **AND** 系统应生成填报文件
- **AND** 系统应显示成功提示

## MODIFIED Requirements

### Requirement: 单位选择功能
系统应提供树形结构的单位选择器：
- 支持5级层级（省/地级市/县/镇/校）
- 支持多选和单选
- 支持搜索功能
- 支持全选/反选/清空操作
- 显示完整路径和层级标签

### Requirement: 字段映射API
系统应提供字段映射配置的API：
- GET `/api/template/field-mapping/{template_id}` - 获取字段映射配置
- POST `/api/template/field-mapping/{template_id}` - 保存字段映射配置
- 使用独立的数据库表 `data_filling_field_mappings`

## REMOVED Requirements
无
