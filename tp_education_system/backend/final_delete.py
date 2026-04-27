"""
最终删除 - 删除 business_checklist_instances 中的数据
"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def final_delete():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    teachers = ['牛全胜', '白清学', '张运勤']
    
    print("=" * 80)
    print("最终删除 business_checklist_instances 中的数据")
    print("=" * 80)
    
    try:
        # 先查询有哪些数据
        print("\n当前数据:")
        for teacher in teachers:
            cursor.execute("""
                SELECT id, 实例编码, 关联对象名称, 状态, 总任务数, 已完成数
                FROM business_checklist_instances
                WHERE 关联对象名称 = %s
            """, (teacher,))
            
            rows = cursor.fetchall()
            print(f"\n{teacher}: {len(rows)} 条")
            for row in rows:
                print(f"  ID:{row[0]} | {row[1]} | {row[3]} | {row[5]}/{row[4]}")
        
        # 删除数据
        print("\n" + "=" * 80)
        print("开始删除...")
        print("=" * 80)
        
        for teacher in teachers:
            # 先删除关联的任务项记录
            cursor.execute("""
                DELETE FROM business_checklist_item_records
                WHERE 实例ID IN (
                    SELECT id FROM business_checklist_instances
                    WHERE 关联对象名称 = %s
                )
            """, (teacher,))
            records_deleted = cursor.rowcount
            
            # 删除实例
            cursor.execute("""
                DELETE FROM business_checklist_instances
                WHERE 关联对象名称 = %s
            """, (teacher,))
            instances_deleted = cursor.rowcount
            
            print(f"\n{teacher}:")
            print(f"  删除任务项记录: {records_deleted} 条")
            print(f"  删除清单实例: {instances_deleted} 条")
        
        conn.commit()
        
        # 验证
        print("\n" + "=" * 80)
        print("验证删除结果:")
        print("=" * 80)
        
        for teacher in teachers:
            cursor.execute("""
                SELECT COUNT(*) FROM business_checklist_instances
                WHERE 关联对象名称 = %s
            """, (teacher,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                print(f"  ✓ {teacher}: 已彻底删除")
            else:
                print(f"  ✗ {teacher}: 仍有 {count} 条")
        
    except Exception as e:
        conn.rollback()
        print(f"\n删除失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    final_delete()
