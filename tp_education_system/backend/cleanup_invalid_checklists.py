"""
清理无效的退休业务清单实例
- 删除没有子任务（总任务数为0）的清单
- 删除无法完成操作的清单（保留有进度但无法操作的）
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

def cleanup_invalid_checklists():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("清理无效的退休业务清单实例")
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
            print("没有找到退休相关模板")
            return
        
        print(f"\n找到 {len(template_ids)} 个退休相关模板:")
        for t in retirement_templates:
            print(f"  - {t[2]} (编码: {t[1]})")
        
        # 2. 查询所有待处理的退休业务清单实例
        cursor.execute("""
            SELECT ci.id, ci.实例编码, ci.关联对象名称, ci.总任务数, ci.已完成数, ci.状态
            FROM business_checklist_instances ci
            WHERE ci.模板ID IN %s
            AND ci.状态 IN ('待处理', '进行中')
            ORDER BY ci.关联对象名称
        """, (tuple(template_ids),))
        
        all_instances = cursor.fetchall()
        print(f"\n当前共有 {len(all_instances)} 个待处理/进行中的退休业务清单实例")
        
        # 3. 筛选出需要删除的实例
        # 条件1: 总任务数为0（没有子任务）
        # 条件2: 保留有完成进度的（已完成数>0）
        to_delete = []
        to_keep = []
        
        for instance in all_instances:
            instance_id = instance[0]
            instance_code = instance[1]
            teacher_name = instance[2]
            total_tasks = instance[3]
            completed_tasks = instance[4]
            status = instance[5]
            
            # 如果没有子任务（总任务数为0），删除
            if total_tasks == 0 or total_tasks is None:
                to_delete.append({
                    'id': instance_id,
                    'teacher_name': teacher_name,
                    'reason': '没有子任务',
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks
                })
            else:
                to_keep.append({
                    'id': instance_id,
                    'teacher_name': teacher_name,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks
                })
        
        print(f"\n需要删除的实例（没有子任务）: {len(to_delete)} 个")
        for item in to_delete:
            print(f"  - {item['teacher_name']} (ID: {item['id']}, 原因: {item['reason']})")
        
        print(f"\n保留的实例（有子任务）: {len(to_keep)} 个")
        for item in to_keep:
            print(f"  - {item['teacher_name']} (ID: {item['id']}, 任务: {item['completed_tasks']}/{item['total_tasks']})")
        
        # 4. 执行删除
        if to_delete:
            instance_ids = [item['id'] for item in to_delete]
            
            # 先删除关联的任务项记录
            cursor.execute("""
                DELETE FROM business_checklist_item_records
                WHERE 实例ID IN %s
            """, (tuple(instance_ids),))
            
            records_deleted = cursor.rowcount
            print(f"\n已删除 {records_deleted} 个关联任务项记录")
            
            # 再删除实例
            cursor.execute("""
                DELETE FROM business_checklist_instances
                WHERE id IN %s
            """, (tuple(instance_ids),))
            
            instances_deleted = cursor.rowcount
            print(f"已删除 {instances_deleted} 个清单实例")
            
            conn.commit()
            print(f"\n清理完成！共清理 {instances_deleted} 个无效的退休业务清单实例")
        else:
            print("\n没有需要删除的实例")
        
        # 5. 查询清理后的统计
        cursor.execute("""
            SELECT COUNT(*) 
            FROM business_checklist_instances
            WHERE 模板ID IN %s
            AND 状态 IN ('待处理', '进行中')
        """, (tuple(template_ids),))
        
        remaining = cursor.fetchone()[0]
        print(f"\n清理后剩余 {remaining} 个待处理/进行中的退休业务清单实例")
        
    except Exception as e:
        conn.rollback()
        print(f"\n清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    cleanup_invalid_checklists()
