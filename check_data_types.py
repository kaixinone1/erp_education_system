#!/usr/bin/env python3
"""
检查上传文件中的数据类型
"""

import pandas as pd
import os

def check():
    upload_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads'
    files = [f for f in os.listdir(upload_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
    files.sort(reverse=True)
    latest_file = files[0]
    file_path = os.path.join(upload_dir, latest_file)
    
    print(f"检查文件: {latest_file}")
    print("=" * 80)
    
    # 读取文件
    if latest_file.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    print(f"\n文件列的数据类型:")
    print(df.dtypes)
    
    print(f"\n\n前10行数据:")
    print(df.head(10))
    
    print(f"\n\n学历类型的唯一值:")
    print(df['学历类型'].unique())
    print(f"类型: {df['学历类型'].dtype}")
    
    print(f"\n\n学历的唯一值:")
    print(df['学历'].unique())
    print(f"类型: {df['学历'].dtype}")

if __name__ == "__main__":
    check()
