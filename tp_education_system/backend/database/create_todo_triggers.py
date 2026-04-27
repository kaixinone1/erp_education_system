#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建数据库触发器，监听教师信息表的变化
当数据变化时，自动记录到 pending_triggers 表
"""

import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_triggers():
    """创建数据库触发器"""
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
        print("开始创建数据库触发器")
        print("=" * 60)

        # 创建触发器函数
        print("\n[1] 创建触发器函数...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION check_todo_trigger()
            RETURNS TRIGGER AS $$
            DECLARE
                v_condition RECORD;
                v_teacher_name VARCHAR(100);
                v_template_name VARCHAR(200);
                v_trigger_reason TEXT;
            BEGIN
                -- 获取教师姓名
                SELECT name INTO v_teacher_name
                FROM teacher_basic_info
                WHERE id = NEW.id;

                -- 遍历所有启用的触发条件
                FOR v_condition IN
                    SELECT * FROM trigger_conditions
                    WHERE is_enabled = TRUE
                      AND listen_table = 'teacher_basic_info'
                LOOP
                    -- 检查是否是监听的字段发生变化
                    IF v_condition.listen_field = 'employment_status' THEN
                        -- 检查触发条件
                        IF v_condition.trigger_type = 'equal' AND NEW.employment_status = v_condition.trigger_value THEN
                            -- 检查是否是从其他值变化而来（避免重复触发）
                            IF OLD.employment_status IS NULL OR OLD.employment_status != NEW.employment_status THEN
                                -- 获取模板名称
                                SELECT template_name INTO v_template_name
                                FROM todo_templates
                                WHERE template_code = v_condition.template_code;

                                -- 构建触发原因
                                v_trigger_reason := '教师 ' || COALESCE(v_teacher_name, '未知') || 
                                    ' 的任职状态从 "' || COALESCE(OLD.employment_status, '空') || 
                                    '" 变为 "' || COALESCE(NEW.employment_status, '空') || '"';

                                -- 插入待确认触发记录
                                INSERT INTO pending_triggers (
                                    trigger_reason,
                                    listen_table,
                                    listen_field,
                                    old_value,
                                    new_value,
                                    teacher_id,
                                    teacher_name,
                                    template_code,
                                    template_name,
                                    status
                                ) VALUES (
                                    v_trigger_reason,
                                    'teacher_basic_info',
                                    'employment_status',
                                    OLD.employment_status,
                                    NEW.employment_status,
                                    NEW.id,
                                    v_teacher_name,
                                    v_condition.template_code,
                                    v_template_name,
                                    'pending'
                                );
                            END IF;
                        END IF;
                    END IF;
                END LOOP;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("  [OK] 触发器函数创建成功")

        # 删除已存在的触发器
        cursor.execute("""
            DROP TRIGGER IF EXISTS todo_trigger_on_teacher_update
            ON teacher_basic_info;
        """)
        print("  [OK] 旧触发器已删除")

        # 创建触发器
        print("\n[2] 创建触发器...")
        cursor.execute("""
            CREATE TRIGGER todo_trigger_on_teacher_update
            AFTER UPDATE ON teacher_basic_info
            FOR EACH ROW
            EXECUTE FUNCTION check_todo_trigger();
        """)
        print("  [OK] 触发器创建成功")

        conn.commit()
        print("\n" + "=" * 60)
        print("数据库触发器创建成功！")
        print("=" * 60)
        print("\n现在，当教师任职状态变化时，系统会自动：")
        print("  1. 检测变化是否符合触发条件")
        print("  2. 将触发记录写入 pending_triggers 表")
        print("  3. 等待用户确认后生成正式待办")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] 创建触发器失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_triggers()
