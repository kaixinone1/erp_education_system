"""
党员信息汇总表 - 自动统计与备份路由
从党员信息表聚合数据，生成汇总表，支持按月/按年备份
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import json
import os
import psycopg2
from datetime import datetime

router = APIRouter(prefix="/api/party/statistics", tags=["党员统计"])

# 数据库连接配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'taiping_education',
    'user': 'taiping_user',
    'password': 'taiping_password'
}

# 表名常量
SOURCE_TABLE = "zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao"
SUMMARY_TABLE = "party_member_info_summary"
BACKUP_TABLE_PREFIX = "party_member_info_summary_backup"
SCHOOL_TABLE = "school_information_table"

# 配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
NAVIGATION_FILE = os.path.join(CONFIG_DIR, 'navigation.json')
TABLE_NAME_MAPPINGS_FILE = os.path.join(CONFIG_DIR, 'table_name_mappings.json')
MERGED_SCHEMA_FILE = os.path.join(CONFIG_DIR, 'merged_schema_mappings.json')


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DATABASE_CONFIG)


def get_summary_field_mapping() -> dict:
    """
    获取汇总表的字段映射
    返回：{中文名: 英文字段名}，如 {'党组织名称': 'field_140', '入库党员': 'party_member', ...}
    """
    try:
        with open(MERGED_SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        # 结构: { "tables": { "party_member_info_summary": { "fields": [...] } }, ... }
        table_info = schema.get('tables', {}).get(SUMMARY_TABLE, {})
        fields = table_info.get('fields', [])
        mapping = {}
        for field in fields:
            source = field.get('sourceField', '')
            target = field.get('targetField', '')
            if source and target:
                mapping[source] = target
        return mapping
    except Exception as e:
        print(f"读取字段映射失败: {e}")
        return {}
    

def get_school_core_names() -> list:
    """
    从学校信息表获取所有学校名称，提取核心名称用于匹配支部
    将"枣阳市太平镇第二初级中学" → "第二初级中学"
    将"枣阳市太平镇中心小学" → "中心小学"
    将"枣阳市太平镇寺庄中心小学" → ["寺庄中心小学", "寺庄小学"]（含"中心"时生成变体）
    用于白名单过滤：支部名必须包含任一核心名称才被汇总
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f'SELECT school FROM "{SCHOOL_TABLE}" WHERE school IS NOT NULL')
        schools = [r[0] for r in cur.fetchall()]
        cur.close()

        core_names = []
        common_prefixes = ['枣阳市太平镇', '枣阳市']

        for school in schools:
            core = school
            for prefix in common_prefixes:
                if core.startswith(prefix):
                    core = core[len(prefix):]
                    break
            if core:
                core_names.append(core)
                # 如果核心名称含"中心"且去掉"中心"后仍有意义，生成变体
                # 如"寺庄中心小学" → 同时添加"寺庄小学"
                if '中心' in core:
                    variant = core.replace('中心', '')
                    if variant and variant != core:
                        core_names.append(variant)

        return core_names
    except Exception as e:
        print(f"读取学校信息失败: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_chinese_name(table_name: str) -> str:
    """获取表的中文名"""
    try:
        with open(TABLE_NAME_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        reverse = mappings.get('reverse_mappings', {})
        return reverse.get(table_name, table_name)
    except Exception:
        return table_name


BACKUP_QUERY_PARENT_ID = "party-backup"  # 备份查询子菜单ID
BACKUP_QUERY_TITLE = "备份查询"
MONTHLY_BACKUP_YEARS = 2  # 月度备份保留2年
YEARLY_BACKUP_YEARS = 5   # 年度备份保留5年


def add_table_to_navigation(table_name: str, chinese_title: str, parent_id: str = "party"):
    """动态添加备份表到导航配置（添加到"备份查询"子菜单下）"""
    try:
        with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
            nav = json.load(f)

        def find_and_add(nodes):
            for node in nodes:
                if node.get('id') == parent_id:
                    children = node.get('children', [])

                    # 1. 确保"备份查询"子菜单存在
                    backup_query_node = None
                    for child in children:
                        if child.get('id') == BACKUP_QUERY_PARENT_ID:
                            backup_query_node = child
                            break

                    if not backup_query_node:
                        backup_query_node = {
                            "id": BACKUP_QUERY_PARENT_ID,
                            "title": BACKUP_QUERY_TITLE,
                            "name": BACKUP_QUERY_TITLE,
                            "icon": "FolderOpened",
                            "type": "module",
                            "children": []
                        }
                        children.append(backup_query_node)

                    # 2. 在备份查询下添加备份节点
                    backup_children = backup_query_node.get('children', [])
                    existing_ids = [c.get('id', '') for c in backup_children]
                    new_id = f"table-{table_name}"
                    if new_id not in existing_ids:
                        backup_children.append({
                            "id": new_id,
                            "title": chinese_title,
                            "name": chinese_title,
                            "icon": "Document",
                            "path": f"/data/{table_name}",
                            "type": "component",
                            "component": "DynamicDataView",
                            "api_endpoint": f"/api/data/{table_name}",
                            "table_name": table_name,
                            "table_type": "backup"
                        })
                        backup_query_node['children'] = backup_children

                    node['children'] = children

                    # 3. 清理过期备份节点
                    cleanup_expired_nodes(backup_query_node)

                    return True
                if node.get('children'):
                    if find_and_add(node['children']):
                        return True
            return False

        find_and_add(nav.get('modules', nav if isinstance(nav, list) else []))

        with open(NAVIGATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(nav, f, ensure_ascii=False, indent=2)

        # 同时更新表名映射
        with open(TABLE_NAME_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            tm = json.load(f)
        reverse = tm.get('reverse_mappings', {})
        reverse[table_name] = chinese_title
        tm['reverse_mappings'] = reverse
        with open(TABLE_NAME_MAPPINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tm, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"添加导航节点失败: {e}")
        return False


def remove_table_from_navigation(table_name: str, parent_id: str = "party"):
    """从导航配置的"备份查询"子菜单中移除备份表"""
    try:
        with open(NAVIGATION_FILE, 'r', encoding='utf-8') as f:
            nav = json.load(f)

        def find_and_remove(nodes):
            for node in nodes:
                if node.get('id') == parent_id:
                    children = node.get('children', [])
                    for child in children:
                        if child.get('id') == BACKUP_QUERY_PARENT_ID:
                            backup_children = child.get('children', [])
                            child['children'] = [c for c in backup_children if c.get('table_name') != table_name]
                            return True
                    # 也检查直接子节点（兼容旧数据）
                    node['children'] = [c for c in children if c.get('table_name') != table_name]
                    return True
                if node.get('children'):
                    if find_and_remove(node['children']):
                        return True
            return False

        find_and_remove(nav.get('modules', nav if isinstance(nav, list) else []))

        with open(NAVIGATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(nav, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"移除导航节点失败: {e}")
        return False


def cleanup_expired_nodes(backup_query_node: dict):
    """
    清理过期备份节点（仅从菜单删除，不删除数据库）
    月度备份：保留2年，超过2年自动移除菜单节点
    年度备份：保留5年，超过5年自动移除菜单节点
    """
    from datetime import datetime
    import re

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    children = backup_query_node.get('children', [])
    kept = []

    for child in children:
        title = child.get('title', '')
        removed = False

        # 匹配月度备份："2026年8月备份"
        monthly_match = re.search(r'(\d{4})年(\d{1,2})月备份', title)
        if monthly_match:
            backup_year = int(monthly_match.group(1))
            backup_month = int(monthly_match.group(2))
            # 计算经过的月数
            months_passed = (current_year - backup_year) * 12 + (current_month - backup_month)
            if months_passed >= MONTHLY_BACKUP_YEARS * 12:
                print(f"[备份清理] 月度备份已过期，移除菜单节点: {title}")
                removed = True

        # 匹配年度备份："2026年备份"
        if not removed:
            yearly_match = re.search(r'(\d{4})年备份', title)
            # 确保不是月度备份（月度备份已被上面处理）
            if yearly_match and '月' not in title:
                backup_year = int(yearly_match.group(1))
                if current_year - backup_year >= YEARLY_BACKUP_YEARS:
                    print(f"[备份清理] 年度备份已过期，移除菜单节点: {title}")
                    removed = True

        if not removed:
            kept.append(child)

    if len(kept) < len(children):
        backup_query_node['children'] = kept
        print(f"[备份清理] 清理完成，保留 {len(kept)} 个节点，移除 {len(children) - len(kept)} 个过期节点")

    return backup_query_node


@router.post("/generate")
async def generate_statistics():
    """
    从党员信息表聚合数据，生成汇总表
    1. 根据学校信息表白名单过滤支部（只汇总学校信息表中存在的学校）
    2. 第一行为总支合计，后续为各支部明细
    3. 汇总维度：按所在党支部分组，统计各项分类人数
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. 获取字段映射
        field_map = get_summary_field_mapping()
        if not field_map:
            raise HTTPException(status_code=500, detail="无法读取汇总表字段映射，请确认 merged_schema_mappings.json 配置正确")

        col_name = field_map.get('党组织名称', '党组织名称')
        col_heji = field_map.get('合计', '合计')
        col_ruku = field_map.get('入库党员', '入库党员')
        col_yubei = field_map.get('预备党员', '预备党员')
        col_nv = field_map.get('女党员', '女党员')
        col_shaoshu = field_map.get('少数民族党员', '少数民族党员')
        col_dazhuan = field_map.get('大专及以上学历党员', '大专及以上学历党员')
        col_weiruku = field_map.get('未入库党员', '未入库党员')

        # 2. 获取学校白名单（核心名称列表）
        school_core_names = get_school_core_names()
        print(f"[党员统计] 学校白名单: {school_core_names}")

        # 3. 从信息表聚合统计（只统计正常和组织关系挂靠的党员）
        #    排除：去世(2)、组织关系转出(3)、开除党籍(5)、退党/自行脱党(6)
        cur.execute(f"""
            WITH stats AS (
                SELECT
                    suo_zai_dang_zhi_bu AS 支部,
                    COUNT(*) AS 总人数,
                    COUNT(CASE WHEN shi_fou_ru_ku = '已入库' THEN 1 END) AS 入库人数,
                    COUNT(CASE WHEN personnel_category = '预备党员' THEN 1 END) AS 预备人数,
                    COUNT(CASE WHEN gender = '女' THEN 1 END) AS 女性人数,
                    COUNT(CASE WHEN ethnicity != '汉族' THEN 1 END) AS 少数民族人数,
                    COUNT(CASE WHEN education IN ('大专', '大学', '研究生', '硕士', '博士') THEN 1 END) AS 大专以上人数,
                    COUNT(CASE WHEN shi_fou_ru_ku = '未入库' THEN 1 END) AS 未入库人数
                FROM "{SOURCE_TABLE}"
                WHERE organizational_relationship_status IS NULL
                   OR organizational_relationship_status IN ('1', '正常', '4', '组织关系挂靠')
                GROUP BY suo_zai_dang_zhi_bu
            )
            SELECT "支部", "总人数", "入库人数", "预备人数", "女性人数", "少数民族人数", "大专以上人数", "未入库人数"
            FROM stats ORDER BY "总人数" DESC
        """)

        all_rows = cur.fetchall()

        # 4. 用学校白名单过滤支部
        if school_core_names:
            matched_rows = []
            skipped_branches = []
            for row in all_rows:
                branch_name = row[0] or ''
                matched = any(core in branch_name for core in school_core_names)
                if matched:
                    matched_rows.append(row)
                else:
                    skipped_branches.append(branch_name)

            if skipped_branches:
                print(f"[党员统计] 以下支部不在学校白名单中，已跳过: {skipped_branches}")
        else:
            # 没有学校白名单时，汇总全部（兼容旧数据）
            matched_rows = all_rows
            print("[党员统计] 未获取到学校白名单，汇总全部支部")

        # 5. 重建汇总表（使用中文字段名）
        cur.execute(f'DROP TABLE IF EXISTS "{SUMMARY_TABLE}"')
        cur.execute(f"""
            CREATE TABLE "{SUMMARY_TABLE}" (
                id SERIAL PRIMARY KEY,
                "{col_name}" VARCHAR(255),
                "{col_heji}" VARCHAR(255),
                "{col_ruku}" VARCHAR(255),
                "{col_yubei}" VARCHAR(255),
                "{col_nv}" VARCHAR(255),
                "{col_shaoshu}" VARCHAR(255),
                "{col_dazhuan}" VARCHAR(255),
                "{col_weiruku}" VARCHAR(255)
            )
        """)

        # 6. 计算总支合计
        total = [0, 0, 0, 0, 0, 0, 0]  # 总人数, 入库, 预备, 女, 少数, 大专+, 未入库
        for row in matched_rows:
            for i in range(7):
                val = row[i + 1]  # row[0]是支部名
                total[i] += int(val) if val is not None else 0

        # 7. 插入总支合计行（第一行）
        cur.execute(f"""
            INSERT INTO "{SUMMARY_TABLE}" 
            ("{col_name}", "{col_heji}", "{col_ruku}", "{col_yubei}", "{col_nv}", "{col_shaoshu}", "{col_dazhuan}", "{col_weiruku}")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, ("总支合计", str(total[0]), str(total[1]), str(total[2]), str(total[3]), str(total[4]), str(total[5]), str(total[6])))

        # 8. 插入各支部明细
        for row in matched_rows:
            cur.execute(f"""
                INSERT INTO "{SUMMARY_TABLE}" 
                ("{col_name}", "{col_heji}", "{col_ruku}", "{col_yubei}", "{col_nv}", "{col_shaoshu}", "{col_dazhuan}", "{col_weiruku}")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (row[0], str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7])))

        inserted = len(matched_rows) + 1  # +1 是总支合计行

        conn.commit()
        cur.close()

        return {
            "success": True,
            "message": f"汇总数据生成成功，共 {len(matched_rows)} 个支部 + 1个总支合计",
            "total_branches": len(matched_rows),
            "inserted_rows": inserted,
            "school_whitelist_count": len(school_core_names),
            "skipped_branches": skipped_branches if 'skipped_branches' in dir() else []
        }

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"生成汇总数据失败: {str(e)}")
    finally:
        if conn:
            conn.close()


def do_refresh_party_summary() -> dict:
    """
    从党员信息表聚合数据，生成汇总表（同步版本，可被其他模块调用）
    返回: {"success": bool, "message": str, "inserted_rows": int}
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        field_map = get_summary_field_mapping()
        if not field_map:
            return {"success": False, "message": "无法读取汇总表字段映射"}

        col_name = field_map.get('党组织名称', '党组织名称')
        col_heji = field_map.get('合计', '合计')
        col_ruku = field_map.get('入库党员', '入库党员')
        col_yubei = field_map.get('预备党员', '预备党员')
        col_nv = field_map.get('女党员', '女党员')
        col_shaoshu = field_map.get('少数民族党员', '少数民族党员')
        col_dazhuan = field_map.get('大专及以上学历党员', '大专及以上学历党员')
        col_weiruku = field_map.get('未入库党员', '未入库党员')

        school_core_names = get_school_core_names()
        print(f"[党员统计-自动刷新] 学校白名单: {school_core_names}")

        cur.execute(f"""
            WITH stats AS (
                SELECT
                    suo_zai_dang_zhi_bu AS 支部,
                    COUNT(*) AS 总人数,
                    COUNT(CASE WHEN shi_fou_ru_ku = '已入库' THEN 1 END) AS 入库人数,
                    COUNT(CASE WHEN personnel_category = '预备党员' THEN 1 END) AS 预备人数,
                    COUNT(CASE WHEN gender = '女' THEN 1 END) AS 女性人数,
                    COUNT(CASE WHEN ethnicity != '汉族' THEN 1 END) AS 少数民族人数,
                    COUNT(CASE WHEN education IN ('大专', '大学', '研究生', '硕士', '博士') THEN 1 END) AS 大专以上人数,
                    COUNT(CASE WHEN shi_fou_ru_ku = '未入库' THEN 1 END) AS 未入库人数
                FROM "{SOURCE_TABLE}"
                WHERE organizational_relationship_status IS NULL
                   OR organizational_relationship_status IN ('1', '正常', '4', '组织关系挂靠')
                GROUP BY suo_zai_dang_zhi_bu
            )
            SELECT "支部", "总人数", "入库人数", "预备人数", "女性人数", "少数民族人数", "大专以上人数", "未入库人数"
            FROM stats ORDER BY "总人数" DESC
        """)

        all_rows = cur.fetchall()

        if school_core_names:
            matched_rows = []
            skipped_branches = []
            for row in all_rows:
                branch_name = row[0] or ''
                matched = any(core in branch_name for core in school_core_names)
                if matched:
                    matched_rows.append(row)
                else:
                    skipped_branches.append(branch_name)
            if skipped_branches:
                print(f"[党员统计-自动刷新] 跳过支部: {skipped_branches}")
        else:
            matched_rows = all_rows

        cur.execute(f'DROP TABLE IF EXISTS "{SUMMARY_TABLE}"')
        cur.execute(f"""
            CREATE TABLE "{SUMMARY_TABLE}" (
                id SERIAL PRIMARY KEY,
                "{col_name}" VARCHAR(255),
                "{col_heji}" VARCHAR(255),
                "{col_ruku}" VARCHAR(255),
                "{col_yubei}" VARCHAR(255),
                "{col_nv}" VARCHAR(255),
                "{col_shaoshu}" VARCHAR(255),
                "{col_dazhuan}" VARCHAR(255),
                "{col_weiruku}" VARCHAR(255)
            )
        """)

        total = [0, 0, 0, 0, 0, 0, 0]
        for row in matched_rows:
            for i in range(7):
                val = row[i + 1]
                total[i] += int(val) if val is not None else 0

        cur.execute(f"""
            INSERT INTO "{SUMMARY_TABLE}" 
            ("{col_name}", "{col_heji}", "{col_ruku}", "{col_yubei}", "{col_nv}", "{col_shaoshu}", "{col_dazhuan}", "{col_weiruku}")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, ("总支合计", str(total[0]), str(total[1]), str(total[2]), str(total[3]), str(total[4]), str(total[5]), str(total[6])))

        for row in matched_rows:
            cur.execute(f"""
                INSERT INTO "{SUMMARY_TABLE}" 
                ("{col_name}", "{col_heji}", "{col_ruku}", "{col_yubei}", "{col_nv}", "{col_shaoshu}", "{col_dazhuan}", "{col_weiruku}")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (row[0], str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7])))

        inserted = len(matched_rows) + 1
        conn.commit()
        cur.close()

        print(f"[党员统计-自动刷新] 成功，共 {len(matched_rows)} 个支部 + 1个总支合计")
        return {"success": True, "message": f"汇总数据生成成功，共 {len(matched_rows)} 个支部", "inserted_rows": inserted}

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[党员统计-自动刷新] 失败: {e}")
        return {"success": False, "message": f"刷新失败: {str(e)}"}
    finally:
        if conn:
            conn.close()


@router.post("/backup/monthly")
async def backup_monthly():
    """
    按月备份汇总表
    备份表名：party_member_info_summary_backup_2026_08
    中文名：枣阳市太平镇教育总支党员信息汇总表（2026年8月备份）
    """
    now = datetime.now()
    year_month = now.strftime("%Y_%m")
    backup_table_name = f"{BACKUP_TABLE_PREFIX}_{year_month}"
    chinese_month = f"{now.year}年{now.month}月"
    chinese_backup_name = f"枣阳市太平镇教育总支党员信息汇总表（{chinese_month}备份）"

    return await _do_backup(backup_table_name, chinese_backup_name, "月度")


@router.post("/backup/yearly")
async def backup_yearly():
    """
    按年备份汇总表
    备份表名：party_member_info_summary_backup_2026
    中文名：枣阳市太平镇教育总支党员信息汇总表（2026年备份）
    """
    now = datetime.now()
    year = now.strftime("%Y")
    backup_table_name = f"{BACKUP_TABLE_PREFIX}_{year}"
    chinese_backup_name = f"枣阳市太平镇教育总支党员信息汇总表（{year}年备份）"

    return await _do_backup(backup_table_name, chinese_backup_name, "年度")


async def _do_backup(backup_table_name: str, chinese_name: str, backup_type: str):
    """执行备份操作"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 检查汇总表是否存在且有数据
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{SUMMARY_TABLE}'
            )
        """)
        exists = cur.fetchone()[0]
        if not exists:
            raise HTTPException(status_code=400, detail="汇总表不存在，请先生成汇总数据")

        # 检查是否已有同名备份
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{backup_table_name}'
            )
        """)
        backup_exists = cur.fetchone()[0]

        if backup_exists:
            # 删除旧备份，重新创建
            cur.execute(f'DROP TABLE IF EXISTS "{backup_table_name}"')

        # 复制汇总表结构及数据
        cur.execute(f"""
            CREATE TABLE "{backup_table_name}" AS 
            SELECT * FROM "{SUMMARY_TABLE}"
        """)

        # 添加备份时间字段
        cur.execute(f"""
            ALTER TABLE "{backup_table_name}" 
            ADD COLUMN IF NOT EXISTS backup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """)

        conn.commit()
        cur.close()

        # 添加导航节点
        add_table_to_navigation(backup_table_name, chinese_name)

        return {
            "success": True,
            "message": f"{backup_type}备份成功",
            "backup_table": backup_table_name,
            "backup_name": chinese_name
        }

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.get("/backups")
async def list_backups():
    """
    获取所有备份表列表
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '{BACKUP_TABLE_PREFIX}%'
            ORDER BY table_name DESC
        """)
        tables = cur.fetchall()

        backups = []
        for (table_name,) in tables:
            # 获取中文名
            chinese = get_chinese_name(table_name)
            # 获取记录数
            try:
                cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cur.fetchone()[0]
            except Exception:
                count = 0

            backups.append({
                "table_name": table_name,
                "chinese_name": chinese,
                "record_count": count
            })

        cur.close()
        return {"success": True, "backups": backups}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")
    finally:
        if conn:
            conn.close()


@router.delete("/backup/{backup_table_name}")
async def delete_backup(backup_table_name: str):
    """
    删除指定备份表
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 安全检查：只允许删除备份表
        if not backup_table_name.startswith(BACKUP_TABLE_PREFIX):
            raise HTTPException(status_code=400, detail="不允许删除非备份表")

        cur.execute(f'DROP TABLE IF EXISTS "{backup_table_name}"')
        conn.commit()
        cur.close()

        # 移除导航节点
        remove_table_from_navigation(backup_table_name)

        return {"success": True, "message": f"备份 {backup_table_name} 已删除"}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")
    finally:
        if conn:
            conn.close()