import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查 id_card 表的数据
print('1. id_card 表的前5条数据：')
print('=' * 50)
cursor.execute("SELECT * FROM id_card LIMIT 5")
columns = [desc[0] for desc in cursor.description]
print(f"列名: {columns}")
for row in cursor.fetchall():
    print(f"  {row}")

# 检查 teacher_basic_info 表是否有数据
print('\n2. teacher_basic_info 表记录数：')
print('=' * 50)
cursor.execute("SELECT COUNT(*) FROM teacher_basic_info")
count = cursor.fetchone()[0]
print(f"  记录数: {count}")

if count > 0:
    cursor.execute("SELECT * FROM teacher_basic_info LIMIT 3")
    columns = [desc[0] for desc in cursor.description]
    print(f"  列名: {columns}")

# 检查 person_tags 表是否有数据
print('\n3. person_tags 表记录数：')
print('=' * 50)
cursor.execute("SELECT COUNT(*) FROM person_tags")
count = cursor.fetchone()[0]
print(f"  记录数: {count}")

if count > 0:
    cursor.execute("SELECT * FROM person_tags LIMIT 5")
    columns = [desc[0] for desc in cursor.description]
    print(f"  列名: {columns}")
    for row in cursor.fetchall():
        print(f"  {row}")

# 检查 employee_tag_relations 表
print('\n4. employee_tag_relations 表记录数：')
print('=' * 50)
cursor.execute("SELECT COUNT(*) FROM employee_tag_relations")
count = cursor.fetchone()[0]
print(f"  记录数: {count}")

cursor.close()
conn.close()
