
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新待办标题格式为：某某某教师某某某事件名称
"""

import psycopg2

def update_titles():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    try:
        print("=" * 60)
        print("更新待办标题格式")
        print("=" * 60)

        # 孟伟英、张瑜：到龄退休提醒
        print("\n更新到龄退休提醒标题...")
        cursor.execute("""
            UPDATE todo_items
            SET title = '孟伟英教师到龄退休提醒'
            WHERE id = 5
        """)
        print("  [OK] 孟伟英标题已更新")

        cursor.execute("""
            UPDATE todo_items
            SET title = '张瑜教师到龄退休提醒'
            WHERE id = 6
        """)
        print("  [OK] 张瑜标题已更新")

        # 白清学、张运勤：死亡登记
        print("\n更新死亡登记标题...")
        cursor.execute("""
            UPDATE todo_items
            SET title = '白清学教师死亡登记'
            WHERE id = 1
        """)
        print("  [OK] 白清学标题已更新")

        cursor.execute("""
            UPDATE todo_items
            SET title = '张运勤教师死亡登记'
            WHERE id = 3
        """)
        print("  [OK] 张运勤标题已更新")

        # 牛全胜：死亡登记
        cursor.execute("""
            UPDATE todo_items
            SET title = '牛全胜教师死亡登记'
            WHERE id = 2
        """)
        print("  [OK] 牛全胜标题已更新")

        # 高广华：80周岁高龄补贴申请
        print("\n更新80周岁高龄补贴申请标题...")
        cursor.execute("""
            UPDATE todo_items
            SET title = '高广华教师80周岁高龄补贴申请'
            WHERE id = 4
        """)
        print("  [OK] 高广华标题已更新")

        conn.commit()

        # 验证更新结果
        print("\n验证更新结果...")
        cursor.execute("""
            SELECT id, teacher_name, business_type, title
            FROM todo_items
            ORDER BY id
        """)
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]} - {row[2]} - {row[3]}")

        print("\n" + "=" * 60)
        print("待办标题更新完成！")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 更新失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_titles()
