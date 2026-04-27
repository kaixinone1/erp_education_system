"""
更新80岁高龄补贴业务清单为4个复选项任务
"""
import psycopg2
import json

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

def update():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("=== 更新80岁高龄补贴业务清单 ===\n")
        
        # 1. 查找高龄模板
        print("1. 查找高龄补贴模板...")
        cursor.execute("""
            SELECT id, 模板名称 FROM business_checklist_templates
            WHERE 业务类型 = 'OCTOGENARIAN'
        """)
        
        row = cursor.fetchone()
        if not row:
            print("   ❌ 未找到高龄补贴模板")
            return
        
        template_id = row[0]
        template_name = row[1]
        print(f"   ✓ 找到模板: {template_name} (ID: {template_id})")
        
        # 2. 删除旧的任务项
        print("\n2. 删除旧的任务项...")
        cursor.execute("""
            DELETE FROM business_checklist_items
            WHERE 模板ID = %s
        """, (template_id,))
        print(f"   ✓ 删除了旧任务项")
        
        # 3. 添加新的4个复选项任务
        print("\n3. 添加4个复选项任务...")
        
        tasks = [
            {
                "序号": 1,
                "名称": "已通知家属或单位",
                "说明": "已通知教师家属或所在单位",
                "字段": "选项1_已通知家属"
            },
            {
                "序号": 2,
                "名称": "已收到补贴申请审批表",
                "说明": "已收到《枣阳市80周岁以上高龄老人补贴申请审批表》",
                "字段": "选项2_已收到申请表"
            },
            {
                "序号": 3,
                "名称": "已上报民政办或教育局",
                "说明": "已将申请材料上报至民政部门或教育局",
                "字段": "选项3_已上报"
            },
            {
                "序号": 4,
                "名称": "已批准",
                "说明": "高龄补贴申请已获批准",
                "字段": "选项4_已批准"
            }
        ]
        
        for task in tasks:
            cursor.execute("""
                INSERT INTO business_checklist_items 
                (模板ID, 任务序号, 任务编码, 任务名称, 任务说明, 是否必填, 
                 办理时限天数, 时限计算方式, 提醒方式, 排序, 关联数据字段)
                VALUES (%s, %s, %s, %s, %s, TRUE, 30, '清单创建后', '截止前', %s, %s)
            """, (
                template_id,
                task["序号"],
                f"OCTOGENARIAN_001_TASK{task['序号']:03d}",
                task["名称"],
                task["说明"],
                task["序号"] - 1,
                json.dumps({
                    "对应字段": task["字段"],
                    "任务类型": "复选项",
                    "进度占比": "25%"
                })
            ))
            print(f"   ✓ 添加任务 {task['序号']}: {task['名称']}")
        
        # 4. 更新模板名称和描述
        print("\n4. 更新模板信息...")
        cursor.execute("""
            UPDATE business_checklist_templates
            SET 模板名称 = '80周岁高龄补贴业务清单',
                模板描述 = '教师满80周岁时办理高龄补贴相关手续（4个复选项）',
                触发条件配置 = %s,
                更新时间 = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            json.dumps([{
                "条件类型": "age",
                "条件字段": "birth_date",
                "操作符": ">=",
                "条件值": "80",
                "条件名称": "年龄满80周岁"
            }]),
            template_id
        ))
        print(f"   ✓ 模板信息已更新")
        
        conn.commit()
        print("\n✅ 80岁高龄补贴业务清单更新完成！")
        print(f"\n更新摘要:")
        print(f"  - 模板 ID: {template_id}")
        print(f"  - 任务项数量: 4个复选项")
        print(f"  - 任务列表:")
        for task in tasks:
            print(f"    {task['序号']}. {task['名称']}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update()
