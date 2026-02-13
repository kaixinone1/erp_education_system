# 太平教育系统 - 代码编写规范

## 一、命名规范

### 1. 数据库命名规范

#### 表名规范
- **后端使用英文**，格式：`[模块前缀][核心实体]_[业务对象]`
- **全部小写**，单词间用下划线连接
- **示例**：
  - `教师人才类型` → `teacher_talent_info`
  - `教师职务字典` → `dict_teacher_position_dictionary`
  - `学历层次字典` → `dict_education_level`

#### 字段名规范
- **后端使用英文**，全部小写，单词间用下划线连接
- **前端显示中文**，使用原始中文字段名
- **示例**：
  - `姓名` → `name`
  - `身份证号码` → `id_card`
  - `档案出生日期` → `file_birth_date`

### 2. 翻译规则

#### 表名翻译规则
格式：`[模块前缀][核心实体]_[业务对象]`

**核心实体字典** (CORE_ENTITY_DICT)：
```python
{
    "教师": "teacher",
    "学生": "student",
    "员工": "employee",
    "党员": "party_member",
    "课程": "course",
    "数据": "data",
    "年级": "grade",
    "班级": "class",
    "学历": "education",
    "职称": "title",
    "职务": "position",
    "资格证": "certificate",
    "单位": "unit",
    "身份证": "id_card",
    "人才": "talent",
    "考勤": "attendance",
    "党建": "party_building",
    "活动": "activity",
    "人事": "hr",
    "工资": "salary",
    "部门": "department"
}
```

**业务对象字典** (BUSINESS_OBJECT_DICT)：
```python
{
    "基础信息": "basic_info",
    "个人身份": "personal_identity",
    "字典": "dictionary",
    "记录": "record",
    "明细": "detail",
    "信息": "info",
    "数据": "data",
    "管理": "management",
    "统计": "statistics",
    "汇总": "summary",
    "分析": "analysis",
    "档案": "archive",
    "证书": "certificate",
    "合同": "contract",
    "考核": "assessment",
    "培训": "training",
    "调动": "transfer",
    "离职": "resignation",
    "退休": "retirement"
}
```

**字典表前缀**：`dict_`

#### 字段名翻译规则
优先使用全局字段映射表：

```python
GLOBAL_FIELD_MAPPINGS = {
    "姓名": "name",
    "身份证号码": "id_card",
    "出生日期": "birth_date",
    "民族": "ethnicity",
    "籍贯": "native_place",
    "联系电话": "phone",
    "学历": "education_level",
    "学位": "degree",
    "专业": "major",
    "毕业院校": "graduated_school",
    "参加工作日期": "join_work_date",
    "进入本单位日期": "enter_company_date",
    "任职状态": "employment_status",
    "性别": "gender",
    "年龄": "age",
    "政治面貌": "political_status",
    "入党时间": "party_join_date",
    "职称": "professional_title",
    "职务": "position",
    "部门": "department",
    "地址": "address",
    "邮箱": "email",
    "备注": "remark",
    "创建时间": "created_at",
    "更新时间": "updated_at"
}
```

## 二、前后端分离原则

### 后端（数据库/API）
- 表名：英文
- 字段名：英文
- API路径：英文

### 前端（显示）
- 表名：中文
- 字段名：中文
- 菜单名：中文
- 按钮文字：中文

### 映射关系
- 使用 `table_name_mappings.json` 维护中英文表名映射
- 使用 `field_mappings.json` 维护中英文字段映射
- 使用 `navigation.json` 维护菜单结构

## 三、菜单挂载规则

### 文件夹类型模块
- **特征**：`type: "module"`，有 `children` 属性
- **功能**：用于组织子模块，不直接挂载数据管理器
- **示例**：
  ```json
  {
    "id": "system-dictionaries",
    "title": "字典管理",
    "type": "module",
    "children": [...]
  }
  ```

### 功能类型模块
- **特征**：`type: "component"`，有 `component` 属性
- **功能**：直接挂载数据管理器，可显示数据
- **示例**：
  ```json
  {
    "id": "teacher-basic",
    "title": "教师基础信息",
    "type": "component",
    "component": "DataTable",
    "table_name": "teacher_basic"
  }
  ```

## 四、数据清理原则

### 清理内容（数据库层面）
- ✅ 数据库表（DROP TABLE）
- ✅ 表数据（DELETE/TRUNCATE）
- ✅ 表名映射（table_name_mappings.json）
- ✅ 字段配置（field_configs/*.json）

### 保留内容（系统层面）
- ❌ 导航菜单（navigation.json）
- ❌ 系统模块结构
- ❌ 用户配置

## 五、字典表规范

### 字典表结构
```sql
CREATE TABLE dict_xxx (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
```

### 字典表命名
- 前缀：`dict_`
- 格式：`dict_[核心实体]_[业务对象]`
- 示例：
  - `dict_teacher_position`（教师职务字典）
  - `dict_education_level`（学历层次字典）

### 字典表使用
- 子表通过 `xxx_id` 和 `xxx_name` 关联字典表
- 示例：
  ```sql
  teacher_talent_type (
      talent_type_id INTEGER,  -- 关联字典表id
      talent_type_name VARCHAR  -- 冗余存储字典表name
  )
  ```

## 六、导入流程规范

### 导入顺序
1. **字典表** - 先导入所有字典表
2. **主表** - 导入主表（如教师基础信息）
3. **子表** - 导入子表（关联主表和字典表）

### 表名冲突处理
1. 检查中文表名是否已存在
2. 检查表结构是否一致
3. 表结构一致 → 使用现有表
4. 表结构不一致 → 提示修改中文表名

## 七、代码规范检查清单

- [ ] 表名使用英文，符合翻译规则
- [ ] 字段名使用英文，符合全局映射
- [ ] 前端显示使用中文
- [ ] 字典表使用标准结构（id + name）
- [ ] 菜单挂载符合类型规则
- [ ] 数据清理不删除导航配置
