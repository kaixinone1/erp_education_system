# 太平镇教育人事管理系统 — Code Wiki

> 项目名称：太平镇教育人事管理系统（TP Education System）
> 最后更新：2026-06-10

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈](#2-技术栈)
3. [项目目录结构](#3-项目目录结构)
4. [后端架构](#4-后端架构)
5. [前端架构](#5-前端架构)
6. [数据库设计](#6-数据库设计)
7. [配置文件体系](#7-配置文件体系)
8. [核心业务流程](#8-核心业务流程)
9. [依赖关系图](#9-依赖关系图)
10. [项目运行方式](#10-项目运行方式)

---

## 1. 项目概述

太平镇教育人事管理系统是一套面向乡镇教育机构的**配置驱动型人事管理平台**，涵盖教师信息管理、工资绩效、退休业务、预警督办、报表管理等功能。

**核心设计理念**：系统的所有行为、外观和数据结构不由代码硬编码，而由外部配置文件定义。配置文件的生成来源于用户数据上传与导入过程。

**主要业务模块**：
- **系统管理** — 模块管理、数据表管理、字典管理、字段配置、数据迁移
- **预警督办** — 待办业务管理、清单模板、到期提醒、历史归档
- **数据中心** — 数据导入工作台、聚合查询、表结构管理、数据清理
- **人事管理** — 教师基本信息、学历信息、职务信息、岗位聘任、退休管理
- **绩效管理** — 绩效工资审批、历史记录、统计报表、标准设置
- **报表管理** — Word/Excel 模板管理、模板填报、报表设计器、通用模板导出

---

## 2. 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| **前端框架** | Vue 3 + TypeScript | 3.4+ |
| **状态管理** | Pinia | 2.1+ |
| **路由** | Vue Router (Hash 模式) | 4.3+ |
| **UI 组件库** | Element Plus（中文语言包） | 2.6+ |
| **图表** | ECharts 5 + vue-echarts | 5.5+ |
| **构建工具** | Vite | 5.2+ |
| **在线表格** | Luckysheet | 2.1 |
| **文档处理** | docx.js / xlsx.js / mammoth.js | — |
| **后端框架** | Python FastAPI | — |
| **ORM** | SQLAlchemy | — |
| **数据库** | PostgreSQL（taiping_education） | — |
| **定时任务** | APScheduler | — |
| **文档生成** | python-docx / openpyxl | — |
| **进程管理** | PM2（可选） | — |

---

## 3. 项目目录结构

```
d:\erp_thirteen/
├── tp_education_system/          # 主应用目录
│   ├── backend/                   # Python 后端
│   │   ├── main.py                # FastAPI 应用入口
│   │   ├── requirements.txt       # Python 依赖
│   │   ├── core/                  # 核心引擎模块
│   │   ├── routes/                # API 路由（32个路由文件）
│   │   ├── services/              # 业务服务（52个服务文件）
│   │   ├── utils/                 # 工具函数
│   │   ├── config/                # JSON 配置文件（35+）
│   │   ├── static/                # 静态文件
│   │   ├── templates/             # Word 模板文件
│   │   └── uploads/               # 上传文件
│   ├── frontend/                  # Vue3 前端
│   │   ├── index.html             # HTML 入口
│   │   ├── package.json           # Node 依赖
│   │   ├── vite.config.ts         # Vite 构建配置
│   │   ├── tsconfig.json          # TypeScript 配置
│   │   └── src/
│   │       ├── main.ts            # 前端入口
│   │       ├── App.vue            # 根组件
│   │       ├── router/            # 路由配置
│   │       ├── store/             # Pinia 状态管理
│   │       ├── utils/             # 前端工具
│   │       ├── config/            # 前端配置
│   │       ├── components/        # 公共组件（Layout/import/data等）
│   │       └── views/             # 页面视图（14个模块）
│   └── 启动全部服务器.bat          # 一键启动脚本
├── 数据库信息/                     # 数据源文件（Excel/Word）
├── 推送清单功能开发/               # 业务文档
├── tools/                         # 第三方工具（poppler PDF工具）
├── backups/                       # 备份文件
├── test_environment/              # 测试环境
└── dev_logs/                      # 开发日志
```

---

## 4. 后端架构

### 4.1 应用入口 — `backend/main.py`

FastAPI 应用，端口 **8000**，负责：
1. 注册 **24 个路由模块**
2. 配置 CORS（允许跨域）
3. 挂载静态文件服务（模板文件 / 上传文件）
4. 加载导航配置（`navigation.json`），暴露导航 API
5. 注册中间表框架和自动表框架
6. 启动 APScheduler 定时任务调度器

```python
# 关键注册代码结构
app.include_router(import_router)           # 数据导入
app.include_router(data_router)             # 数据 CRUD
app.include_router(admin_router)            # 管理后台
app.include_router(todo_system_router)      # 待办系统
app.include_router(menu_router)             # 菜单管理
app.include_router(performance_pay_router)  # 绩效工资
# ... 共24个路由模块
```

### 4.2 核心引擎模块 — `backend/core/`

| 文件 | 职责 | 关键类/函数 |
|---|---|---|
| **event_bus.py** | 事件总线（发布-订阅模式） | `EventBus` — `subscribe()` / `publish()` / `unsubscribe()`；全局实例 `event_bus` |
| **dynamic_db.py** | 动态数据库管理 | `DynamicTableManager` — `create_or_update_table_from_schema()` 根据 JSON schema 动态建表 |
| **config_manager.py** | 统一配置管理 | `ConfigManager` — `read_navigation_config()` / `write_merged_schema_config()` / `read_ui_components_config()` |
| **pinyin_service.py** | 中文转拼音 | 用于将用户输入的中文表名/字段名转换为英文命名 |
| **table_name_manager.py** | 表名映射管理 | 管理英文表名 ↔ 中文表名的双向映射 |
| **field_name_manager.py** | 字段名映射管理 | 管理英文字段名 ↔ 中文字段名的双向映射 |
| **field_config_manager.py** | 字段配置管理 | 字段级别的配置加载/保存 |
| **data_export_engine.py** | 数据导出引擎 | 支持 Excel / Word / PDF 格式导出 |
| **data_fill_engine.py** | 数据填充引擎 | 将数据填充到模板中的占位符位置 |
| **data_source_registry.py** | 数据源注册表 | 注册和管理数据源 |
| **metadata_engine.py** | 元数据引擎 | 提取和管理数据表的元信息 |
| **system_index_manager.py** | 系统索引管理器 | 维护表和字段索引 |
| **template_import_engine.py** | 模板导入引擎 | 导入 Word/Excel 模板并解析占位符 |
| **template_preview_engine.py** | 模板预览引擎 | 生成模板的 HTML 预览 |
| **translation_service.py** | 翻译服务 | 中英文表名/字段名翻译 |
| **unified_template_manager.py** | 统一模板管理器 | 统一管理所有模板 |

### 4.3 API 路由模块 — `backend/routes/`

#### 数据管理
| 路由文件 | 前缀 | 功能 |
|---|---|---|
| `data_routes.py` | `/api/data` | 通用数据 CRUD（增删改查），支持动态表名 |
| `data_routes_new.py` | `/api/v2/data` | 新版数据 CRUD |
| `import_routes.py` | `/api/import` | 数据导入流程（上传→预览→清洗→确认→入库） |
| `import.py` | `/api/data/import` | 导入功能模块 |
| `table_structure_routes.py` | `/api/table-structure` | 表结构管理（查看/修改字段） |
| `migration_routes.py` | `/api/migration` | 数据迁移 |
| `system_table_routes.py` | `/api/system-table` | 系统表管理 |

#### 业务管理
| 路由文件 | 前缀 | 功能 |
|---|---|---|
| `admin_routes.py` | `/api/admin` | 管理后台（表名映射管理、初始化等） |
| `menu_routes.py` | `/api/menu` | 菜单配置管理 |
| `menu_routes_new.py` | `/api/navigation-admin` | 新版导航配置管理 |
| `status_change_routes.py` | `/api/status-change` | 状态变更管理 |
| `retirement_routes.py` | `/api/retirement` | 退休测算 |
| `retirement_data_routes.py` | `/api/retirement-data` | 退休数据管理 |
| `retirement_report_routes.py` | `/api/retirement-report` | 退休呈报表 |
| `performance_pay_routes.py` | `/api/performance-pay` | 绩效工资审批 |
| `performance_pay_history_routes.py` | `/api/performance-pay-history` | 绩效工资历史 |
| `performance_pay_template.py` | `/api/performance-pay-approval` | 绩效审批表模板 |
| `aggregate_query_routes.py` | `/api/aggregate-query` | 聚合查询 |
| `unit_hierarchy_routes.py` | `/api/unit-hierarchy` | 单位层级管理 |
| `tag_relations_routes.py` | `/api/tag-relations` | 标签关系管理 |
| `filter_condition_routes.py` | `/api/filter-conditions` | 过滤条件管理 |

#### 模板与报表
| 路由文件 | 前缀 | 功能 |
|---|---|---|
| `report_designer_routes.py` | `/api/report-designer` | 报表设计器 |
| `report_designer_routes_v2.py` | `/api/report-designer-v2` | 报表设计器 V2 |
| `universal_template_routes.py` | `/api/universal-template` | 通用模板管理 |
| `template_data_fill_routes.py` | `/api/template-fill` | 模板数据填报 |
| `checklist_template_routes.py` | `/api/checklist-templates` | 清单模板管理 |

#### 待办与提醒
| 路由文件 | 前缀 | 功能 |
|---|---|---|
| `todo_system_routes.py` | `/api/todo-system` | 待办系统（创建/查询/推送/确认/归档） |
| `dashboard_routes.py` | `/api/dashboard` | 仪表盘统计数据 |

#### 其他
| 路由文件 | 前缀 | 功能 |
|---|---|---|
| `intermediate_table_routes.py` | `/api/intermediate` | 中间表管理 |
| `excel_to_pdf.py` | `/api/excel-to-pdf` | Excel 转 PDF |
| `field_config_routes.py` | `/api/field-config` | 字段配置 |
| `meta_config_routes.py` | `/api/meta-config` | 元配置管理 |

### 4.4 业务服务 — `backend/services/`

#### 数据导入服务（核心）
| 服务文件 | 说明 |
|---|---|
| `import_service.py` | 通用导入服务（配置驱动，动态建表/插入/更新导航） |
| `universal_import_service_v3.py` | V3 版通用导入服务，支持字典表自动识别 |
| `universal_import_service_v2.py` | V2 版导入服务 |
| `universal_import_service.py` | V1 版导入服务 |

#### 模板与导出服务
| 服务文件 | 说明 |
|---|---|
| `report_service.py` | 报表生成服务（Word 模板填充） |
| `word_template_engine.py` | Word 模板引擎 |
| `word_exporter.py` | Word 导出 |
| `universal_word_exporter.py` | 通用 Word 导出 |
| `pdf_exporter.py` | PDF 导出 |
| `pdf_filler.py` | PDF 填充 |
| `excel_exporter.py` | Excel 导出 |
| `template_engine.py` | 模板引擎 |
| `template_analyzer.py` | 模板分析器 |
| `template_processor.py` | 模板处理器 |
| `smart_template_engine.py` | 智能模板引擎 |
| `placeholder_extractor.py` | 占位符提取器 |
| `universal_placeholder_extractor.py` | 通用占位符提取器 |
| `template_exporter.py` | 模板导出 |
| `simple_exporter.py` | 简单导出 |
| `excel_engine.py` | Excel 引擎 |
| `excel_to_html.py` | Excel 转 HTML |
| `excel_to_image.py` | Excel 转图片 |
| `field_extractor.py` | 字段提取器 |
| `field_matcher.py` | 字段匹配器 |
| `field_mapping_service.py` | 字段映射服务 |
| `mapping_optimizer.py` | 映射优化器 |
| `auto_fill_service.py` | 自动填充服务 |
| `auto_fill_extension_service.py` | 自动填充扩展服务 |
| `fill_service.py` | 填充服务 |
| `auto_template_analyzer.py` | 模板自动分析器 |

#### 待办与提醒服务
| 服务文件 | 说明 |
|---|---|
| `todo_reminder.py` | 待办提醒服务（到期检查/逾期警告/归档） |
| `trigger_monitor.py` | 触发条件监听器 |
| `scheduler_service.py` | 定时任务调度器 |
| `message_service.py` | 消息服务 |

#### 导航与系统服务
| 服务文件 | 说明 |
|---|---|
| `navigation_service.py` | 导航配置管理（增删改查导航节点） |
| `validation_service.py` | 4 级数据验证服务 |
| `data_aggregator.py` | 数据聚合器 |
| `cleanup_service.py` | 数据清理服务 |
| `menu_backup_service.py` | 菜单备份服务 |
| `tag_migration_service.py` | 标签迁移服务 |

### 4.5 工具类 — `backend/utils/`

| 文件 | 功能 |
|---|---|
| `auto_table_framework.py` | **自动表框架**（新框架-零配置），基于 Vue Router + SQLAlchemy 动态 CRUD |
| `intermediate_table_framework.py` | **中间表框架**（旧框架），用于退休呈报等复杂业务表的配置化 CRUD |
| `intermediate_table_manager.py` | 中间表管理器 |
| `data_aggregator.py` | 数据聚合器 |
| `dict_utils.py` | 字典工具函数 |
| `excel_metadata_extractor.py` | Excel 元数据提取器（完整样式还原） |
| `excel_to_luckysheet.py` | Excel 转 Luckysheet 格式 |
| `name_translator.py` | 名称翻译器（中英文互转） |
| `retirement_calculator.py` | 退休计算器（新政策计算） |
| `smart_template_filler.py` | 智能模板填充器 |
| `target_mapping.py` | 目标字段映射 |
| `todo_scheduler.py` | 待办定时调度器（80周岁扫描/退休提醒扫描） |

---

## 5. 前端架构

### 5.1 应用入口 — `frontend/src/main.ts`

```typescript
import { createApp } from "vue"
import { createPinia } from "pinia"
import ElementPlus from "element-plus"
import zhCn from "element-plus/dist/locale/zh-cn.mjs"

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount("#app")
```

### 5.2 路由系统 — `frontend/src/router/index.ts`

使用 **Hash 模式**，路由结构如下：

| 路径 | 组件 | 说明 |
|---|---|---|
| `/` | Dashboard | 首页仪表盘 |
| `/system` | 系统管理布局 | 导航到子路由 |
| `/system/module-mgt` | Modules | 模块管理 |
| `/system/data-table` | 数据表管理 | 表结构管理 |
| `/system/dict` | 字典管理 | 字典表管理 |
| `/system/*` | 动态模块 | 系统管理下的动态数据节点 |
| `/todo/*` | 待办系统 | 预警督办模块 |
| `/import/workbench` | DataImportWorkbench | 数据导入工作台 |
| `/data/:tableName` | GenericDataView | 通用数据视图 |
| `/performance/*` | 绩效管理 | 绩效审批/历史/统计 |
| `/:moduleId/:tableName` | 动态路由 | 模块数据节点 |
| `/:parentId/:moduleId/:tableName` | 动态路由 | 子模块数据节点 |
| `/auto-table/:tableName` | AutoTableView | 自动表管理（新框架） |
| `/intermediate/:tableName` | IntermediateTableView | 中间表管理（旧框架） |
| `/report-view/:templateId/:teacherId?` | ReportView | 报表查看 |
| `/universal-report/:templateId/:teacherId?` | UniversalReportView | 通用模板导出 |

### 5.3 状态管理 — `frontend/src/store/`

| Store | 职责 | 关键状态 |
|---|---|---|
| **app.ts** | 应用状态 | `sidebarCollapse` / `device` / `theme` / `language` |
| **tags.ts** | 多标签页 | `tagsList` / `activeTag` / `cachedViews` |
| **user.ts** | 用户信息 | `userInfo` / `isLoggedIn` / `token` |

### 5.4 布局组件 — `frontend/src/components/Layout/`

```
App.vue
├── Header.vue              # 顶部导航栏
│   ├── 系统标题 "太平教育人事管理系统"
│   ├── 待办通知铃铛（30秒轮询）
│   └── 用户下拉菜单
├── Sidebar.vue             # 左侧导航菜单
│   └── SidebarItem.vue     # 递归菜单项（支持三级）
├── TagsView.vue            # 多标签导航栏
└── AppMain.vue             # 主内容区（router-view）
```

**Sidebar 的核心逻辑**：
- 从后端 `/api/navigation-admin/tree` 动态加载导航树
- 支持三级嵌套：模块 → 子模块 → 叶子节点
- 每个叶子节点动态生成路由路径

### 5.5 关键业务组件

| 组件 | 功能 |
|---|---|
| **TodoTriggerDialog.vue** | 待办业务触发确认弹窗 |
| **TodoList.vue** | 待办工作列表组件 |
| **ChecklistDrawer.vue** | 清单抽屉组件 |
| **RetirementReportForm.vue** | 退休呈报表组件 |
| **ReportDesigner.vue** | 报表设计器组件 |
| **PerformancePayApprovalDesigner.vue** | 绩效工资审批表设计器 |
| **AutoTableManager.vue** | 自动表管理器 |
| **IntermediateTableManager.vue** | 中间表管理器 |
| **DocumentPreview.vue** | 文档预览组件 |
| **RetirementCalculatorDialog.vue** | 退休计算器弹窗 |
| **BackupManager.vue** | 备份管理器 |

### 5.6 前端工具类 — `frontend/src/utils/`

| 文件 | 功能 |
|---|---|
| **eventBus.ts** | 自定义事件总线（导航更新/标签切换/路由变更） |
| **todoNotification.ts** | 待办通知服务（HTTP 轮询，每5秒查询待处理触发器） |
| **websocket.ts** | WebSocket 实时通知服务（自动重连，最多5次） |
| **namingValidator.js** | 命名验证器（表名/字段名规范检查） |
| **tableNameManager.js** | 表名管理器（中英文双向映射，本地缓存） |

---

## 6. 数据库设计

### 6.1 连接信息

- **数据库**：PostgreSQL
- **数据库名**：`taiping_education`
- **用户**：`taiping_user`
- **密码**：`taiping_password`
- **主机**：`localhost:5432`
- **连接串**：`postgresql://taiping_user:taiping_password@localhost:5432/taiping_education`

### 6.2 表结构体系

系统不预设任何数据表结构，所有表通过用户上传数据后动态创建。但根据配置文件和数据分析，存在以下典型表结构：

#### 主表（核心业务表）
- `teacher_basic` — 教师基础信息（姓名、身份证、性别、出生日期等）
- `teacher_education` — 教师学历记录
- `teacher_position` — 教师职务记录
- `teacher_certificate` — 教师资格证信息

#### 字典表（配置数据，前缀 `dict_`）
- `dict_position` — 岗位/职务字典
- `dict_education` — 学历字典
- `dict_department` — 单位/部门字典
- `dict_personal_identity` — 个人身份字典
- `dict_teacher_type` — 人才类型字典
- `dict_work_status` — 任职状态字典
- `dict_tags` — 标签字典
- `dict_id_card_attr` — 身份证属性字典
- `dict_unit_name` — 单位名称字典
- `dict_post_name` — 岗位名称字典
- `dict_post_level` — 岗位等级字典

#### 业务子表
- `retirement_report_data` — 退休呈报数据（中间表，67个字段）
- `performance_pay_*` — 绩效工资相关表
- `person_tags` — 人员标签关系表
- `unit_hierarchy` — 单位层级关系表

#### 待办/清单表
- `todo_items` — 待办事项
- `todo_triggers` — 待办触发器
- `todo_history` — 待办历史归档
- `checklist_templates` — 清单模板
- `pushed_checklists` — 已推送清单

### 6.3 核心设计原则

1. **统一主键**：所有表使用自增 `id` 作为主键
2. **标准化关联**：外键使用 `表名_id` 命名规范
3. **冗余显示字段**：关联表冗余存储 `name` 字段避免频繁 JOIN
4. **动态建表**：`DynamicTableManager` 根据 `table_schemas.json` 在运行时动态创建/修改表

---

## 7. 配置文件体系

系统采用 **100% 配置驱动** 架构，核心配置文件集中在 `backend/config/` 目录：

### 7.1 核心配置

| 配置文件 | 用途 | 说明 |
|---|---|---|
| **navigation.json** | 导航菜单定义 | 6大模块树形结构，动态更新 |
| **table_name_mappings.json** | 表名中英文映射 | 中文→英文 / 英文→中文 双向映射，80+ 表 |
| **table_schemas.json** | 表结构定义 | 所有表的字段名、数据类型、约束 |
| **field_mappings.json** | 字段映射配置 | 18个表的字段映射 + 100+全局映射 |
| **field_name_mappings.json** | 字段名中英文映射 | 双向映射 |
| **mapping_rules.json** | 映射规则 | 表名/字段名命名规则、过滤规则 |
| **dict_tables_config.json** | 字典表配置 | 11个字典表的定义 |
| **import_config.json** | 导入配置 V3 | 关联规范、字段类型映射、校验规则 |
| **report_definitions.json** | 报表定义 | 退休呈报表/职务升降表等的数据映射 |
| **template_config.json** | 模板配置 | 占位符格式、系统字段、文件类型 |
| **unified_template_config.json** | 统一模板配置 | 模板分类管理 |
| **ui_components.json** | UI 组件配置 | 表单/列表的 UI 结构定义 |
| **system_index.json** | 系统索引 | 表和字段索引 |

### 7.2 子目录配置

| 目录 | 内容 |
|---|---|
| `config/field_configs/` | 18个字段配置文件（每个表一个） |
| `config/template_configs/` | 3个模板配置文件（绩效工资审批表/退休呈报表等） |
| `config/intermediate_tables/` | 中间表定义（退休呈报数据 67个字段） |

### 7.3 前端配置

| 配置文件 | 用途 |
|---|---|
| `frontend/src/config/routeMapping.js` | 路由映射配置（模块路径统一管理） |

---

## 8. 核心业务流程

### 8.1 数据导入流程

```
用户上传文件（Excel/Word/CSV）
    ↓
FileSelectionPanel（选择文件 + 选择归属模块）
    ↓
后端解析文件（提取表头和数据）
    ↓
FieldConfigPanel（字段映射配置：原始字段 → 标准字段）
    ↓
DataPreviewPanel（数据预览 + 清洗）
    ↓
ConfirmImportPanel（确认导入）
    ↓
ImportService.import_data()
    ├── 1. 动态建表（_create_or_update_table）
    ├── 2. 插入数据（upsert / insert）
    ├── 3. 更新 schema 配置（table_schemas.json）
    └── 4. 更新导航配置（navigation.json）
```

### 8.2 模板填报流程

```
用户选择模板（Word/Excel）
    ↓
模板引擎解析模板（提取占位符）
    ↓
字段映射（模板字段 ↔ 数据表字段）
    ↓
数据查询（从数据库获取数据）
    ↓
数据填充（将数据写入模板占位符）
    ↓
导出/预览（Word / Excel / PDF / HTML）
```

### 8.3 待办业务触发流程

```
定时任务扫描（APScheduler）
    │
    ├── 到龄退休提醒（每天2:30）
    ├── 80周岁高龄补贴扫描（每天2:30）
    ├── 待办到期检查（每天2:00）
    └── 触发条件监听（每5分钟）
        │
        ├── 推送待办通知
        ├── 前端轮询/WebSocket 接收
        ├── 用户确认推送
        └── 写入 todo_items 表
```

### 8.4 退休呈报表填报流程

```
选择退休教师
    ↓
RetirementCalculatorDialog（退休条件测算）
    ↓
RetirementReportForm（呈报表数据录入）
    ↓
模板填充（退休呈报表 Word 模板）
    ↓
导出 Word 文档（《职工退休呈报表》）
    ↓
推送审批（进入待办系统）
```

---

## 9. 依赖关系图

### 9.1 后端依赖关系

```
main.py（应用入口）
  ├── core/（基础引擎层）
  │   ├── dynamic_db.py ← SQLAlchemy → PostgreSQL
  │   ├── event_bus.py（独立，被所有模块引用）
  │   ├── config_manager.py ← 读写 JSON 配置文件
  │   ├── table_name_manager.py ← table_name_mappings.json
  │   ├── field_name_manager.py ← field_name_mappings.json
  │   └── pinyin_service.py（工具类）
  ├── routes/（API 路由层）
  │   ├── 依赖 services/ 进行业务处理
  │   └── 依赖 core/ 进行数据操作
  ├── services/（业务逻辑层）
  │   ├── import_service.py → 依赖 core/dynamic_db.py
  │   ├── navigation_service.py → 依赖 core/config_manager.py
  │   ├── todo_reminder.py → 直接连接数据库
  │   ├── validation_service.py → 依赖 merged_schema_mappings.json
  │   └── template_engine.py → 依赖 python-docx / openpyxl
  └── utils/（工具层）
      ├── auto_table_framework.py → 依赖 core/dynamic_db.py
      ├── intermediate_table_framework.py → 依赖 core/dynamic_db.py
      └── todo_scheduler.py → 调用 services/todo_reminder.py
```

### 9.2 前端依赖关系

```
main.ts（应用入口）
  ├── router/index.ts ← 路由表
  ├── store/（状态管理）
  │   ├── app.ts（全局状态）
  │   ├── tags.ts（标签页状态）
  │   └── user.ts（用户状态）
  ├── App.vue（根组件）
  │   └── Layout/
  │       ├── Header.vue → TodoList.vue / ChecklistDrawer.vue
  │       ├── Sidebar.vue ← /api/navigation-admin/tree
  │       ├── TagsView.vue ← store/tags.ts
  │       └── AppMain.vue → <router-view>
  ├── views/（页面）
  │   ├── dashboard/index.vue → ECharts 图表
  │   ├── import/DataImportWorkbench.vue → 导入流程
  │   ├── data/GenericDataView.vue → 通用数据展示
  │   ├── system/ModuleManagement.vue → 模块配置
  │   └── ...
  └── utils/
      ├── eventBus.ts（组件间通信）
      ├── todoNotification.ts → /api/todo-system/pending-triggers
      └── websocket.ts → 实时通知
```

### 9.3 前后端通信

- **HTTP API**：前端通过 `axios` 调用 `/api/*` 接口，Vite 代理到后端 `localhost:8000`
- **轮询**：待办通知使用 5 秒 HTTP 轮询
- **WebSocket**：备用实时通知通道
- **事件驱动**：后端事件总线 `event_bus` 用于模块间解耦

---

## 10. 项目运行方式

### 10.1 环境要求

- **Python**：3.10+
- **Node.js**：18+
- **PostgreSQL**：14+
- **操作系统**：Windows（主）/ Linux（支持）

### 10.2 一键启动（推荐）

双击运行 `tp_education_system\启动全部服务器.bat`，同时启动：
- 后端：`http://localhost:8000`
- 前端：`http://localhost:5173`

### 10.3 分步启动

#### 启动后端
```bash
cd tp_education_system\backend
pip install -r requirements.txt
python main.py
```
后端启动在 `http://0.0.0.0:8000`

#### 启动前端
```bash
cd tp_education_system\frontend
npm install
npm run dev
```
前端启动在 `http://localhost:5173`

### 10.4 PM2 进程管理（可选）

```bash
# 使用 ecosystem.config.js
pm2 start ecosystem.config.js
```

管理两个进程：
- `education-backend`：Python uvicorn，端口 8000
- `education-frontend`：npm run dev

### 10.5 数据库初始化

系统无需手动建表。首次使用时：
1. 确保 PostgreSQL 中已创建 `taiping_education` 数据库和 `taiping_user` 用户
2. 启动后端后，通过**数据导入工作台**上传 Excel/Word 文件
3. 系统自动完成：建表 → 数据入库 → 导航注册

### 10.6 备份与恢复

项目根目录提供多种备份方式：
- `backup_db.py` — 数据库备份
- `backup_all.py` — 全量备份（数据库 + 配置文件 + 模板）
- `git_backup.bat` — Git 仓库备份
- `auto_backup_daily.ps1` — 每日自动备份脚本

---

## 附录：关键 API 端点速查

| 方法 | 端点 | 用途 |
|---|---|---|
| GET | `/api/navigation-admin/tree` | 获取导航菜单树 |
| PUT | `/api/navigation-admin/tree` | 更新导航菜单树 |
| POST | `/api/import/upload` | 上传数据文件 |
| POST | `/api/import/import` | 执行数据导入 |
| GET | `/api/data/{table_name}` | 查询表数据 |
| POST | `/api/data/{table_name}` | 插入表数据 |
| PUT | `/api/data/{table_name}/{id}` | 更新表数据 |
| DELETE | `/api/data/{table_name}/{id}` | 删除表数据 |
| GET | `/api/table-structure/{table_name}` | 获取表结构 |
| GET | `/api/todo-system/pending-triggers` | 查询待处理触发器 |
| POST | `/api/todo-system/triggers` | 创建待办触发器 |
| GET | `/api/dashboard/stats` | 获取仪表盘统计数据 |
| POST | `/api/template-fill/fill` | 执行模板数据填报 |
| POST | `/api/status-change/apply` | 应用状态变更 |

---

> **文档版本**：v1.0  
> **适用范围**：太平镇教育人事管理系统  
> **设计理念**：配置驱动 · 零代码扩展 · 动态建表 · 事件驱动