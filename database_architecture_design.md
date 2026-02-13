# 数据库架构设计方案

## 核心设计原则

1. **统一主键**：所有表使用自增id作为主键
2. **标准化关联**：通过外键id关联，不直接存储业务code
3. **冗余显示字段**：存储关联表的中文名称，方便查询展示
4. **支持多表统计**：设计便于JOIN查询的表结构

---

## 表结构设计

### 1. 主表 - 教师基础信息

```sql
CREATE TABLE teacher_basic (
    id SERIAL PRIMARY KEY,                    -- 自增主键（核心关联字段）
    姓名 VARCHAR(50) NOT NULL,
    身份证号码 VARCHAR(18) UNIQUE NOT NULL,    -- 业务主键（用于导入时关联）
    性别 VARCHAR(10),
    出生日期 DATE,
    联系电话 VARCHAR(20),
    邮箱 VARCHAR(100),
    部门_id INTEGER REFERENCES department(id), -- 关联部门字典
    部门_名称 VARCHAR(50),                      -- 冗余存储部门名称
    状态 VARCHAR(20) DEFAULT '在职',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 字典表设计规范

所有字典表统一结构：

```sql
-- 教师职务字典
CREATE TABLE dict_position (
    id SERIAL PRIMARY KEY,      -- 自增id（关联用）
    code VARCHAR(30) UNIQUE,    -- 业务代码（如1,2,3或A,B,C）
    name VARCHAR(50) NOT NULL,  -- 显示名称
    sort_order INTEGER,         -- 排序
    status BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学历字典
CREATE TABLE dict_education (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE,
    name VARCHAR(50) NOT NULL,
    sort_order INTEGER,
    status BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 部门字典
CREATE TABLE dict_department (
    id SERIAL PRIMARY KEY,
    code VARCHAR(30) UNIQUE,
    name VARCHAR(50) NOT NULL,
    parent_id INTEGER REFERENCES dict_department(id), -- 支持层级
    sort_order INTEGER,
    status BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 子表设计规范

所有子表必须包含：
1. `teacher_id` - 关联主表
2. `{字段}_id` - 关联字典表的id
3. `{字段}_名称` - 冗余存储字典名称

```sql
-- 教师职务记录表
CREATE TABLE teacher_position (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teacher_basic(id),  -- 关联主表
    
    -- 职务信息
    职务_id INTEGER REFERENCES dict_position(id),               -- 关联字典id
    职务_名称 VARCHAR(50),                                       -- 冗余存储名称
    职务_code VARCHAR(30),                                       -- 冗余存储code
    
    -- 其他字段
    任职文号 VARCHAR(50),
    起始日期 DATE,
    认定日期 DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 教师学历记录表
CREATE TABLE teacher_education (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teacher_basic(id),
    
    -- 学历信息
    学历_id INTEGER REFERENCES dict_education(id),
    学历_名称 VARCHAR(50),
    学历_code VARCHAR(30),
    
    -- 其他字段
    毕业院校 VARCHAR(100),
    专业 VARCHAR(50),
    毕业日期 DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 关联关系图

```
┌─────────────────┐
│  teacher_basic  │◄───────┐
│  (主表)          │        │
│  - id (PK)      │        │
│  - 姓名          │        │
│  - 身份证号码    │        │
│  - 部门_id (FK)  │        │
└────────┬────────┘        │
         │                 │
         │ 1:N             │
         ▼                 │
┌─────────────────┐        │
│ teacher_position │        │
│  (子表-职务)     │        │
│  - id (PK)      │        │
│  - teacher_id (FK)       │
│  - 职务_id (FK)  │        │
│  - 职务_名称     │        │
└────────┬────────┘        │
         │                 │
         │ N:1             │
         ▼                 │
┌─────────────────┐        │
│  dict_position  │        │
│  (字典表)        │        │
│  - id (PK)      │        │
│  - code         │        │
│  - name         │        │
└─────────────────┘        │
                           │
┌─────────────────┐        │
│ teacher_education│◄───────┤
│  (子表-学历)     │        │
│  - id (PK)      │        │
│  - teacher_id (FK)       │
│  - 学历_id (FK)  │        │
│  - 学历_名称     │        │
└────────┬────────┘        │
         │                 │
         │ N:1             │
         ▼                 │
┌─────────────────┐        │
│ dict_education  │        │
│  (字典表)        │        │
│  - id (PK)      │        │
│  - code         │        │
│  - name         │        │
└─────────────────┘        │
                           │
┌─────────────────┐        │
│ dict_department │◄───────┘
│  (字典表)        │
│  - id (PK)      │
│  - code         │
│  - name         │
└─────────────────┘
```

---

## 统计查询示例

### 1. 教师基本信息汇总（主表+最新职务+最高学历）

```sql
SELECT 
    tb.姓名,
    tb.身份证号码,
    tb.性别,
    tb.部门_名称,
    dp.职务_名称 as 当前职务,
    de.学历_名称 as 最高学历,
    de.毕业院校
FROM teacher_basic tb
LEFT JOIN (
    -- 获取最新职务
    SELECT DISTINCT ON (teacher_id) 
        teacher_id, 
        职务_名称
    FROM teacher_position
    ORDER BY teacher_id, 起始日期 DESC
) dp ON tb.id = dp.teacher_id
LEFT JOIN (
    -- 获取最高学历
    SELECT DISTINCT ON (teacher_id) 
        teacher_id, 
        学历_名称,
        毕业院校
    FROM teacher_education
    ORDER BY teacher_id, 毕业日期 DESC
) de ON tb.id = de.teacher_id;
```

### 2. 按职务统计教师人数

```sql
SELECT 
    dp.name as 职务,
    COUNT(DISTINCT tp.teacher_id) as 教师人数
FROM dict_position dp
LEFT JOIN teacher_position tp ON dp.id = tp.职务_id
GROUP BY dp.id, dp.name
ORDER BY dp.sort_order;
```

### 3. 按部门统计教师学历分布

```sql
SELECT 
    tb.部门_名称,
    de.name as 学历,
    COUNT(*) as 人数
FROM teacher_basic tb
JOIN teacher_education te ON tb.id = te.teacher_id
JOIN dict_education de ON te.学历_id = de.id
GROUP BY tb.部门_名称, de.name
ORDER BY tb.部门_名称, de.sort_order;
```

### 4. 复杂统计 - 各部门各职务人数

```sql
SELECT 
    tb.部门_名称,
    dp.name as 职务,
    COUNT(DISTINCT tb.id) as 人数
FROM teacher_basic tb
LEFT JOIN teacher_position tp ON tb.id = tp.teacher_id
LEFT JOIN dict_position dp ON tp.职务_id = dp.id
GROUP BY tb.部门_名称, dp.name
ORDER BY tb.部门_名称, dp.sort_order;
```

---

## 导入时自动处理流程

### 1. 导入字典表

```
Excel数据：
┌──────┬────────┐
│ 序号 │  职务  │
├──────┼────────┤
│  1   │ 正高级 │
│  2   │ 高级   │
│  3   │ 中级   │
└──────┴────────┘

自动处理：
1. 创建 dict_position 表（id, code, name）
2. 插入数据：
   - id=1, code='1', name='正高级'
   - id=2, code='2', name='高级'
   - id=3, code='3', name='中级'
```

### 2. 导入子表（教师职务记录）

```
Excel数据：
┌──────┬──────────────┬──────┬──────────┐
│ 姓名 │  身份证号码  │ 职级 │ 任职文号 │
├──────┼──────────────┼──────┼──────────┤
│ 张三 │ 110101...    │  3   │ 2023-001 │
└──────┴──────────────┴──────┴──────────┘

自动处理：
1. 创建 teacher_position 表
2. 根据身份证号码查询 teacher_basic 获取 teacher_id
3. 根据职级'3'查询 dict_position 获取 职务_id=3, 职务_名称='中级'
4. 插入数据：
   - teacher_id = 100 (张三的id)
   - 职务_id = 3
   - 职务_名称 = '中级'
   - 职务_code = '3'
   - 任职文号 = '2023-001'
```

---

## 优势总结

1. **查询简单**：冗余存储名称，避免多表JOIN
2. **统计方便**：通过id关联，支持复杂统计
3. **扩展灵活**：新增字典项只需插入数据，无需改代码
4. **数据一致性**：通过外键约束保证数据完整性
5. **导入自动化**：统一处理逻辑，无需为每个表写代码
