"""
中间表管理路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import psycopg2
from datetime import datetime
import json

router = APIRouter(prefix="/api/intermediate-table", tags=["中间表管理"])

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


@router.get("/list")
async def get_intermediate_tables():
    """获取中间表列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, table_name, table_name_cn, description, fields, is_active, created_at, updated_at
            FROM intermediate_tables
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        result = []

        for row in rows:
            fields = row[4] if isinstance(row[4], list) else json.loads(row[4]) if row[4] else []
            result.append({
                "id": row[0],
                "table_name": row[1],
                "table_name_cn": row[2],
                "description": row[3],
                "fields": fields,
                "is_active": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None
            })

        cursor.close()
        conn.close()

        return {"status": "success", "data": result}
    except Exception as e:
        print(f"获取中间表列表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-fields")
async def get_all_fields():
    """获取所有系统字段（用于下拉选择）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        all_fields = []

        # 1. 获取中间表列表（需要排除）
        cursor.execute("SELECT table_name FROM intermediate_tables")
        intermediate_tables = set(row[0] for row in cursor.fetchall())

        # 2. 获取模板表列表（需要排除）
        cursor.execute("""
            SELECT DISTINCT intermediate_table 
            FROM document_templates 
            WHERE intermediate_table IS NOT NULL AND intermediate_table != ''
        """)
        template_tables = set(row[0] for row in cursor.fetchall())

        # 3. 查询所有原始数据表（排除中间表、模板表、系统表）
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE 'sql_%'
            AND table_name NOT LIKE 'intermediate_tables'
            AND table_name NOT LIKE 'document_templates'
            AND table_name NOT LIKE 'template_%'
            AND table_name NOT LIKE 'dict_%'
            ORDER BY table_name
        """)

        # 过滤掉中间表和模板表
        data_tables = [
            row[0] for row in cursor.fetchall()
            if row[0] not in intermediate_tables 
            and row[0] not in template_tables
        ]

        # 4. 添加字典表（dict_*）
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name LIKE 'dict_%'
            ORDER BY table_name
        """)
        dict_tables = [row[0] for row in cursor.fetchall()]

        # 合并数据表和字典表
        all_tables = data_tables + dict_tables

        # 5. 加载表名中文映射（从 intermediate_tables 表和预设映射）
        table_name_cn_map = {
            # 预设的表名映射
            'teacher_basic_info': '教师基础信息',
            'teacher_education_record': '教师学历信息',
            'teacher_training_records': '教师培训记录',
            'retirement_report_form': '退休呈报表',
            'retirement_cert_records': '退休证记录',
            'dict_dictionary': '字典表',
            'dict_education_level_dictionary': '学历字典',
            'dict_education_type_dictionary': '教育类型字典',
            'business_checklist': '业务清单',
            'performance_pay_approval': '绩效工资审批',
            'navigation_modules': '导航模块',
            'todo_work': '待办工作',
        }
        
        # 从 intermediate_tables 表补充映射
        try:
            cursor.execute("""
                SELECT table_name, table_name_cn 
                FROM intermediate_tables
            """)
            for row in cursor.fetchall():
                table_name_cn_map[row[0]] = row[1]
        except:
            pass

        # 6. 收集每个表的字段
        for table in all_tables:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            
            columns = [row[0] for row in cursor.fetchall()]
            
            for col in columns:
                all_fields.append({
                    "value": col,
                    "label": col,
                    "table": table,
                    "table_name_cn": table_name_cn_map.get(table, table)
                })

        cursor.close()
        conn.close()

        return {"status": "success", "data": all_fields}
    except Exception as e:
        print(f"获取所有字段失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_id}")
async def get_intermediate_table(table_id: int):
    """获取单个中间表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, table_name, table_name_cn, description, fields, is_active, created_at, updated_at
            FROM intermediate_tables
            WHERE id = %s
        """, (table_id,))

        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="中间表不存在")

        fields = row[4] if isinstance(row[4], list) else json.loads(row[4]) if row[4] else []

        result = {
            "id": row[0],
            "table_name": row[1],
            "table_name_cn": row[2],
            "description": row[3],
            "fields": fields,
            "is_active": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }

        cursor.close()
        conn.close()

        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取中间表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_intermediate_table(data: dict):
    """创建中间表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        table_name = data.get("table_name")
        table_name_cn = data.get("table_name_cn")
        description = data.get("description", "")
        fields = data.get("fields", [])
        is_active = data.get("is_active", True)

        cursor.execute("""
            INSERT INTO intermediate_tables (table_name, table_name_cn, description, fields, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (table_name, table_name_cn, description, json.dumps(fields), is_active, datetime.now(), datetime.now()))

        new_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "id": new_id, "message": "中间表创建成功"}
    except Exception as e:
        conn.rollback()
        print(f"创建中间表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{table_id}")
async def update_intermediate_table(table_id: int, data: dict):
    """更新中间表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM intermediate_tables WHERE id = %s", (table_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="中间表不存在")

        table_name_cn = data.get("table_name_cn")
        description = data.get("description")
        fields = data.get("fields")
        is_active = data.get("is_active")

        cursor.execute("""
            UPDATE intermediate_tables
            SET table_name_cn = %s, description = %s, fields = %s, is_active = %s, updated_at = %s
            WHERE id = %s
        """, (table_name_cn, description, json.dumps(fields), is_active, datetime.now(), table_id))

        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "中间表更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"更新中间表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{table_id}")
async def delete_intermediate_table(table_id: int):
    """删除中间表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM intermediate_tables WHERE id = %s", (table_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="中间表不存在")

        cursor.execute("DELETE FROM intermediate_tables WHERE id = %s", (table_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "中间表删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"删除中间表失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-name")
async def translate_table_name(data: dict):
    """将中文表名翻译为英文表名"""
    try:
        from utils.name_translator import translate_table_name
        
        name = data.get("name", "")
        if not name:
            return {"status": "error", "message": "名称不能为空"}
        
        english_name = translate_table_name(name)
        return {"status": "success", "data": english_name}
    except Exception as e:
        print(f"翻译表名失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
