"""
历史快照管理 API
功能：手动创建数据快照、查询快照列表、查看快照详情（时光倒流）
"""
import json
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
import psycopg2.extras

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education_fifteen",
    "user": "taiping_user",
    "password": "taiping_password"
}

router = APIRouter(prefix="/api/snapshots", tags=["历史快照"])

# 不参与快照的系统表
EXCLUDED_TABLES = [
    "data_history_snapshots",
    "system_users",
    "unit_hierarchy",
    "navigation_config",
    "table_schemas",
    "alembic_version",
    "spatial_ref_sys",
]


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


class CreateSnapshotRequest(BaseModel):
    table_name: Optional[str] = None
    snapshot_type: str = "manual"


def get_business_tables():
    """获取所有业务表（排除系统表）"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    all_tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return [t for t in all_tables if t not in EXCLUDED_TABLES]


def create_snapshot_for_table(conn, table_name: str, snapshot_type: str):
    """为单个表创建快照"""
    cur = conn.cursor()

    # 获取表的所有数据
    cur.execute(f'SELECT * FROM "{table_name}"')
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    if not rows:
        cur.close()
        return 0

    today = date.today()
    count = 0

    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            val = row[i]
            if isinstance(val, (datetime, date)):
                val = val.isoformat()
            elif isinstance(val, bytes):
                val = None  # 二进制数据跳过
            row_dict[col] = val

        cur.execute("""
            INSERT INTO data_history_snapshots
                (table_name, record_id, snapshot_data, snapshot_type, snapshot_date, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (table_name, row_dict.get('id', 0),
              json.dumps(row_dict, ensure_ascii=False), snapshot_type, today))
        count += 1

    conn.commit()
    cur.close()
    return count


# ==================== API 端点 ====================

@router.post("/create")
def create_snapshots(request: CreateSnapshotRequest):
    """手动创建数据快照"""
    try:
        conn = get_db_connection()
        total = 0
        tables_done = []

        if request.table_name:
            count = create_snapshot_for_table(conn, request.table_name, request.snapshot_type)
            tables_done.append({"表名": request.table_name, "记录数": count})
            total += count
        else:
            tables = get_business_tables()
            for table_name in tables:
                try:
                    count = create_snapshot_for_table(conn, table_name, request.snapshot_type)
                    if count > 0:
                        tables_done.append({"表名": table_name, "记录数": count})
                        total += count
                except Exception as e:
                    print(f"表 {table_name} 快照失败: {e}")

        conn.close()

        return {
            "status": "success",
            "message": f"快照创建完成，共 {total} 条记录",
            "快照类型": request.snapshot_type,
            "快照日期": str(date.today()),
            "涉及表数": len(tables_done),
            "总记录数": total,
            "详情": tables_done[:20]
        }
    except Exception as e:
        print(f"创建快照失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_snapshots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    table_name: Optional[str] = None,
    snapshot_type: Optional[str] = None
):
    """查询快照列表（按日期分组）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        conditions = []
        params = []
        if table_name:
            conditions.append("table_name = %s")
            params.append(table_name)
        if snapshot_type:
            conditions.append("snapshot_type = %s")
            params.append(snapshot_type)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cur.execute(f"""
            SELECT
                snapshot_date::text,
                snapshot_type,
                COUNT(DISTINCT table_name) as table_count,
                COUNT(*) as record_count,
                MIN(created_at)::text as first_created,
                MAX(created_at)::text as last_created
            FROM data_history_snapshots
            WHERE {where_clause}
            GROUP BY snapshot_date, snapshot_type
            ORDER BY snapshot_date DESC, snapshot_type
            LIMIT %s OFFSET %s
        """, params + [page_size, (page - 1) * page_size])

        rows = cur.fetchall()

        data = []
        for row in rows:
            data.append({
                "快照日期": row[0],
                "快照类型": row[1],
                "涉及表数": row[2],
                "总记录数": row[3],
                "首次创建": row[4],
                "最后创建": row[5]
            })

        cur.close()
        conn.close()

        return {
            "status": "success",
            "data": data,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        print(f"查询快照列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{snapshot_date}")
def get_snapshot_detail(
    snapshot_date: str,
    table_name: Optional[str] = None
):
    """查看指定日期的快照详情（时光倒流）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if table_name:
            cur.execute("""
                SELECT id, table_name, record_id, snapshot_data, snapshot_type,
                       snapshot_date::text, created_at::text, created_by
                FROM data_history_snapshots
                WHERE snapshot_date = %s AND table_name = %s
                ORDER BY table_name, record_id
            """, (snapshot_date, table_name))
        else:
            cur.execute("""
                SELECT id, table_name, record_id, snapshot_data, snapshot_type,
                       snapshot_date::text, created_at::text, created_by
                FROM data_history_snapshots
                WHERE snapshot_date = %s
                ORDER BY table_name, record_id
            """, (snapshot_date,))

        rows = cur.fetchall()

        data = []
        for row in rows:
            snapshot_data = row[3]
            if isinstance(snapshot_data, str):
                snapshot_data = json.loads(snapshot_data)

            data.append({
                "id": row[0],
                "表名": row[1],
                "记录ID": row[2],
                "快照数据": snapshot_data,
                "快照类型": row[4],
                "快照日期": row[5],
                "创建时间": row[6],
                "创建人": row[7]
            })

        cur.close()
        conn.close()

        return {"status": "success", "data": data, "total": len(data)}
    except Exception as e:
        print(f"查询快照详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables")
def get_snapshot_tables():
    """获取所有可快照的业务表列表"""
    try:
        tables = get_business_tables()
        return {"status": "success", "data": tables, "total": len(tables)}
    except Exception as e:
        print(f"获取表列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{snapshot_date}")
def delete_snapshot(snapshot_date: str, table_name: Optional[str] = None):
    """删除指定日期的快照"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if table_name:
            cur.execute(
                "DELETE FROM data_history_snapshots WHERE snapshot_date = %s AND table_name = %s",
                (snapshot_date, table_name)
            )
        else:
            cur.execute(
                "DELETE FROM data_history_snapshots WHERE snapshot_date = %s",
                (snapshot_date,)
            )

        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": f"已删除 {deleted} 条快照记录"}
    except Exception as e:
        print(f"删除快照失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))