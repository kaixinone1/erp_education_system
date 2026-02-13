#!/usr/bin/env python3
"""
检查用户上传文件中的身份证号码与主表的匹配情况
"""

import psycopg2
import pandas as pd

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_match(uploaded_file_path):
    """检查上传文件中的身份证与主表的匹配情况"""
    
    # 1. 读取上传的文件
    print(f"读取上传文件: {uploaded_file_path}")
    if uploaded_file_path.endswith('.xlsx') or uploaded_file_path.endswith('.xls'):
        df = pd.read_excel(uploaded_file_path)
    else:
        df = pd.read_csv(uploaded_file_path)
    
    print(f"上传文件共有 {len(df)} 行数据")
    print(f"文件列名: {list(df.columns)}")
    
    # 2. 查找身份证号码列
    id_card_column = None
    for col in df.columns:
        if '身份证' in str(col):
            id_card_column = col
            break
    
    if not id_card_column:
        print("错误：找不到身份证号码列！")
        return
    
    print(f"身份证号码列: {id_card_column}")
    
    # 3. 获取上传文件中的身份证号码
    uploaded_id_cards = set()
    for idx, value in enumerate(df[id_card_column]):
        if pd.notna(value) and str(value).strip():
            uploaded_id_cards.add(str(value).strip())
    
    print(f"上传文件中的身份证号码数量: {len(uploaded_id_cards)}")
    print(f"前10个示例: {list(uploaded_id_cards)[:10]}")
    
    # 4. 获取主表中的身份证号码
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 身份证号码 FROM teacher_basic WHERE 身份证号码 IS NOT NULL')
    master_id_cards = set(row[0] for row in cursor.fetchall())
    
    print(f"\n主表 teacher_basic 中的身份证号码数量: {len(master_id_cards)}")
    
    # 5. 对比匹配情况
    matched = uploaded_id_cards & master_id_cards
    not_matched = uploaded_id_cards - master_id_cards
    
    print(f"\n匹配结果:")
    print(f"  匹配的身份证号码: {len(matched)} 个")
    print(f"  不匹配的身份证号码: {len(not_matched)} 个")
    
    if matched:
        print(f"\n匹配的示例: {list(matched)[:5]}")
    
    if not_matched:
        print(f"\n不匹配的示例（前20个）:")
        for i, id_card in enumerate(list(not_matched)[:20], 1):
            print(f"  {i}. {id_card}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # 请替换为实际的上传文件路径
    import sys
    if len(sys.argv) > 1:
        check_match(sys.argv[1])
    else:
        print("请提供上传文件路径，例如:")
        print("  python check_id_card_match.py '教师学历记录.xlsx'")
