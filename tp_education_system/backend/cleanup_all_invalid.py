"""
清理所有无效的退休业务清单实例
包括：
1. 新版系统中没有任务项记录的清单实例
2. 旧版系统中所有待处理的退休业务清单
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

def cleanup_all_invalid():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("清理所有无效的退休业务清单")
    print("=" * 80)
    
    try:
        # ===== 第一部分：清理新版系统的无效清单 =====
        print("\n【第一部分】清理新版系统无效清单")
        print("-" * 80)
        
        # 查询退休相关的清单模板
        cursor.execute("""
            SELECT id, 模板编码, 模板名称
            FROM business_checklist_templates
            WHERE 模板名称 LIKE '%退休%' OR 业务类型 LIKE '%退休%'
        """)
        
        retirement_templates = cursor.fetchall()
        template_ids = [t[0] for t in retirement_templates]
        
        if template_ids:
            print(f"找到 {len(template_ids)} 个退休相关模板")
            
            # 查询没有任务项记录的清单实例
            cursor.execute("""
                SELECT ci.id, ci.关联对象名称, ci.总任务数
                FROM business_checklist_instances ci
                LEFT JOIN business_checklist_item_records r ON ci.id = r.实例ID
                WHERE ci.模板ID IN %s
                GROUP BY ci.id, ci.关联对象名称, ci.总任务数
                HAVING COUNT(r.id) = 0
            """, (tuple(template_ids),))
            
            invalid_instances = cursor.fetchall()
            print(f"\n找到 {len(invalid_instances)} 个没有任务项记录的清单实例:")
            
            for inst in invalid_instances:
                print(f"  - {inst[1]} (ID: {inst[0]}, 总任务数: {inst[2]})")
            
            if invalid_instances:
                instance_ids = [inst[0] for inst in invalid_instances]
                
                # 删除这些实例
                cursor.execute("""
                    DELETE FROM business_checklist_instances
                    WHERE id IN %s
                """, (tuple(instance_ids),))
                
                deleted = cursor.rowcount
                print(f"\n已删除 {deleted} 个无效的新版清单实例")
        
        # ===== 第二部分：清理旧版系统的退休业务清单 =====
        print("\n【第二部分】清理旧版系统退休业务清单")
        print("-" * 80)
        
        # 查询旧版系统中所有退休相关的待处理清单
        cursor.execute("""
            SELECT id, 教师姓名, 清单名称, 总任务数, 已完成数
            FROM todo_work
            WHERE 清单名称 LIKE '%退休%'
            AND 状态 = 'pending'
            ORDER BY 教师姓名
        """)
        
        old_checklists = cursor.fetchall()
        print(f"\n找到 {len(old_checklists)} 个旧版退休业务清单:")
        
        for old in old_checklists:
            print(f"  - {old[1]}: {old[2]} (任务: {old[4]}/{old[3]})")
        
        if old_checklists:
            old_ids = [old[0] for old in old_checklists]
            
            # 删除旧版清单
            cursor.execute("""
                DELETE FROM todo_work
                WHERE id IN %s
            """, (tuple(old_ids),))
            
            old_deleted = cursor.rowcount
            print(f"\n已删除 {old_deleted} 个旧版退休业务清单")
        
        # 提交事务
        conn.commit()
        
        print("\n" + "=" * 80)
        print("清理完成！")
        print("=" * 80)
        
        # 查询清理后的统计
        if template_ids:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM business_checklist_instances
                WHERE 模板ID IN %s
            """, (tuple(template_ids),))
            
            remaining_new = cursor.fetchone()[0]
            print(f"\n新版系统剩余 {remaining_new} 个退休业务清单实例")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM todo_work
            WHERE 清单名称 LIKE '%退休%'
        """)
        
        remaining_old = cursor.fetchone()[0]
        print(f"旧版系统剩余 {remaining_old} 个退休业务清单")
        
    except Exception as e:
        conn.rollback()
        print(f"\n清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    cleanup_all_invalid()
