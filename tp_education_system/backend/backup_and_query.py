"""备份数据库并查询所有包含调出的表和字段"""
import psycopg2
import time
import os
import subprocess

# 数据库连接参数
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'taiping_education_fifteen',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def backup_database():
    """备份数据库"""
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_dir = r'D:\erp_fifteen\tp_education_system\备份\数据库自动备份'
    backup_file = os.path.join(backup_dir, f'taiping_education_{timestamp}.sql')
    
    # 尝试找到pg_dump
    pg_dump_paths = [
        r'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\14\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\13\bin\pg_dump.exe',
        'pg_dump'  # 从PATH查找
    ]
    
    pg_dump = None
    for path in pg_dump_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                pg_dump = path
                print(f"找到pg_dump: {path}")
                print(f"版本: {result.stdout.strip()}")
                break
        except FileNotFoundError:
            continue
    
    if not pg_dump:
        print("警告: 未找到pg_dump，跳过备份")
        return None
    
    cmd = [
        pg_dump,
        '-h', DB_CONFIG['host'],
        '-p', str(DB_CONFIG['port']),
        '-U', DB_CONFIG['user'],
        '-d', DB_CONFIG['dbname'],
        '-f', backup_file
    ]
    
    # 设置PGPASSWORD环境变量
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_CONFIG['password']
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    if result.returncode == 0 and os.path.exists(backup_file):
        file_size = os.path.getsize(backup_file)
        print(f"备份成功: {backup_file}")
        print(f"文件大小: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        return backup_file
    else:
        print(f"备份失败: {result.stderr}")
        return None

def query_diao_chu_fields():
    """查询数据库中所有包含'调出'的表和字段"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("\n=== 查询包含'调出'的表和字段 ===")
    
    # 查询所有包含"调出"的字段
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND (column_name LIKE '%调出%' OR column_name LIKE '%diao_chu%')
        ORDER BY table_name, column_name
    """)
    columns = cur.fetchall()
    print(f"\n包含'调出'或'diao_chu'的字段: {len(columns)}个")
    for table, col, dtype in columns:
        print(f"  表: {table}, 字段: {col}, 类型: {dtype}")
    
    # 查询所有包含"调出"值的数据
    print("\n=== 查询包含'调出'值的数据 ===")
    
    # 先查看teacher_basic_info表的所有包含"调出"的字段
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'teacher_basic_info' AND column_name LIKE '%调出%'
    """)
    tbi_cols = cur.fetchall()
    print(f"teacher_basic_info中包含'调出'的字段: {tbi_cols}")
    
    # teacher_basic_info表 - 查询任职状态为调出的记录
    cur.execute("""
        SELECT COUNT(*) FROM teacher_basic_info 
        WHERE "任职状态" = '调出'
    """)
    count = cur.fetchone()[0]
    print(f"teacher_basic_info中任职状态为'调出'的记录数: {count}")
    
    cur.execute("""
        SELECT id, "姓名", "任职状态"
        FROM teacher_basic_info 
        WHERE "任职状态" = '调出'
        LIMIT 10
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"  ID:{row[0]}, 姓名:{row[1]}, 任职状态:{row[2]}")
    
    # id_card表
    cur.execute("""
        SELECT COUNT(*) FROM id_card WHERE diao_chu IS NOT NULL AND diao_chu != ''
    """)
    count_id_card = cur.fetchone()[0]
    print(f"\nid_card表中diao_chu字段有值的记录数: {count_id_card}")
    
    # personal_dict_dictionary表中的调出标签
    cur.execute("""
        SELECT * FROM personal_dict_dictionary 
        WHERE biao_qian LIKE '%调出%'
        LIMIT 5
    """)
    tags = cur.fetchall()
    # 获取列名
    col_names = [desc[0] for desc in cur.description]
    print(f"\npersonal_dict_dictionary中包含调出的标签: {len(tags)}个")
    print(f"  表结构列名: {col_names}")
    for tag in tags:
        print(f"  {dict(zip(col_names, tag))}")
    
    # employee_tag_relations表中的调出标签关系
    cur.execute("""
        SELECT etr.id, etr.tag_id, etr.employee_id, pdd.biao_qian
        FROM employee_tag_relations etr
        LEFT JOIN personal_dict_dictionary pdd ON etr.tag_id = pdd.id
        WHERE pdd.biao_qian = '调出'
        LIMIT 10
    """)
    relations = cur.fetchall()
    print(f"\nemployee_tag_relations中调出标签关系: {len(relations)}条")
    for rel in relations:
        print(f"  关系ID:{rel[0]}, 标签ID:{rel[1]}, 职工ID:{rel[2]}, 标签名:{rel[3]}")
    
    # personnel_change_records表
    try:
        cur.execute("""
            SELECT COUNT(*) FROM personnel_change_records 
            WHERE new_status = '调出' OR old_status = '调出'
        """)
        change_count = cur.fetchone()[0]
        print(f"\npersonnel_change_records中调出变动记录: {change_count}条")
    except Exception as e:
        print(f"\npersonnel_change_records查询失败: {e}")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("开始数据库备份和查询")
    print("=" * 60)
    
    backup_file = backup_database()
    query_diao_chu_fields()
    
    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)
