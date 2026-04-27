"""
清理错误推送的退休业务清单实例
由于之前的触发逻辑错误，系统为已经退休的教师创建了重复的清单实例
此脚本用于查询和清理这些错误的实例
"""
import psycopg2
import json
from datetime import datetime

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def query_problematic_instances():
    """查询可能存在问题的退休业务清单实例"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("查询可能存在问题的退休业务清单实例")
    print("=" * 80)
    
    # 1. 查询所有退休相关的清单模板
    cursor.execute("""
        SELECT id, 模板编码, 模板名称, 业务类型
        FROM business_checklist_templates
        WHERE 模板名称 LIKE '%退休%' OR 业务类型 LIKE '%退休%'
    """)
    
    retirement_templates = cursor.fetchall()
    print(f"\n找到 {len(retirement_templates)} 个退休相关模板:")
    template_ids = []
    for template in retirement_templates:
        print(f"  - ID: {template[0]}, 编码: {template[1]}, 名称: {template[2]}, 业务类型: {template[3]}")
        template_ids.append(template[0])
    
    if not template_ids:
        print("没有找到退休相关模板")
        cursor.close()
        conn.close()
        return
    
    # 2. 查询这些模板对应的所有实例
    cursor.execute("""
        SELECT ci.id, ci.实例编码, ci.关联对象ID, ci.关联对象名称, 
               ci.状态, ci.创建时间, ci.触发事件,
               t.employment_status
        FROM business_checklist_instances ci
        JOIN teacher_basic_info t ON ci.关联对象ID = t.id
        WHERE ci.模板ID IN %s
        ORDER BY ci.创建时间 DESC
    """, (tuple(template_ids),))
    
    instances = cursor.fetchall()
    print(f"\n找到 {len(instances)} 个退休业务清单实例")
    
    # 3. 分析哪些实例可能有问题（教师早已退休但最近创建的实例）
    problematic_instances = []
    
    for instance in instances:
        instance_id = instance[0]
        instance_code = instance[1]
        teacher_id = instance[2]
        teacher_name = instance[3]
        status = instance[4]
        created_at = instance[5]
        trigger_event = instance[6]
        current_employment_status = instance[7]
        
        # 如果教师当前状态不是退休，但实例是退休清单，可能有问题
        if current_employment_status != '退休':
            problematic_instances.append({
                'instance_id': instance_id,
                'teacher_name': teacher_name,
                'reason': f'教师当前状态为"{current_employment_status}"，不是退休状态',
                'created_at': created_at
            })
    
    print(f"\n其中可能有问题的实例: {len(problematic_instances)} 个")
    
    if problematic_instances:
        print("\n问题实例列表（前20个）:")
        for i, item in enumerate(problematic_instances[:20], 1):
            print(f"  {i}. 实例ID: {item['instance_id']}, 教师: {item['teacher_name']}")
            print(f"     原因: {item['reason']}, 创建时间: {item['created_at']}")
    
    cursor.close()
    conn.close()
    
    return problematic_instances, template_ids

def delete_problematic_instances():
    """删除有问题的清单实例"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("开始清理有问题的退休业务清单实例")
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
        
        # 2. 查询需要删除的实例（教师当前状态不是退休的实例）
        cursor.execute("""
            SELECT ci.id, ci.关联对象名称, ci.创建时间
            FROM business_checklist_instances ci
            JOIN teacher_basic_info t ON ci.关联对象ID = t.id
            WHERE ci.模板ID IN %s
            AND t.employment_status != '退休'
            AND ci.状态 IN ('待处理', '进行中')
        """, (tuple(template_ids),))
        
        to_delete = cursor.fetchall()
        print(f"\n找到 {len(to_delete)} 个需要删除的实例（教师当前不是退休状态）:")
        
        for item in to_delete[:10]:
            print(f"  - 实例ID: {item[0]}, 教师: {item[1]}, 创建时间: {item[2]}")
        
        if len(to_delete) > 10:
            print(f"  ... 还有 {len(to_delete) - 10} 个实例")
        
        if to_delete:
            # 3. 删除这些实例
            instance_ids = [item[0] for item in to_delete]
            
            # 先删除关联的任务项
            cursor.execute("""
                DELETE FROM business_checklist_tasks
                WHERE 实例ID IN %s
            """, (tuple(instance_ids),))
            
            tasks_deleted = cursor.rowcount
            print(f"\n已删除 {tasks_deleted} 个关联任务项")
            
            # 再删除实例
            cursor.execute("""
                DELETE FROM business_checklist_instances
                WHERE id IN %s
            """, (tuple(instance_ids),))
            
            instances_deleted = cursor.rowcount
            print(f"已删除 {instances_deleted} 个清单实例")
            
            conn.commit()
            print(f"\n清理完成！")
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

def query_all_retirement_instances():
    """查询所有退休业务清单实例的统计信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "=" * 80)
    print("退休业务清单实例统计")
    print("=" * 80)
    
    # 查询所有退休相关的清单模板
    cursor.execute("""
        SELECT id, 模板名称
        FROM business_checklist_templates
        WHERE 模板名称 LIKE '%退休%' OR 业务类型 LIKE '%退休%'
    """)
    
    templates = cursor.fetchall()
    
    for template_id, template_name in templates:
        print(f"\n模板: {template_name}")
        
        # 统计各状态的实例数量
        cursor.execute("""
            SELECT 状态, COUNT(*)
            FROM business_checklist_instances
            WHERE 模板ID = %s
            GROUP BY 状态
        """, (template_id,))
        
        status_counts = cursor.fetchall()
        for status, count in status_counts:
            print(f"  - {status}: {count} 个")
        
        # 查询最近创建的10个实例
        cursor.execute("""
            SELECT ci.关联对象名称, ci.状态, ci.创建时间, t.employment_status
            FROM business_checklist_instances ci
            JOIN teacher_basic_info t ON ci.关联对象ID = t.id
            WHERE ci.模板ID = %s
            ORDER BY ci.创建时间 DESC
            LIMIT 10
        """, (template_id,))
        
        recent = cursor.fetchall()
        if recent:
            print(f"\n  最近创建的实例:")
            for item in recent:
                print(f"    - {item[0]} | 状态:{item[1]} | 创建:{item[2]} | 教师当前状态:{item[3]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("退休业务清单清理工具")
    print("=" * 80)
    print("1. 查询所有退休业务清单实例统计")
    print("2. 查询可能存在问题的实例")
    print("3. 删除有问题的实例（教师当前不是退休状态的实例）")
    print("4. 退出")
    print("=" * 80)
    
    choice = input("\n请选择操作 (1-4): ").strip()
    
    if choice == "1":
        query_all_retirement_instances()
    elif choice == "2":
        query_problematic_instances()
    elif choice == "3":
        confirm = input("\n确认删除有问题的实例吗？此操作不可恢复！(yes/no): ").strip().lower()
        if confirm == "yes":
            delete_problematic_instances()
        else:
            print("已取消删除操作")
    elif choice == "4":
        print("退出")
    else:
        print("无效选择")
