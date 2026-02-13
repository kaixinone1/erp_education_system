#!/usr/bin/env python3
"""
在退休呈报数据表的身份证号码后面添加"个人编号"字段
并同步更新配置文件
"""
import json
import psycopg2

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

SCHEMA_FILE = r'd:\erp_thirteen\tp_education_system\backend\config\merged_schema_mappings.json'


def add_field_to_database():
    """在数据库表中添加个人编号字段"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    # 检查字段是否已存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'retirement_report_data' AND column_name = '个人编号'
    """)
    
    if cursor.fetchone():
        print("字段'个人编号'已存在")
    else:
        # 在身份证号码后面添加个人编号字段
        cursor.execute("""
            ALTER TABLE retirement_report_data 
            ADD COLUMN 个人编号 VARCHAR(50)
        """)
        conn.commit()
        print("已在数据库中添加'个人编号'字段")
    
    cursor.close()
    conn.close()


def update_schema_config():
    """更新配置文件，在身份证号码字段后面添加个人编号字段"""
    # 读取配置文件
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    table = config['tables'].get('retirement_report_data')
    if not table:
        print("未找到 retirement_report_data 表配置")
        return
    
    fields = table.get('fields', [])
    
    # 检查字段是否已存在
    for field in fields:
        if field.get('targetField') == '个人编号' or field.get('english_name') == '个人编号':
            print("字段'个人编号'已在配置文件中")
            return
    
    # 找到身份证号码字段的位置
    id_card_index = -1
    for i, field in enumerate(fields):
        field_name = field.get('targetField') or field.get('english_name', '')
        if field_name == '身份证号码':
            id_card_index = i
            break
    
    if id_card_index == -1:
        print("未找到'身份证号码'字段，将添加到末尾")
        insert_index = len(fields)
    else:
        insert_index = id_card_index + 1
        print(f"找到'身份证号码'字段在位置 {id_card_index}，将在位置 {insert_index} 插入'个人编号'")
    
    # 创建新字段配置
    new_field = {
        'targetField': '个人编号',
        'english_name': '个人编号',
        'sourceField': '个人编号',
        'chinese_name': '个人编号',
        'dataType': 'VARCHAR',
        'data_type': 'VARCHAR',
        'required': False,
        'length': 50
    }
    
    # 插入新字段
    fields.insert(insert_index, new_field)
    
    # 保存配置文件
    with open(SCHEMA_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("配置文件已更新！")
    print(f"'个人编号'字段已添加到位置 {insert_index}")


def verify_update():
    """验证更新结果"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, ordinal_position
        FROM information_schema.columns
        WHERE table_name = 'retirement_report_data'
        ORDER BY ordinal_position
    """)
    
    print("\n数据库表字段顺序（部分）:")
    for row in cursor.fetchall():
        if row[0] in ['身份证号码', '个人编号', '岗位', '姓名']:
            print(f"  位置{row[1]}: {row[0]}")
    
    cursor.close()
    conn.close()


if __name__ == '__main__':
    print("=== 添加'个人编号'字段 ===\n")
    
    # 1. 更新数据库
    add_field_to_database()
    
    # 2. 更新配置文件
    update_schema_config()
    
    # 3. 验证结果
    verify_update()
    
    print("\n=== 完成 ===")
