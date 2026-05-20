from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

print("第三步：创建视图方便查询")
print("=" * 80)

# 创建单位树形视图
create_view_sql = """
-- 创建单位树形视图（递归查询）
CREATE OR REPLACE VIEW unit_tree_view AS
WITH RECURSIVE unit_tree AS (
    -- 基础查询：选择所有顶级单位（省级）
    SELECT 
        id,
        unit_level,
        unit_name,
        parent_id,
        school_dict_id,
        full_path,
        1 as depth,
        ARRAY[id]::integer[] as path_ids,
        ARRAY[unit_name]::varchar[] as path_names
    FROM unit_hierarchy
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- 递归查询：选择所有子单位
    SELECT 
        u.id,
        u.unit_level,
        u.unit_name,
        u.parent_id,
        u.school_dict_id,
        u.full_path,
        ut.depth + 1,
        (ut.path_ids || u.id)::integer[],
        (ut.path_names || u.unit_name)::varchar[]
    FROM unit_hierarchy u
    INNER JOIN unit_tree ut ON u.parent_id = ut.id
)
SELECT * FROM unit_tree;
"""

try:
    conn.execute(text(create_view_sql))
    conn.commit()
    print("[OK] unit_tree_view视图创建成功")
except Exception as e:
    print(f"[ERROR] 创建视图失败：{e}")
    conn.rollback()

# 创建教师单位关联视图
create_teacher_unit_view_sql = """
-- 创建教师单位关联视图
CREATE OR REPLACE VIEW teacher_unit_view AS
SELECT 
    tbi.id as teacher_id,
    tbi.name as teacher_name,
    tbi.id_card,
    tu.unit_1 as school_dict_id,
    dud.unit as school_name,
    uh.id as unit_hierarchy_id,
    uh.full_path,
    uh.unit_level
FROM teacher_basic_info tbi
LEFT JOIN teacher_unit tu ON tbi.id_card = tu.id_card
LEFT JOIN dict_unit_dictionary dud ON tu.unit_1::integer = dud.id
LEFT JOIN unit_hierarchy uh ON dud.id = uh.school_dict_id;
"""

try:
    conn.execute(text(create_teacher_unit_view_sql))
    conn.commit()
    print("[OK] teacher_unit_view视图创建成功")
except Exception as e:
    print(f"[ERROR] 创建视图失败：{e}")
    conn.rollback()

# 验证视图
print("\n验证unit_tree_view视图：")
print("=" * 80)
result = conn.execute(text("""
    SELECT id, unit_level, unit_name, depth, path_names
    FROM unit_tree_view
    ORDER BY depth, id
    LIMIT 10
"""))
rows = result.fetchall()

for row in rows:
    print(f"ID: {row[0]:2d} | 层级: {row[1]:8s} | 名称: {row[2]:30s} | 深度: {row[3]} | 路径: {' -> '.join(row[4])}")

print("\n验证teacher_unit_view视图（前5条）：")
print("=" * 80)
result = conn.execute(text("""
    SELECT teacher_id, teacher_name, school_name, full_path
    FROM teacher_unit_view
    LIMIT 5
"""))
rows = result.fetchall()

for row in rows:
    print(f"教师ID: {row[0]} | 姓名: {row[1]:10s} | 学校: {row[2]:30s} | 路径: {row[3]}")

conn.close()
print("\n[OK] 所有视图创建完成")
