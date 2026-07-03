import psycopg2

conn = psycopg2.connect(
    host='localhost', port='5432',
    database='taiping_education',
    user='taiping_user', password='taiping_password'
)
cursor = conn.cursor()

# 删除测试创建的待办 (teacher_id=99999)
cursor.execute("DELETE FROM todo_items WHERE teacher_id = 99999")
deleted = cursor.rowcount
print(f"删除了 {deleted} 条测试待办记录")

conn.commit()
conn.close()
print("清理完成")