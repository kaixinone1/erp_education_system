"""
删除指定的三个退休业务清单
- 牛全胜
- 白清学  
- 张运勤
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

def cleanup_three_checklists():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("删除指定的退休业务清单")
    print("=" * 80)
    
    try:
        # 查询旧版系统中这三个教师的退休清单
        cursor.execute("""
            SELECT id, 教师姓名, 清单名称, 总任务数, 已完成数
            FROM todo_work
            WHERE (教师姓名 = '牛全胜' OR 教师姓名 = '白清学' OR 教师姓名 = '张运勤')
            AND 清单名称 LIKE '%退休%'
        """)
        
        old_instances = cursor.fetchall()
        print(f"找到 {len(old_instances)} 个旧版清单实例:")
        for inst in old_instances:
            print(f"  - {inst[1]}: {inst[2]} (任务: {inst[4]}/{inst[3]})")
        
        if old_instances:
            # 逐个删除
            deleted_count = 0
            for inst in old_instances:
                cursor.execute("DELETE FROM todo_work WHERE id = %s", (inst[0],))
                deleted_count += 1
            
            print(f"\n已删除 {deleted_count} 个旧版清单实例")
        
        # 提交事务
        conn.commit()
        
        print("\n" + "=" * 80)
        print("清理完成！")
        print("=" * 80)
        
        # 验证清理结果
        cursor.execute("""
            SELECT 教师姓名 
            FROM todo_work
            WHERE (教师姓名 = '牛全胜' OR 教师姓名 = '白清学' OR 教师姓名 = '张运勤')
            AND 清单名称 LIKE '%退休%'
        """)
        
        remaining = cursor.fetchall()
        if remaining:
            print(f"\n⚠️ 仍有未删除: {', '.join([r[0] for r in remaining])}")
        else:
            print("\n✓ 已清理干净")
        
    except Exception as e:
        conn.rollback()
        print(f"\n清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    cleanup_three_checklists()
