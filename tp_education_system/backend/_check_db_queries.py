"""
临时数据库检查脚本 - 执行四项查询任务
"""
import psycopg2

conn_info = {
    "host": "localhost",
    "port": 5432,
    "database": "taiping_education_fifteen",
    "user": "taiping_user",
    "password": "taiping_password"
}

conn = psycopg2.connect(**conn_info)
cur = conn.cursor()

print("=" * 80)
print("【任务1】查询 title_info 表（职称字典）的结构和数据")
print("=" * 80)

# 先检查表是否存在
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'title_info'
    );
""")
exists = cur.fetchone()[0]
print(f"\ntitle_info 表是否存在: {exists}")

if not exists:
    print("\n【重要发现】title_info 表不存在！")
    print("但表名映射配置中 title_info -> '职称字典'")
    print("可能职称字典数据存在于其他表中，我来检查相关表...")
    
    # 检查 dict_grade_dictionary
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'dict_grade_dictionary'
        );
    """)
    print(f"dict_grade_dictionary 表是否存在: {cur.fetchone()[0]}")
    
    # 检查 dict_dictionary
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'dict_dictionary'
        );
    """)
    print(f"dict_dictionary 表是否存在: {cur.fetchone()[0]}")

    # 查询 dict_grade_dictionary
    try:
        cur.execute("SELECT * FROM dict_grade_dictionary LIMIT 10;")
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        print(f"\n--- dict_grade_dictionary 表结构（共{len(col_names)}列）---")
        print(f"  列名: {col_names}")
        print(f"\n--- dict_grade_dictionary 数据（前{len(rows)}条）---")
        for i, row in enumerate(rows):
            print(f"  第{i+1}条: {dict(zip(col_names, row))}")
    except Exception as e:
        print(f"查询 dict_grade_dictionary 失败: {e}")

    # 也看 dict_dictionary
    try:
        cur.execute("SELECT * FROM dict_dictionary LIMIT 10;")
        rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]
        print(f"\n--- dict_dictionary 表结构（共{len(col_names)}列）---")
        print(f"  列名: {col_names}")
        print(f"\n--- dict_dictionary 数据（前{len(rows)}条）---")
        for i, row in enumerate(rows):
            print(f"  第{i+1}条: {dict(zip(col_names, row))}")
    except Exception as e:
        print(f"查询 dict_dictionary 失败: {e}")

print("\n" + "=" * 80)
print("【任务2】查询 teacher_title_info 表（职称评定信息）的数据（前10条）")
print("=" * 80)

# 先查表结构
cur.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'teacher_title_info'
    ORDER BY ordinal_position;
""")
columns = cur.fetchall()
print(f"\n--- teacher_title_info 表结构（共{len(columns)}列）---")
for col in columns:
    print(f"  列名: {col[0]}, 类型: {col[1]}, 长度: {col[2]}, 可空: {col[3]}")

# 查询前10条数据
cur.execute("SELECT * FROM teacher_title_info LIMIT 10;")
rows = cur.fetchall()
col_names = [desc[0] for desc in cur.description]
print(f"\n--- teacher_title_info 数据（前{len(rows)}条）---")
for i, row in enumerate(rows):
    print(f"  第{i+1}条: {dict(zip(col_names, row))}")

# 特别关注"专业技术资格"相关字段
tech_cols = [c for c in col_names if '资格' in c.lower() or '技术' in c.lower() or '专业' in c.lower() or 'title' in c.lower()]
print(f"\n与'专业技术资格'相关的字段名: {tech_cols}")

print("\n" + "=" * 80)
print("【任务3】查询 post_appointment_info 表（岗位聘任信息）结构（列名）")
print("=" * 80)

cur.execute("""
    SELECT column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'post_appointment_info'
    ORDER BY ordinal_position;
""")
columns = cur.fetchall()
print(f"\n--- post_appointment_info 表结构（共{len(columns)}列）---")
for col in columns:
    print(f"  列名: {col[0]}, 类型: {col[1]}, 长度: {col[2]}, 可空: {col[3]}")

# 特别检查 post_date, post_1, post_level_1 等字段
target_cols = ['post_date', 'post_1', 'post_level_1', 'post_date_1', 'post_date_2', 'post_2', 'post_level_2']
col_names_list = [c[0] for c in columns]
for tc in target_cols:
    exists = tc in col_names_list
    print(f"  字段 '{tc}' 是否存在: {exists}")

print("\n" + "=" * 80)
print("【任务4】查询 post_appointment_info 表中'杨萍丽'的数据")
print("=" * 80)

# 查找姓名相关列
name_cols = [c[0] for c in columns if 'name' in c[0].lower() or '姓名' in c[0] or '姓' in c[0]]
print(f"可能包含姓名的列: {name_cols}")

found = False
for nc in name_cols:
    try:
        cur.execute(f'SELECT * FROM post_appointment_info WHERE "{nc}" LIKE \'%杨萍丽%\' LIMIT 5;')
        rows = cur.fetchall()
        if rows:
            all_col_names = [desc[0] for desc in cur.description]
            print(f"\n在列 '{nc}' 中找到杨萍丽的数据（{len(rows)}条）:")
            for i, row in enumerate(rows):
                print(f"\n  第{i+1}条:")
                for k, v in zip(all_col_names, row):
                    if v is not None:
                        print(f"    {k}: {v}")
            found = True
            break
    except Exception as e:
        print(f"  在列 '{nc}' 中搜索失败: {e}")

if not found:
    print("\n在姓名列中未找到，尝试全表搜索...")
    for nc in col_names_list:
        try:
            cur.execute(f'SELECT * FROM post_appointment_info WHERE CAST("{nc}" AS TEXT) LIKE \'%杨萍丽%\' LIMIT 5;')
            rows = cur.fetchall()
            if rows:
                all_col_names = [desc[0] for desc in cur.description]
                print(f"\n在列 '{nc}' 中找到杨萍丽的数据（{len(rows)}条）:")
                for i, row in enumerate(rows):
                    print(f"\n  第{i+1}条:")
                    for k, v in zip(all_col_names, row):
                        if v is not None:
                            print(f"    {k}: {v}")
                found = True
                break
        except Exception:
            pass
    if not found:
        print("\n未找到'杨萍丽'的数据")

# 显示前3条数据作为参考
cur.execute("SELECT * FROM post_appointment_info LIMIT 3;")
rows = cur.fetchall()
all_col_names = [desc[0] for desc in cur.description]
print(f"\n--- post_appointment_info 前3条数据（共{len(all_col_names)}列）---")
for i, row in enumerate(rows):
    print(f"\n  第{i+1}条:")
    for k, v in zip(all_col_names, row):
        if v is not None:
            print(f"    {k}: {v}")

cur.close()
conn.close()
print("\n" + "=" * 80)
print("查询完成！")
print("=" * 80)