#!/usr/bin/env python3
"""
检查上传文件中的身份证号码与主表的匹配情况
"""

import pandas as pd
import psycopg2
import os

DB_PARAMS = {
    'host': 'localhost',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

def check_uploaded_file():
    # 1. 找到最新的上传文件
    upload_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads'
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
    if not files:
        print("没有找到上传的文件！")
        return
    
    # 按时间排序，取最新的
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(upload_dir, latest_file)
    
    print(f"检查文件: {latest_file}")
    print("=" * 80)
    
    # 2. 读取文件
    if latest_file.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    print(f"文件总行数: {len(df)}")
    print(f"文件列名: {list(df.columns)}")
    print()
    
    # 3. 查找身份证号码列
    id_card_col = None
    for col in df.columns:
        if '身份证' in str(col):
            id_card_col = col
            break
    
    if not id_card_col:
        print("错误：找不到身份证号码列！")
        return
    
    print(f"身份证号码列名: {id_card_col}")
    print()
    
    # 4. 获取文件中的身份证号码
    uploaded_id_cards = []
    for idx, value in enumerate(df[id_card_col]):
        if pd.notna(value):
            id_card = str(value).strip()
            if id_card:
                uploaded_id_cards.append((idx + 1, id_card))
    
    print(f"文件中有身份证号码的行数: {len(uploaded_id_cards)}")
    print()
    
    # 5. 获取主表中的身份证号码
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 身份证号码 FROM teacher_basic WHERE 身份证号码 IS NOT NULL')
    master_id_cards = set(row[0] for row in cursor.fetchall())
    
    print(f"主表 teacher_basic 中的身份证号码数量: {len(master_id_cards)}")
    print()
    
    # 6. 对比匹配情况
    matched = []
    not_matched = []
    
    for row_num, id_card in uploaded_id_cards:
        if id_card in master_id_cards:
            matched.append((row_num, id_card))
        else:
            not_matched.append((row_num, id_card))
    
    print("=" * 80)
    print("匹配结果:")
    print("=" * 80)
    print(f"  匹配的身份证号码: {len(matched)} 个")
    print(f"  不匹配的身份证号码: {len(not_matched)} 个")
    print()
    
    # 7. 显示匹配的示例
    if matched:
        print("匹配的身份证号码示例（前10个）:")
        for row_num, id_card in matched[:10]:
            print(f"  第{row_num}行: {id_card}")
        print()
    
    # 8. 显示不匹配的示例
    if not_matched:
        print("不匹配的身份证号码（前20个）:")
        for row_num, id_card in not_matched[:20]:
            print(f"  第{row_num}行: {id_card}")
        print()
        
        if len(not_matched) > 20:
            print(f"  ... 还有 {len(not_matched) - 20} 个不匹配的身份证号码")
    
    # 9. 显示文件前5行数据
    print()
    print("=" * 80)
    print("文件前5行数据:")
    print("=" * 80)
    for idx, row in df.head(5).iterrows():
        print(f"\n第{idx + 1}行:")
        for col in df.columns:
            value = row[col]
            if pd.notna(value):
                print(f"  {col}: {value}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_uploaded_file()
