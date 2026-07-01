"""
仪表盘数据API - 从数据库真实数据生成首页统计
"""
from fastapi import APIRouter
import psycopg2
from datetime import date

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )


@router.get("/stats")
async def get_dashboard_stats():
    """获取仪表盘统计数据（全部来自数据库真实数据）"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        today = date.today()

        # 1. 教师总数
        cursor.execute("SELECT COUNT(*) FROM teacher_basic_info")
        total_teachers = cursor.fetchone()[0]

        # 2. 待办工作数
        cursor.execute("SELECT COUNT(*) FROM todo_items WHERE status = 'pending'")
        pending_todos = cursor.fetchone()[0]

        # 3. 绩效工资勾选人数（标签关系管理中绩效工资标签关联的教师数）
        cursor.execute("""
            SELECT COUNT(DISTINCT employee_id) FROM employee_tag_relations
            WHERE tag_id = (SELECT id FROM personal_dict_dictionary WHERE biao_qian = %s)
        """, ("绩效工资",))
        performance_salary_count = cursor.fetchone()[0]

        # 4. 退休人数
        cursor.execute(
            "SELECT COUNT(*) FROM teacher_basic_info WHERE employment_status = %s", ("退休",)
        )
        retired_teachers = cursor.fetchone()[0]

        # 5. 单位/部门数
        cursor.execute("SELECT COUNT(DISTINCT unit_1) FROM teacher_unit WHERE unit_1 IS NOT NULL")
        unit_count = cursor.fetchone()[0]

        # 6. 去世人数
        cursor.execute(
            "SELECT COUNT(*) FROM teacher_basic_info WHERE employment_status = %s", ("去世",)
        )
        deceased_teachers = cursor.fetchone()[0]

        # 7. 性别分布
        cursor.execute("""
            SELECT
                CASE WHEN CAST(SUBSTRING(id_card, 17, 1) AS INTEGER) % 2 = 0
                     THEN '女' ELSE '男' END AS gender,
                COUNT(*) AS cnt
            FROM teacher_basic_info
            WHERE id_card IS NOT NULL AND LENGTH(id_card) = 18
            GROUP BY (CASE WHEN CAST(SUBSTRING(id_card, 17, 1) AS INTEGER) % 2 = 0
                           THEN '女' ELSE '男' END)
        """)
        gender_data = [{"name": row[0], "value": row[1]} for row in cursor.fetchall()]

        # 8. 现受聘岗位等级分布（来自岗位聘任信息表 post_level_1 JOIN 岗位等级字典）
        cursor.execute("""
            SELECT g.post_level, COUNT(*) AS cnt
            FROM post_appointment_info p
            JOIN dict_grade_dictionary g ON p.post_level_1 = g.id::text
            WHERE p.post_level_1 IS NOT NULL
            GROUP BY g.post_level
            ORDER BY cnt DESC
        """)
        post_level_data = [{"name": row[0], "value": row[1]} for row in cursor.fetchall()]

        # 8-2. 现受聘岗位名称分布（来自岗位聘任信息表 post_1 JOIN 岗位名称字典）
        cursor.execute("""
            SELECT d.post, COUNT(*) AS cnt
            FROM post_appointment_info p
            JOIN dict_dictionary_personal d ON p.post_1 = d.id::text
            WHERE p.post_1 IS NOT NULL
            GROUP BY d.post
            ORDER BY cnt DESC
        """)
        post_name_data = [{"name": row[0], "value": row[1]} for row in cursor.fetchall()]

        # 9. 学历分布（每人最高学历，来自教师学历记录）
        cursor.execute("""
            SELECT edu_name, COUNT(*) AS cnt
            FROM (
                SELECT id_card,
                       (SELECT d2.education FROM dict_education_level_dictionary d2 
                        WHERE d2.id::text = MAX(t.education::int)::text) AS edu_name
                FROM teacher_education_record t
                WHERE t.id_card IS NOT NULL AND t.id_card != ''
                GROUP BY t.id_card
            ) sub
            WHERE edu_name IS NOT NULL
            GROUP BY edu_name
            ORDER BY cnt DESC
        """)
        education_data = [{"name": row[0], "value": row[1]} for row in cursor.fetchall()]

        # 10. 任职状态分布
        cursor.execute("""
            SELECT employment_status, COUNT(*) AS cnt
            FROM teacher_basic_info
            WHERE employment_status IS NOT NULL
            GROUP BY employment_status
            ORDER BY cnt DESC
        """)
        status_data = [{"name": row[0] if row[0] else "未知", "value": row[1]} for row in cursor.fetchall()]

        # 11. 离休人数
        cursor.execute(
            "SELECT COUNT(*) FROM teacher_basic_info WHERE employment_status = %s", ("离休",)
        )
        retired_old_style = cursor.fetchone()[0]

        return {
            "统计卡片": {
                "教师总数": total_teachers,
                "待办工作": pending_todos,
                "绩效工资人数": performance_salary_count,
                "退休人数": retired_teachers,
                "单位数量": unit_count,
                "离休人数": retired_old_style,
            },
            "图表数据": {
                "性别分布": gender_data,
                "现受聘岗位等级分布": post_level_data,
                "现受聘岗位名称分布": post_name_data,
                "学历分布": education_data,
                "任职状态分布": status_data,
            }
        }

    finally:
        cursor.close()
        conn.close()