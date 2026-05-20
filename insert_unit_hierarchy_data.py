from sqlalchemy import create_engine, text

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

print("第二步：插入省、市、镇、校四级数据")
print("=" * 80)

# 插入省级单位
print("\n插入省级单位...")
conn.execute(text("""
    INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, full_path)
    VALUES ('province', '湖北省', NULL, '湖北省')
"""))
conn.commit()
print("[OK] 省级单位插入成功")

# 插入市级单位
print("\n插入市级单位...")
conn.execute(text("""
    INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, full_path)
    SELECT 'city', '枣阳市', id, '湖北省/枣阳市'
    FROM unit_hierarchy
    WHERE unit_level='province' AND unit_name='湖北省'
"""))
conn.commit()
print("[OK] 市级单位插入成功")

# 插入镇级单位
print("\n插入镇级单位...")
conn.execute(text("""
    INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, full_path)
    SELECT DISTINCT 'town', '枣阳市太平镇', 
           (SELECT id FROM unit_hierarchy WHERE unit_level='city' AND unit_name='枣阳市'),
           '湖北省/枣阳市/枣阳市太平镇'
    FROM dict_unit_dictionary
    WHERE unit LIKE '%太平镇%'
"""))
conn.commit()
print("[OK] 镇级单位插入成功")

# 插入校级单位
print("\n插入校级单位...")
conn.execute(text("""
    INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, school_dict_id, full_path)
    SELECT 'school', unit, 
           (SELECT id FROM unit_hierarchy WHERE unit_level='town' AND unit_name='枣阳市太平镇'),
           id,
           '湖北省/枣阳市/枣阳市太平镇/' || unit
    FROM dict_unit_dictionary
"""))
conn.commit()
print("[OK] 校级单位插入成功")

# 验证数据
print("\n验证插入的数据：")
print("=" * 80)
result = conn.execute(text("""
    SELECT id, unit_level, unit_name, parent_id, school_dict_id, full_path
    FROM unit_hierarchy
    ORDER BY id
"""))
rows = result.fetchall()

for row in rows:
    print(f"ID: {row[0]:2d} | 层级: {row[1]:8s} | 名称: {row[2]:30s} | 父ID: {row[3]} | 学校ID: {row[4]} | 路径: {row[5]}")

conn.close()
print("\n[OK] 所有数据插入完成")
