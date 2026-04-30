#!/usr/bin/env python3
"""
迁移脚本：为高龄提醒处理记录表添加选项4_已批准字段
"""

import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def migrate_add_option4():
    """添加选项4_已批准字段到高龄提醒处理记录表"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '高龄提醒处理记录'
            AND column_name = '选项4_已批准'
        """)

        if cursor.fetchone():
            print("字段 '选项4_已批准' 已存在，跳过迁移")
        else:
            # 添加新字段
            cursor.execute("""
                ALTER TABLE 高龄提醒处理记录
                ADD COLUMN 选项4_已批准 BOOLEAN DEFAULT FALSE
            """)
            conn.commit()
            print("成功添加字段 '选项4_已批准'")

        cursor.close()
        conn.close()
        print("迁移完成！")
        return True

    except Exception as e:
        print(f"迁移失败: {e}")
        return False


if __name__ == "__main__":
    migrate_add_option4()
