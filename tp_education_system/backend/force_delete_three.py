"""
强制删除牛全胜、白清学、张运勤的所有清单数据
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

def force_delete():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    teachers = ['牛全胜', '白清学', '张运勤']
    
    print("=" * 80)
    print("强制删除三个教师的所有清单数据")
    print("=" * 80)
    
    try:
        # 1. 删除 todo_work 表中的数据
        print("\n1. 删除 todo_work 表数据")
        for teacher in teachers:
            cursor.execute("DELETE FROM todo_work WHERE 教师姓名 = %s", (teacher,))
            print(f"   {teacher}: 删除 {cursor.rowcount} 条")
        
        # 2. 删除 business_checklist_instances 表中的数据
        print("\n2. 删除 business_checklist_instances 表数据")
        for teacher in teachers:
            cursor.execute("DELETE FROM business_checklist_instances WHERE 关联对象名称 = %s", (teacher,))
            print(f"   {teacher}: 删除 {cursor.rowcount} 条")
        
        # 3. 检查 death_todo_list 表
        print("\n3. 检查 death_todo_list 表")
        try:
            for teacher in teachers:
                cursor.execute("DELETE FROM death_todo_list WHERE 教师姓名 = %s", (teacher,))
                print(f"   {teacher}: 删除 {cursor.rowcount} 条")
        except:
            print("   表不存在或没有数据")
        
        # 4. 检查 retirement_checklists 表
        print("\n4. 检查 retirement_checklists 表")
        try:
            for teacher in teachers:
                cursor.execute("DELETE FROM retirement_checklists WHERE 教师姓名 = %s", (teacher,))
                print(f"   {teacher}: 删除 {cursor.rowcount} 条")
        except:
            print("   表不存在或没有数据")
        
        # 5. 检查 教师死亡待办工作 表
        print("\n5. 检查 教师死亡待办工作 表")
        try:
            for teacher in teachers:
                cursor.execute("DELETE FROM 教师死亡待办工作 WHERE 教师姓名 = %s", (teacher,))
                print(f"   {teacher}: 删除 {cursor.rowcount} 条")
        except:
            print("   表不存在或没有数据")
        
        conn.commit()
        print("\n" + "=" * 80)
        print("删除完成！")
        print("=" * 80)
        
        # 验证
        print("\n验证结果:")
        for teacher in teachers:
            cursor.execute("SELECT COUNT(*) FROM todo_work WHERE 教师姓名 = %s", (teacher,))
            todo_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM business_checklist_instances WHERE 关联对象名称 = %s", (teacher,))
            instance_count = cursor.fetchone()[0]
            
            if todo_count == 0 and instance_count == 0:
                print(f"   ✓ {teacher}: 已彻底删除")
            else:
                print(f"   ✗ {teacher}: todo_work={todo_count}, instances={instance_count}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n删除失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    force_delete()
