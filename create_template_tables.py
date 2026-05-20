import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

sql_file = r'd:\erp_thirteen\tp_education_system\backend\database\create_template_tables.sql'

with open(sql_file, 'r', encoding='utf-8') as f:
    sql_content = f.read()

conn = psycopg2.connect(**DATABASE_CONFIG)
cursor = conn.cursor()

try:
    cursor.execute(sql_content)
    conn.commit()
    print('[OK] 数据库表创建成功')
    print('  - template_configs')
    print('  - template_data_records')
    print('  - template_field_values')
except Exception as e:
    conn.rollback()
    print(f'[ERROR] 创建失败: {e}')
finally:
    cursor.close()
    conn.close()
