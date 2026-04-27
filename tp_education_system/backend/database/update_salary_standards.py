#!/usr/bin/env python3
"""更新绩效工资标准字典，补充完整所有岗位级别"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def update_salary_standards():
    """更新绩效工资标准"""
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'taiping_education',
        'user': 'taiping_user',
        'password': 'taiping_password'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 根据图片中的岗位结构，补充完整的工资标准
        # 格式: (岗位名称, 岗位级别, 工资标准)
        salary_data = [
            # 行政管理人员
            ('副处级', '副处', 4500.00),
            ('正科级', '正科', 4000.00),
            ('副科级', '副科', 3600.00),
            ('科员级', '科员', 3200.00),
            ('办事员级', '办事员', 2800.00),
            
            # 专业技术人员
            ('正高级教师', '正高级', 4800.00),
            ('高级教师', '高级', 4200.00),
            ('一级教师', '一级', 3600.00),
            ('二级教师', '二级', 3000.00),
            ('三级教师', '三级', 2600.00),
            
            # 工人
            ('高级技师', '高级技师', 3400.00),
            ('技师', '技师', 3000.00),
            ('高级工', '高级工', 2600.00),
            ('中级工', '中级工', 2400.00),
            ('初级工', '初级工', 2200.00),
            ('普工', '普工', 2000.00),
        ]
        
        inserted_count = 0
        updated_count = 0
        
        for position_name, position_level, salary in salary_data:
            # 先检查是否已存在
            cursor.execute("""
                SELECT id FROM performance_salary_standard 
                WHERE position_name = %s AND position_level = %s AND status = 'active'
            """, (position_name, position_level))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute("""
                    UPDATE performance_salary_standard 
                    SET salary_standard = %s, updated_at = NOW()
                    WHERE id = %s
                """, (salary, existing[0]))
                updated_count += 1
                print(f"[UPDATE] {position_name} ({position_level}): {salary}")
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO performance_salary_standard 
                    (position_name, position_level, salary_standard, effective_date, status, created_at, updated_at)
                    VALUES (%s, %s, %s, '2024-01-01', 'active', NOW(), NOW())
                """, (position_name, position_level, salary))
                inserted_count += 1
                print(f"[INSERT] {position_name} ({position_level}): {salary}")
        
        conn.commit()
        print(f"\n[OK] 完成: 新增 {inserted_count} 条, 更新 {updated_count} 条")
        
        # 查询所有数据确认
        cursor.execute("""
            SELECT position_name, position_level, salary_standard 
            FROM performance_salary_standard 
            WHERE status = 'active'
            ORDER BY position_name, position_level
        """)
        
        print("\n当前绩效工资标准字典:")
        print("-" * 60)
        for row in cursor.fetchall():
            print(f"  {row[0]:12s} | {row[1]:10s} | {row[2]:8.2f} 元")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] 执行失败: {e}")
        return False
    
    return True

if __name__ == '__main__':
    update_salary_standards()
