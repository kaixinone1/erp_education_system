from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 1. 添加襄阳市（地级市）
    print("1. 添加襄阳市（地级市）...")
    result = conn.execute(text("""
        INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, full_path)
        VALUES ('city', '襄阳市', 1, '湖北省/襄阳市')
        ON CONFLICT DO NOTHING
        RETURNING id
    """))
    
    city_row = result.fetchone()
    if city_row:
        city_id = city_row[0]
        print(f"   襄阳市ID: {city_id}")
    else:
        # 如果已存在，获取ID
        result = conn.execute(text("SELECT id FROM unit_hierarchy WHERE unit_name = '襄阳市'"))
        city_id = result.fetchone()[0]
        print(f"   襄阳市已存在，ID: {city_id}")
    
    # 2. 更新枣阳市为县级市，并设置父级为襄阳市
    print("\n2. 更新枣阳市为县级市...")
    conn.execute(text("""
        UPDATE unit_hierarchy 
        SET unit_level = 'county',
            parent_id = :city_id,
            full_path = '湖北省/襄阳市/枣阳市'
        WHERE unit_name = '枣阳市'
    """), {"city_id": city_id})
    
    # 3. 更新镇级单位的full_path
    print("\n3. 更新镇级单位的路径...")
    conn.execute(text("""
        UPDATE unit_hierarchy 
        SET full_path = '湖北省/襄阳市/枣阳市/' || unit_name
        WHERE unit_level = 'town'
    """))
    
    # 4. 更新校级单位的full_path
    print("\n4. 更新校级单位的路径...")
    conn.execute(text("""
        UPDATE unit_hierarchy h1
        SET full_path = (
            SELECT '湖北省/襄阳市/枣阳市/' || h2.unit_name || '/' || h1.unit_name
            FROM unit_hierarchy h2
            WHERE h2.id = h1.parent_id
        )
        WHERE h1.unit_level = 'school'
    """))
    
    conn.commit()
    print("\n[OK] 数据库更新完成！")
    
    # 验证结果
    print("\n验证结果：")
    result = conn.execute(text("""
        SELECT id, unit_level, unit_name, parent_id, full_path
        FROM unit_hierarchy
        ORDER BY id
        LIMIT 20
    """))
    
    for row in result:
        print(f"ID: {row.id:3d} | 层级: {row.unit_level:10s} | 名称: {row.unit_name:30s} | 父ID: {str(row.parent_id):5s} | 路径: {row.full_path}")
