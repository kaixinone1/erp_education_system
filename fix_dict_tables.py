#!/usr/bin/env python3
"""
修复字典表结构，添加系统自增id
"""

import psycopg2

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def fix_dictionary_table(table_name, code_field, name_field):
    """修复字典表结构"""
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        print(f"\n修复字典表: {table_name}")
        
        # 1. 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table_name,))
        
        if not cursor.fetchone()[0]:
            print(f"  表 {table_name} 不存在，跳过")
            return
        
        # 2. 检查是否已有id字段
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = 'id'
        """, (table_name,))
        
        if cursor.fetchone():
            print(f"  表 {table_name} 已有id字段，跳过")
            return
        
        # 3. 创建新表（带id字段）
        new_table = f"{table_name}_new"
        cursor.execute(f"""
            CREATE TABLE {new_table} (
                id SERIAL PRIMARY KEY,
                code VARCHAR(30),
                name VARCHAR(50),
                sort_order INTEGER,
                status BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. 迁移数据
        cursor.execute(f"""
            INSERT INTO {new_table} (code, name, sort_order, status, created_at)
            SELECT {code_field}, {name_field}, 
                   CASE WHEN {code_field} ~ '^[0-9]+$' THEN {code_field}::INTEGER ELSE NULL END,
                   true,
                   CURRENT_TIMESTAMP
            FROM {table_name}
        """)
        
        migrated = cursor.rowcount
        print(f"  迁移了 {migrated} 条数据")
        
        # 5. 删除旧表，重命名新表
        cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table_name}")
        
        conn.commit()
        print(f"  修复完成")
        
    except Exception as e:
        print(f"  修复失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 修复所有字典表
    dict_tables = [
        ('dict_data_personal_identity', 'code', '个人身份'),
        ('dict_position', 'code', 'name'),
        ('dict_education_dictionary', 'code', '学历'),
    ]
    
    for table, code_field, name_field in dict_tables:
        fix_dictionary_table(table, code_field, name_field)
    
    print("\n所有字典表修复完成！")
