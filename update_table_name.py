import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

# 更新触发条件类型定义中的表名
cursor.execute("""
    UPDATE checklist_trigger_type_defs
    SET 适用表名 = 'teacher_basic_info'
    WHERE 适用表名 = 'teachers'
""")

print(f"更新了 {cursor.rowcount} 条记录")

conn.commit()
cursor.close()
conn.close()

print("完成！")
