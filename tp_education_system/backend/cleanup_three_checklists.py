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
    
    # 要删除的教师名单
    teachers_to_delete = ['牛全胜', '白清学', '张运勤']
    
    print("=" * 80)
    print("删除指定的退休业务清单")
    print(f"目标: {', '.join(teachers_to_delete)}")
    print("=" * 80)
    
    try:
        # ===== 第一部分：清理新版系统的清单 =====
        print("\n【第一部分】清理新版系统清单")
        print("-" * 80)
        
        # 查询退休相关的清单模板
        cursor.execute("""
            SELECT id FROM business_checklist_templates
            WHERE 模板名称 LIKE '%退休%' OR 业务类型 LIKE '%退休%'
        """)
        
        templates = cursor.fetchall()
        template_ids = [t[0] for t in templates]
        
        if template_ids:
            # 查询这三个教师的清单实例
            cursor.execute("""
                SELECT id, 关联对象名称, 总任务数, 已完成数
                FROM business_checklist_instances
                WHERE 模板ID IN %s
                AND 关联对象名称 IN %s
            """, (tuple(template_ids), tuple(teachers_to_delete)))
            
            new_instances = cursor.fetchall()
            print(f"找到 {len(new_instances)} 个新版清单实例:")
            for inst in new_instances:
                print(f"  - {inst[1]} (任务: {inst[3]}/{inst[2]})")
            
            if new_instances:
                instance_ids = [inst[0] for inst in new_instances]
                
                # 删除任务项记录
                cursor.execute("""
                    DELETE FROM business_checklist_item_records
                    WHERE 实例ID IN %s
                """, (tuple(instance_ids),))
                
                # 删除实例
                cursor.execute("""
                    DELETE FROM business_checklist_instances
                    WHERE id IN %s
                """, (tuple(instance_ids),))
                
                print(f"\n已删除 {len(new_instances)} 个新版清单实例")
        
        # ===== 第二部分：清理旧版系统的清单 =====
        print("\n【第二部分】清理旧版系统清单")
        print("-" * 80)
        
        # 查询旧版系统中这三个教师的退休清单
        placeholders = ','.join(['%s'] * len(teachers_to_delete))
        cursor.execute(f"""
            SELECT id, 教师姓名, 清单名称, 总任务数, 已完成数
            FROM todo_work
            WHERE 教师姓名 IN ({placeholders})
            AND 清单名称 LIKE '%退休%'
        """, tuple(teachers_to_delete))
        
        old_instances = cursor.fetchall()
        print(f"找到 {len(old_instances)} 个旧版清单实例:")
        for inst in old_instances:
            print(f"  - {inst[1]}: {inst[2]} (任务: {inst[4]}/{inst[3]})")
        
        if old_instances:
            old_ids = [inst[0] for inst in old_instances]
            
            # 删除旧版清单
            cursor.execute("""
                DELETE FROM todo_work
                WHERE id IN %s
            """, (tuple(old_ids),))
            
            print(f"\n已删除 {len(old_instances)} 个旧版清单实例")
        
        # 提交事务
        conn.commit()
        
        print("\n" + "=" * 80)
        print("清理完成！")
        print("=" * 80)
        
        # 验证清理结果
        print("\n验证清理结果:")
        
        if template_ids:
            cursor.execute("""
                SELECT 关联对象名称 
                FROM business_checklist_instances
                WHERE 模板ID IN %s
                AND 关联对象名称 IN %s
            """, (tuple(template_ids), tuple(teachers_to_delete)))
            
            remaining_new = cursor.fetchall()
            if remaining_new:
                print(f"  ⚠️ 新版系统仍有: {', '.join([r[0] for r in remaining_new])}")
            else:
                print("  ✓ 新版系统已清理干净")
        
        cursor.execute("""
            SELECT 教师姓名 
            FROM todo_work
            WHERE 教师姓名 IN %s
            AND 清单名称 LIKE '%退休%'
        """, (tuple(teachers_to_delete),))
        
        remaining_old = cursor.fetchall()
        if remaining_old:
            print(f"  ⚠️ 旧版系统仍有: {', '.join([r[0] for r in remaining_old])}")
        else:
            print("  ✓ 旧版系统已清理干净")
        
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
