"""
绩效工资标准管理路由 - 从 dict_salary_dictionary 和 dict_subsidy_dictionary 读取数据
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education_fifteen",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


router = APIRouter(prefix="/api/performance-pay/standards", tags=["绩效工资标准"])


class PerformanceStandard(BaseModel):
    """绩效工资标准"""
    level_name: str
    level_code: Optional[str] = ""
    performance_pay: float
    effective_date: Optional[str] = ""
    remarks: Optional[str] = ""


class TownSubsidyStandard(BaseModel):
    """乡镇补贴标准"""
    town_name: str
    subsidy_amount: float
    effective_date: Optional[str] = ""
    remarks: Optional[str] = ""


# ==================== 绩效工资标准 ====================

@router.get("/performance")
def get_performance_standards():
    """获取绩效工资标准列表（从 dict_salary_dictionary 读取）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, post_1, month_performance_salary, created_at, updated_at
            FROM dict_salary_dictionary
            ORDER BY id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = []
        for row in rows:
            try:
                pay = float(row[2]) if row[2] else 0
            except (ValueError, TypeError):
                pay = 0

            data.append({
                "id": row[0],
                "level_name": row[1] or "",
                "level_code": "",
                "performance_pay": pay,
                "effective_date": str(row[3])[:10] if row[3] else "",
                "remarks": ""
            })

        return {"status": "success", "data": data}
    except Exception as e:
        print(f"获取绩效工资标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/performance")
def add_performance_standard(data: PerformanceStandard):
    """新增绩效工资标准（写入 dict_salary_dictionary）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dict_salary_dictionary (post_1, month_performance_salary)
            VALUES (%s, %s)
            RETURNING id
        """, (data.level_name, str(data.performance_pay)))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "添加成功", "id": new_id}
    except Exception as e:
        print(f"新增绩效工资标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/performance/{standard_id}")
def update_performance_standard(standard_id: int, data: PerformanceStandard):
    """更新绩效工资标准"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE dict_salary_dictionary
            SET post_1 = %s, month_performance_salary = %s, updated_at = NOW()
            WHERE id = %s
        """, (data.level_name, str(data.performance_pay), standard_id))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "更新成功"}
    except Exception as e:
        print(f"更新绩效工资标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/performance/{standard_id}")
def delete_performance_standard(standard_id: int):
    """删除绩效工资标准"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM dict_salary_dictionary WHERE id = %s", (standard_id,))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "删除成功"}
    except Exception as e:
        print(f"删除绩效工资标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 乡镇补贴标准 ====================

@router.get("/town")
def get_town_subsidy_standards():
    """获取乡镇补贴标准列表（从 dict_subsidy_dictionary 读取）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, subsidy_1, created_at, updated_at
            FROM dict_subsidy_dictionary
            ORDER BY id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = []
        for row in rows:
            try:
                amount = float(row[1]) if row[1] else 0
            except (ValueError, TypeError):
                amount = 0

            data.append({
                "id": row[0],
                "town_name": "乡镇补贴",
                "subsidy_amount": amount,
                "effective_date": str(row[2])[:10] if row[2] else "",
                "remarks": ""
            })

        return {"status": "success", "data": data}
    except Exception as e:
        print(f"获取乡镇补贴标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/town")
def add_town_subsidy_standard(data: TownSubsidyStandard):
    """新增乡镇补贴标准（写入 dict_subsidy_dictionary）"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dict_subsidy_dictionary (subsidy_1)
            VALUES (%s)
            RETURNING id
        """, (str(data.subsidy_amount),))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "添加成功", "id": new_id}
    except Exception as e:
        print(f"新增乡镇补贴标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/town/{standard_id}")
def update_town_subsidy_standard(standard_id: int, data: TownSubsidyStandard):
    """更新乡镇补贴标准"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE dict_subsidy_dictionary
            SET subsidy_1 = %s, updated_at = NOW()
            WHERE id = %s
        """, (str(data.subsidy_amount), standard_id))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "更新成功"}
    except Exception as e:
        print(f"更新乡镇补贴标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/town/{standard_id}")
def delete_town_subsidy_standard(standard_id: int):
    """删除乡镇补贴标准"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM dict_subsidy_dictionary WHERE id = %s", (standard_id,))
        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "删除成功"}
    except Exception as e:
        print(f"删除乡镇补贴标准失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))