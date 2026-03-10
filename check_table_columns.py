import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    database='taiping_education',
    user='taiping_user',
    password='taiping_password'
)
cursor = conn.cursor()

# 检查几个可能的表的字段
tables_to_check = ['id_card', 'teacher_personal_identity', 'dict_personal_identity_dictionary']

for table_name in tables_to_check:
    print(f'\n表: {table_name}')
    print('=' * 50)
    try:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = [row[0] for row in cursor.fetchall()]
        for col in columns:
            print(f'  {col}')
    except Exception as e:
        print(f'  错误: {e}')

cursor.close()
conn.close()
