"""
删除牛全胜、白清学、张运勤的退休业务清单
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

def delete_checklists():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    teachers = ['牛全胜', '白清学', '张运勤']
    
    print("=" * 80)
    print(f"删除教师清单: {', '.join(teachers)}")
    print("=" * 80)
    
    try:
        # 查询所有包含这些教师的清单（不限于退休）
        for teacher in teachers:
            print(f"\n查询教师: {teacher}")
            
            # 查询 todo_work 表
            cursor.execute("""
                SELECT id, 教师姓名, 清单名称, 总任务数, 已完成数, 状态
                FROM todo_work
                WHERE 教师姓名 = %s
            """, (teacher,))
            
            rows = cursor.fetchall()
            print(f"  找到 {len(rows)} 个清单:")
            for row in rows:
                print(f"    - ID:{row[0]} | {row[2]} | 任务:{row[4]}/{row[3]} | 状态:{row[5]}")
            
            # 删除这些清单
            if rows:
                for row in rows:
                    cursor.execute("DELETE FROM todo_work WHERE id = %s", (row[0],))
                print(f"  ✓ 已删除 {len(rows)} 个清单")
        
        conn.commit()
        print("\n" + "=" * 80)
        print("删除完成")
        print("=" * 80)
        
        # 验证删除结果
        print("\n验证删除结果:")
        for teacher in teachers:
            cursor.execute("SELECT COUNT(*) FROM todo_work WHERE 教师姓名 = %s", (teacher,))
            count = cursor.fetchone()[0]
            if count == 0:
                print(f"  ✓ {teacher}: 已清空")
            else:
                print(f"  ✗ {teacher}: 仍有 {count} 个清单")
        
    except Exception as e:
        conn.rollback()
        print(f"\n删除失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    delete_checklists()
