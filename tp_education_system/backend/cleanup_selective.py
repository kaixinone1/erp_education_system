"""
选择性清理业务清单实例
保留指定教师的清单，删除其他待处理清单
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

def selective_cleanup():
    """选择性清理清单实例"""
    # 需要保留的教师姓名列表
    keep_teachers = ['白清学', '刘法仁', '张运勤', '薛白智', '李清忠']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("选择性清理业务清单实例")
    print("=" * 80)
    print(f"\n保留的教师: {', '.join(keep_teachers)}")
    
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
        
        print(f"\n找到 {len(template_ids)} 个退休相关模板")
        
        # 2. 查询当前所有待处理的实例
        cursor.execute("""
            SELECT ci.id, ci.关联对象名称, ci.状态, ci.创建时间
            FROM business_checklist_instances ci
            WHERE ci.模板ID IN %s
            AND ci.状态 = '待处理'
            ORDER BY ci.关联对象名称
        """, (tuple(template_ids),))
        
        all_instances = cursor.fetchall()
        print(f"\n当前共有 {len(all_instances)} 个待处理实例")
        
        # 3. 筛选出需要删除的实例（不在保留列表中的教师）
        to_delete = []
        to_keep = []
        
        for instance in all_instances:
            instance_id = instance[0]
            teacher_name = instance[1]
            status = instance[2]
            created_at = instance[3]
            
            if teacher_name in keep_teachers:
                to_keep.append({
                    'id': instance_id,
                    'teacher_name': teacher_name,
                    'created_at': created_at
                })
            else:
                to_delete.append({
                    'id': instance_id,
                    'teacher_name': teacher_name,
                    'created_at': created_at
                })
        
        print(f"\n需要保留的实例: {len(to_keep)} 个")
        for item in to_keep:
            print(f"  - {item['teacher_name']} (ID: {item['id']})")
        
        print(f"\n需要删除的实例: {len(to_delete)} 个")
        print("前20个待删除实例:")
        for i, item in enumerate(to_delete[:20], 1):
            print(f"  {i}. {item['teacher_name']} (ID: {item['id']}, 创建时间: {item['created_at']})")
        
        if len(to_delete) > 20:
            print(f"  ... 还有 {len(to_delete) - 20} 个实例")
        
        # 4. 执行删除
        if to_delete:
            instance_ids = [item['id'] for item in to_delete]
            
            cursor.execute("""
                DELETE FROM business_checklist_instances
                WHERE id IN %s
            """, (tuple(instance_ids),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            print(f"\n已删除 {deleted_count} 个待处理清单实例")
        else:
            print("\n没有需要删除的实例")
        
        # 5. 查询保留的实例和已完成的实例统计
        cursor.execute("""
            SELECT 状态, COUNT(*)
            FROM business_checklist_instances
            WHERE 模板ID IN %s
            GROUP BY 状态
        """, (tuple(template_ids),))
        
        status_counts = cursor.fetchall()
        print(f"\n清理后清单实例统计:")
        for status, count in status_counts:
            print(f"  - {status}: {count} 个")
        
        print("\n" + "=" * 80)
        print("清理完成！")
        print(f"保留了 {len(to_keep)} 个指定教师的待处理清单")
        print(f"已完成的清单保持不变")
        print("=" * 80)
        
    except Exception as e:
        conn.rollback()
        print(f"清理失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    selective_cleanup()
