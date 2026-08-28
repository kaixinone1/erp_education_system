"""
按单位独立备份和恢复服务

功能：
- 按单位备份：每个单位生成独立 SQL 备份文件
- 按单位恢复：只恢复指定单位的数据，不影响其他单位
- 恢复前自动创建安全备份
- 操作日志记录

备份目录结构：
  备份/按单位备份/
    ├── 枣阳市太平镇第一初级中学/
    │   ├── 20260828_101750.sql
    │   └── 20260827_010000.sql
    ├── 枣阳市太平镇第二初级中学/
    │   └── ...
    └── 共享字典表/
        └── 20260828_101750.sql
"""
import os
import json
import logging
import shutil
from datetime import datetime, date as date_type
from pathlib import Path

logger = logging.getLogger(__name__)

# 数据库连接参数
DB_CONFIG = {
    "dbname": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password",
    "host": "localhost",
    "port": "5432",
}

# 备份根目录
BASE_BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "备份", "按单位备份"
)

# 操作日志文件
OPERATION_LOG_FILE = os.path.join(BASE_BACKUP_DIR, "operation_log.json")


def _get_conn():
    """获取数据库连接"""
    import psycopg2
    return psycopg2.connect(**DB_CONFIG)


def _get_id_card_columns(cur):
    """动态发现所有表中含身份证的列名及其表名"""
    cur.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
          AND (column_name LIKE '%%id_card%%' OR column_name LIKE '%%身份证%%')
          AND table_name NOT LIKE 'pg_%%' 
          AND table_name NOT LIKE 'sql_%%'
        ORDER BY table_name
    """)
    return {row[0]: row[1] for row in cur.fetchall()}


def get_units():
    """获取所有单位列表"""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT d.unit, COUNT(t.id) as teacher_count
            FROM dict_unit_dictionary d
            LEFT JOIN teacher_unit t ON CAST(t.unit_1 AS INTEGER) = d.id
            GROUP BY d.id, d.unit
            ORDER BY d.id
        """)
        units = []
        for row in cur.fetchall():
            units.append({
                "name": row[0],
                "teacher_count": row[1],
            })
        return units
    finally:
        conn.close()


def get_unit_id_cards(unit_name):
    """获取指定单位的所有教师身份证号"""
    conn = _get_conn()
    try:
        cur = conn.cursor()
        # 先获取单位ID
        cur.execute(
            "SELECT id FROM dict_unit_dictionary WHERE unit = %s",
            (unit_name,)
        )
        unit_row = cur.fetchone()
        if not unit_row:
            return None, []
        unit_id = unit_row[0]

        # 获取该单位所有教师的身份证号
        cur.execute(
            "SELECT id_card FROM teacher_unit WHERE unit_1 = %s",
            (str(unit_id),)
        )
        id_cards = [row[0] for row in cur.fetchall()]
        return unit_id, id_cards
    finally:
        conn.close()


def backup_unit(unit_name):
    """
    备份指定单位的所有数据

    返回: {
        "success": bool,
        "unit_name": str,
        "filename": str,
        "teacher_count": int,
        "table_count": int,
        "file_size": int,
        "error": str or None,
    }
    """
    import time as time_module
    start_time = time_module.time()

    result = {
        "success": False,
        "unit_name": unit_name,
        "filename": None,
        "teacher_count": 0,
        "table_count": 0,
        "file_size": 0,
        "error": None,
    }

    try:
        unit_id, id_cards = get_unit_id_cards(unit_name)
        if unit_id is None:
            result["error"] = f"单位不存在: {unit_name}"
            return result

        if not id_cards:
            result["error"] = f"单位 '{unit_name}' 没有教师数据"
            result["success"] = True
            return result

        result["teacher_count"] = len(id_cards)

        # 创建备份目录
        unit_dir = os.path.join(BASE_BACKUP_DIR, unit_name)
        os.makedirs(unit_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.sql"
        filepath = os.path.join(unit_dir, filename)

        conn = _get_conn()
        try:
            cur = conn.cursor()

            # 动态获取所有含身份证列的表
            id_card_tables = _get_id_card_columns(cur)

            table_count = 0
            with open(filepath, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- 按单位备份: {unit_name}\n")
                f.write(f"-- 备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 教师数量: {len(id_cards)}\n")
                f.write(f"-- 单位ID: {unit_id}\n\n")
                f.write("BEGIN;\n\n")

                # 备份每个表的数据
                for table_name, id_col in sorted(id_card_tables.items()):
                    try:
                        # 获取表的所有列名
                        cur.execute("""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_schema = 'public' AND table_name = %s
                            ORDER BY ordinal_position
                        """, (table_name,))
                        columns = [row[0] for row in cur.fetchall()]
                        if not columns:
                            continue

                        # 查询该单位的数据
                        placeholders = ','.join(['%s'] * len(id_cards))
                        quoted_col = f'"{id_col}"'
                        query = f'SELECT * FROM "{table_name}" WHERE {quoted_col} IN ({placeholders})'
                        cur.execute(query, id_cards)
                        rows = cur.fetchall()

                        if not rows:
                            continue

                        # 写入 DELETE 语句（恢复时先清理旧数据）
                        quoted_cols = ', '.join([f'"{c}"' for c in columns])
                        # 构建实际引用值字符串（替换 %s 占位符为实际值）
                        quoted_values = ', '.join([f"'{card}'" for card in id_cards])
                        f.write(f"-- 表: {table_name} ({len(rows)} 行)\n")
                        f.write(f"DELETE FROM \"{table_name}\" WHERE {quoted_col} IN ({quoted_values});\n\n")

                        # 写入 INSERT 语句
                        for row in rows:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, str):
                                    escaped = val.replace("'", "''")
                                    values.append(f"'{escaped}'")
                                elif isinstance(val, datetime):
                                    values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                                elif isinstance(val, date_type):
                                    values.append(f"'{val.strftime('%Y-%m-%d')}'")
                                elif isinstance(val, bool):
                                    values.append("TRUE" if val else "FALSE")
                                else:
                                    values.append(str(val))
                            f.write(f"INSERT INTO \"{table_name}\" ({quoted_cols}) VALUES ({', '.join(values)});\n")

                        f.write("\n")
                        table_count += 1

                    except Exception as e:
                        logger.warning(f"备份表 {table_name} 失败: {e}")
                        f.write(f"-- 备份表 {table_name} 失败: {e}\n\n")

                # 备份 teacher_unit 表（不仅要按 id_card，还要确认 unit_1）
                f.write("-- 表: teacher_unit (单位直接关联)\n")
                f.write(f"DELETE FROM teacher_unit WHERE unit_1 = '{unit_id}';\n\n")
                cur.execute(
                    "SELECT * FROM teacher_unit WHERE unit_1 = %s",
                    (str(unit_id),)
                )
                tu_rows = cur.fetchall()
                cur.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = 'teacher_unit'
                    ORDER BY ordinal_position
                """)
                tu_columns = [row[0] for row in cur.fetchall()]
                tu_quoted_cols = ', '.join([f'"{c}"' for c in tu_columns])
                for row in tu_rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, str):
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, datetime):
                            values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                        elif isinstance(val, date_type):
                            values.append(f"'{val.strftime('%Y-%m-%d')}'")
                        elif isinstance(val, bool):
                            values.append("TRUE" if val else "FALSE")
                        else:
                            values.append(str(val))
                    f.write(f"INSERT INTO teacher_unit ({tu_quoted_cols}) VALUES ({', '.join(values)});\n")
                f.write("\n")

                f.write("COMMIT;\n")

            result["table_count"] = table_count
            result["file_size"] = os.path.getsize(filepath)
            result["filename"] = filename
            result["success"] = True

        finally:
            conn.close()

        elapsed = time_module.time() - start_time
        logger.info(f"按单位备份完成: {unit_name} ({len(id_cards)}人, {table_count}表, "
                    f"{result['file_size']}字节, {elapsed:.1f}秒)")

        _log_operation("backup", unit_name, result)

    except Exception as e:
        logger.error(f"按单位备份失败 [{unit_name}]: {e}")
        result["error"] = str(e)
        _log_operation("backup", unit_name, result)

    return result


def backup_all_units():
    """
    备份所有单位

    返回: {"success": bool, "results": [...], "total_units": int, "success_count": int, "failed_count": int}
    """
    units = get_units()
    results = []
    success_count = 0
    failed_count = 0

    for unit in units:
        unit_name = unit["name"]
        if unit["teacher_count"] == 0:
            continue
        logger.info(f"开始备份单位: {unit_name} ({unit['teacher_count']}人)")
        result = backup_unit(unit_name)
        results.append(result)
        if result["success"]:
            success_count += 1
        else:
            failed_count += 1

    return {
        "success": failed_count == 0,
        "results": results,
        "total_units": len(units),
        "success_count": success_count,
        "failed_count": failed_count,
    }


def restore_unit(unit_name, backup_filename):
    """
    恢复指定单位的数据

    流程：
    1. 先备份当前数据（安全兜底）
    2. 从备份文件恢复数据

    返回: {
        "success": bool,
        "unit_name": str,
        "backup_filename": str,
        "safety_backup": str or None,
        "error": str or None,
    }
    """
    result = {
        "success": False,
        "unit_name": unit_name,
        "backup_filename": backup_filename,
        "safety_backup": None,
        "error": None,
    }

    try:
        backup_filepath = os.path.join(BASE_BACKUP_DIR, unit_name, backup_filename)
        if not os.path.exists(backup_filepath):
            result["error"] = f"备份文件不存在: {backup_filename}"
            return result

        # 第1步：安全备份当前数据
        logger.info(f"恢复前安全备份: {unit_name}")
        safety_result = backup_unit(unit_name)
        if safety_result["success"] and safety_result["filename"]:
            result["safety_backup"] = safety_result["filename"]
            logger.info(f"安全备份完成: {safety_result['filename']}")

        # 第2步：执行恢复
        conn = _get_conn()
        try:
            cur = conn.cursor()

            with open(backup_filepath, 'r', encoding='utf-8') as f:
                sql = f.read()

            cur.execute(sql)
            conn.commit()
            logger.info(f"恢复成功: {unit_name} <- {backup_filename}")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        result["success"] = True
        _log_operation("restore", unit_name, result)

    except Exception as e:
        logger.error(f"恢复失败 [{unit_name}]: {e}")
        result["error"] = str(e)
        _log_operation("restore", unit_name, result)

    return result


def get_unit_backup_history(unit_name):
    """获取指定单位的备份历史"""
    unit_dir = os.path.join(BASE_BACKUP_DIR, unit_name)
    if not os.path.exists(unit_dir):
        return []

    backups = []
    for f in sorted(os.listdir(unit_dir), reverse=True):
        if f.endswith('.sql'):
            filepath = os.path.join(unit_dir, f)
            stat = os.stat(filepath)
            backups.append({
                "filename": f,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })

    return backups


def _log_operation(op_type, unit_name, result):
    """记录操作日志"""
    os.makedirs(BASE_BACKUP_DIR, exist_ok=True)

    logs = []
    if os.path.exists(OPERATION_LOG_FILE):
        try:
            with open(OPERATION_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": op_type,
        "unit": unit_name,
        "success": result.get("success", False),
        "filename": result.get("filename", result.get("backup_filename", "")),
        "error": result.get("error", ""),
    }

    # 如果是恢复操作，记录安全备份
    if result.get("safety_backup"):
        log_entry["safety_backup"] = result["safety_backup"]

    logs.append(log_entry)

    # 只保留最近 1000 条日志
    if len(logs) > 1000:
        logs = logs[-1000:]

    with open(OPERATION_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_operation_logs(limit=50):
    """获取最近的操作日志"""
    if not os.path.exists(OPERATION_LOG_FILE):
        return []

    try:
        with open(OPERATION_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        return logs[-limit:][::-1]  # 最新的在前
    except:
        return []