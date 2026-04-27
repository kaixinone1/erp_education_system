"""
自动清理有问题的退休业务清单实例
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

def delete_problematic_instances():
    """删除有问题的清单实例"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("开始自动清理有问题的退休业务清单实例")
    print("=" * 80)
    
    try:
        # 1. 查询所有退休相关的清单模板
        cursor.execute("""
            SELECT id, 模板编码, 模板名称
            FROM business_checklist_templates
            WHERE 模板名称 LIKE '%退休%' OR 业务类型 LIKE '%退休%'
        """)
        
        retirement_templates = cursor.fetchall()
        template_ids = [t[0] for t in retirement_templates]
        
        if not template_ids:
            print("没有找到退休相关模板，无需清理")
            return
        
        print(f"找到 {len(template_ids)} 个退休相关模板")
        for t in retirement_templates:
            print(f"  - {t[2]} (编码: {t[1]})")
        
        # 2. 查询需要删除的实例（教师当前状态不是退休的实例）
        cursor.execute("""
            SELECT ci.id, ci.关联对象名称, ci.创建时间, t.employment_status
            FROM business_checklist_instances ci
            JOIN teacher_basic_info t ON ci.关联对象ID = t.id
            WHERE ci.模板ID IN %s
            AND t.employment_status != '退休'
            AND ci.状态 IN ('待处理', '进行中')
        """, (tuple(template_ids),))
        
        to_delete = cursor.fetchall()
        print(f"\n找到 {len(to_delete)} 个需要删除的实例（教师当前不是退休状态）:")
        
        for item in to_delete:
            print(f"  - 实例ID: {item[0]}, 教师: {item[1]}, 当前状态: {item[3]}, 创建时间: {item[2]}")
        
        if to_delete:
            # 3. 删除这些实例
            instance_ids = [item[0] for item in to_delete]
            
            # 删除实例
            cursor.execute("""
                DELETE FROM business_checklist_instances
                WHERE id IN %s
            """, (tuple(instance_ids),))
            
            instances_deleted = cursor.rowcount
            print(f"\n已删除 {instances_deleted} 个清单实例")
            
            conn.commit()
            print(f"\n清理完成！共清理 {instances_deleted} 个有问题的退休业务清单实例")
        else:
            print("\n没有需要删除的实例")
        
    except Exception as e:
        conn.rollback()
        print(f"清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    delete_problematic_instances()
