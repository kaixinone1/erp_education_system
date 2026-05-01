"""
绩效工资审批表路由 - FastAPI版本
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import json
import sys

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}


def get_db_connection():
    import psycopg2
    return psycopg2.connect(**DATABASE_CONFIG)

router = APIRouter(prefix="/api/performance-pay-approval", tags=["绩效工资审批"])

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'performance_pay_approval')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups', 'performance_pay_approval')
SCAN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'performance_pay_scans')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(SCAN_DIR, exist_ok=True)


class PerformancePayData(BaseModel):
    """绩效工资数据模型"""
    填报单位: str = "太平中心学校"
    年月: str = ""
    填报时间: str = ""
    
    # 行政管理人员
    副处级人数: int = 0
    副处级标准: float = 0
    正科级人数: int = 0
    正科级标准: float = 0
    副科级人数: int = 0
    副科级标准: float = 0
    科员级人数: int = 0
    科员级标准: float = 1185
    办事员级人数: int = 0
    办事员级标准: float = 0
    
    # 专业技术人员
    正高级教师人数: int = 0
    正高级教师标准: float = 1862
    高级教师人数: int = 0
    高级教师标准: float = 1523
    一级教师人数: int = 0
    一级教师标准: float = 1309
    二级教师人数: int = 0
    二级教师标准: float = 1241
    三级教师人数: int = 0
    三级教师标准: float = 1128
    
    # 工人
    高级技师人数: int = 0
    高级技师标准: float = 0
    技师人数: int = 0
    技师标准: float = 1331
    高级工人数: int = 0
    高级工标准: float = 1219
    中级工人数: int = 0
    中级工标准: float = 1185
    初级工人数: int = 0
    初级工标准: float = 1106
    普工人数: int = 0
    普工标准: float = 1106
    
    # 汇总
    绩效人数合计: int = 0
    绩效工资合计: float = 0
    
    # 乡镇补贴
    在职人数: int = 0
    乡镇补贴标准: float = 350
    乡镇补贴合计: float = 0
    
    # 退休人员
    退休干部: int = 0
    退休职工: int = 0
    离休干部人数: int = 0
    
    # 遗留问题
    遗留问题详情: str = ""
    遗留问题人数: int = 0
    遗留问题金额: float = 0
    无补贴人数: int = 0
    无补贴名单: str = ""
    
    # 备注
    备注: str = ""


class YearMonthRequest(BaseModel):
    year: int
    month: int


@router.get("/current")
def get_current_month_data(year: int = datetime.now().year, month: int = datetime.now().month):
    """获取指定月份的数据"""
    filename = f"performance_pay_{year}_{month:02d}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    
    return {"status": "success", "data": None}

@router.get("/data/{year}/{month}")
def get_month_data(year: int, month: int):
    """获取指定月份的数据"""
    filename = f"performance_pay_{year}_{month:02d}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {"status": "success", "data": data}
    
    return {"status": "success", "data": None}


@router.post("/save")
def save_data(data: PerformancePayData):
    """保存数据"""
    try:
        # 获取年月
        year_month = data.年月
        if year_month:
            try:
                year, month = year_month.replace('年', '-').replace('月', '').split('-')
                year = int(year)
                month = int(month)
            except:
                year = datetime.now().year
                month = datetime.now().month
        else:
            year = datetime.now().year
            month = datetime.now().month
        
        # 保存JSON数据
        filename = f"performance_pay_{year}_{month:02d}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
        
        # 保存教师状态快照（用于下月比较变化）
        try:
            teacher_snapshot = {}
            conn2 = get_db_connection()
            cursor2 = conn2.cursor()
            cursor2.execute("""
                SELECT t.id_card, t.name, t.employment_status, i.post_2
                FROM teacher_basic_info t
                LEFT JOIN information i ON t.id_card = i.id_card
            """)
            for row in cursor2.fetchall():
                teacher_snapshot[row[0]] = {
                    'name': row[1],
                    'status': row[2],
                    'post': row[3]
                }
            cursor2.close()
            conn2.close()
            
            # 保存快照
            snapshot_file = os.path.join(DATA_DIR, f'{year}_{month:02d}_teachers.json')
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(teacher_snapshot, f, ensure_ascii=False)
            print(f"教师状态快照已保存: {snapshot_file}")
        except Exception as e:
            print(f"保存教师状态快照失败: {e}")
        
        # 自动备份Excel
        try:
            from utils.excel_export import export_performance_pay_approval
            excel_path = export_performance_pay_approval(data.dict(), BACKUP_DIR)
            print(f"Excel备份已生成: {excel_path}")
        except Exception as e:
            print(f"Excel备份失败: {e}")
        
        # 自动备份PDF
        try:
            from utils.pdf_export import export_performance_pay_approval_pdf
            pdf_path = export_performance_pay_approval_pdf(data.dict(), BACKUP_DIR)
            print(f"PDF备份已生成: {pdf_path}")
        except Exception as e:
            print(f"PDF备份失败: {e}")
        
        return {"status": "success", "message": "保存成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-from-database")
def load_from_database(req: YearMonthRequest):
    """从数据库加载数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        result_data = {
            'administrative': {},
            'professional': {},
            'worker': {},
            'totals': {
                'performance_count': 0,
                'performance_total': 0,
                'legacy_count': 0,
                'legacy_total': 0
            },
            'subsidies': {
                'count': 0,
                'standard': 0,
                'total': 0
            },
            'legacy': [],
            'retirees': {
                'cadre_count': 0,
                'worker_count': 0,
                'retired_count': 0
            },
            'notes': ''
        }
        
        salary_standards = {}
        try:
            cursor.execute("SELECT post_1, month_performance_salary FROM dict_salary_dictionary")
            for row in cursor.fetchall():
                if row[1]:
                    try:
                        salary_standards[row[0]] = float(row[1])
                    except (ValueError, TypeError):
                        pass
        except Exception as e:
            print(f"读取工资标准失败: {e}")
        
        # 获取有绩效工资标签的人员ID列表
        performance_tag_employee_ids = set()
        try:
            cursor.execute("""
                SELECT DISTINCT employee_id 
                FROM employee_tag_relations 
                WHERE tag_id = (SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资')
            """)
            for row in cursor.fetchall():
                if row[0]:
                    performance_tag_employee_ids.add(row[0])
            print(f"有绩效工资标签的人员数量: {len(performance_tag_employee_ids)}")
        except Exception as e:
            print(f"获取绩效标签人员失败: {e}")
        
        # 从information表读取岗位名称，筛选有绩效工资标签的人员
        position_counts = {}
        try:
            cursor.execute("""
                SELECT post_2, COUNT(*) as cnt
                FROM information
                WHERE id_card IN (
                    SELECT id_card FROM teacher_basic_info 
                    WHERE id IN ({})
                )
                AND post_2 IS NOT NULL AND post_2 != ''
                GROUP BY post_2
            """.format(','.join([str(x) for x in performance_tag_employee_ids]) if performance_tag_employee_ids else '0'))
            for row in cursor.fetchall():
                if row[0]:
                    position_counts[row[0]] = row[1]
        except Exception as e:
            print(f"读取岗位信息失败: {e}")
        
        result_data['administrative'] = {
            '副处级': {
                'count': position_counts.get('副处级', 0),
                'standard': salary_standards.get('副处级', 0),
                'subtotal': position_counts.get('副处级', 0) * salary_standards.get('副处级', 0)
            },
            '正科级': {
                'count': position_counts.get('正科级', 0),
                'standard': salary_standards.get('正科级', 0),
                'subtotal': position_counts.get('正科级', 0) * salary_standards.get('正科级', 0)
            },
            '副科级': {
                'count': position_counts.get('副科级', 0),
                'standard': salary_standards.get('副科级', 0),
                'subtotal': position_counts.get('副科级', 0) * salary_standards.get('副科级', 0)
            },
            '科员级': {
                'count': position_counts.get('九级管理', position_counts.get('科员级', 0)),
                'standard': salary_standards.get('九级管理', salary_standards.get('科员级', 1185)),
                'subtotal': position_counts.get('九级管理', position_counts.get('科员级', 0)) * salary_standards.get('九级管理', salary_standards.get('科员级', 1185))
            },
            '办事员级': {
                'count': position_counts.get('办事员级', 0),
                'standard': salary_standards.get('办事员级', 0),
                'subtotal': position_counts.get('办事员级', 0) * salary_standards.get('办事员级', 0)
            }
        }
        
        result_data['professional'] = {
            '正高级': {
                'count': position_counts.get('正高级教师', 0),
                'standard': salary_standards.get('正高级教师', 1862),
                'subtotal': position_counts.get('正高级教师', 0) * salary_standards.get('正高级教师', 1862)
            },
            '高级教师': {
                'count': position_counts.get('高级教师', 0),
                'standard': salary_standards.get('高级教师', 1523),
                'subtotal': position_counts.get('高级教师', 0) * salary_standards.get('高级教师', 1523)
            },
            '一级教师': {
                'count': position_counts.get('一级教师', 0),
                'standard': salary_standards.get('一级教师', 1309),
                'subtotal': position_counts.get('一级教师', 0) * salary_standards.get('一级教师', 1309)
            },
            '二级教师': {
                'count': position_counts.get('二级教师', 0),
                'standard': salary_standards.get('二级教师', 1241),
                'subtotal': position_counts.get('二级教师', 0) * salary_standards.get('二级教师', 1241)
            },
            '三级教师': {
                'count': position_counts.get('三级教师', 0),
                'standard': salary_standards.get('三级教师', 1128),
                'subtotal': position_counts.get('三级教师', 0) * salary_standards.get('三级教师', 1128)
            }
        }
        
        result_data['worker'] = {
            '高级技师': {
                'count': position_counts.get('高级技师', 0),
                'standard': salary_standards.get('高级技师', 0),
                'subtotal': position_counts.get('高级技师', 0) * salary_standards.get('高级技师', 0)
            },
            '技师': {
                'count': position_counts.get('技师', 0),
                'standard': salary_standards.get('技师', 1331),
                'subtotal': position_counts.get('技师', 0) * salary_standards.get('技师', 1331)
            },
            '高级工': {
                'count': position_counts.get('高级工', 0),
                'standard': salary_standards.get('高级工', 1219),
                'subtotal': position_counts.get('高级工', 0) * salary_standards.get('高级工', 1219)
            },
            '中级工': {
                'count': position_counts.get('中级工', 0),
                'standard': salary_standards.get('中级工', 1185),
                'subtotal': position_counts.get('中级工', 0) * salary_standards.get('中级工', 1185)
            },
            '初级工': {
                'count': position_counts.get('初级工', 0),
                'standard': salary_standards.get('初级工', 1106),
                'subtotal': position_counts.get('初级工', 0) * salary_standards.get('初级工', 1106)
            }
        }
        
        total_count = sum([
            result_data['administrative']['副处级']['count'],
            result_data['administrative']['正科级']['count'],
            result_data['administrative']['副科级']['count'],
            result_data['administrative']['科员级']['count'],
            result_data['administrative']['办事员级']['count'],
            result_data['professional']['正高级']['count'],
            result_data['professional']['高级教师']['count'],
            result_data['professional']['一级教师']['count'],
            result_data['professional']['二级教师']['count'],
            result_data['professional']['三级教师']['count'],
            result_data['worker']['高级技师']['count'],
            result_data['worker']['技师']['count'],
            result_data['worker']['高级工']['count'],
            result_data['worker']['中级工']['count'],
            result_data['worker']['初级工']['count']
        ])
        
        total_amount = sum([
            result_data['administrative']['副处级']['subtotal'],
            result_data['administrative']['正科级']['subtotal'],
            result_data['administrative']['副科级']['subtotal'],
            result_data['administrative']['科员级']['subtotal'],
            result_data['administrative']['办事员级']['subtotal'],
            result_data['professional']['正高级']['subtotal'],
            result_data['professional']['高级教师']['subtotal'],
            result_data['professional']['一级教师']['subtotal'],
            result_data['professional']['二级教师']['subtotal'],
            result_data['professional']['三级教师']['subtotal'],
            result_data['worker']['高级技师']['subtotal'],
            result_data['worker']['技师']['subtotal'],
            result_data['worker']['高级工']['subtotal'],
            result_data['worker']['中级工']['subtotal'],
            result_data['worker']['初级工']['subtotal']
        ])
        
        result_data['totals']['performance_count'] = total_count
        result_data['totals']['performance_total'] = total_amount
        
        # 乡镇补贴人数：同时勾选了"绩效"和"乡镇补贴"标签的人员
        subsidy_employee_ids = set()
        try:
            # 先获取绩效工资标签的ID
            cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资'")
            performance_tag = cursor.fetchone()
            # 获取乡镇补贴标签的ID
            cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '乡镇补贴'")
            subsidy_tag = cursor.fetchone()
            
            if performance_tag and subsidy_tag:
                performance_id = performance_tag[0]
                subsidy_id = subsidy_tag[0]
                
                cursor.execute("""
                    SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s
                    INTERSECT
                    SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s
                """, (performance_id, subsidy_id))
                
                for row in cursor.fetchall():
                    if row[0]:
                        subsidy_employee_ids.add(row[0])
                
                result_data['subsidies']['count'] = len(subsidy_employee_ids)
                print(f"同时有绩效和乡镇补贴标签的人员数量: {len(subsidy_employee_ids)}")
            else:
                result_data['subsidies']['count'] = 0
        except Exception as e:
            print(f"读取乡镇补贴人数失败: {e}")
            result_data['subsidies']['count'] = 0
    
        # 乡镇补贴标准
        result_data['subsidies']['standard'] = 350
        try:
            cursor.execute("SELECT subsidy_amount FROM town_subsidy_standards WHERE is_active = true LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                result_data['subsidies']['standard'] = float(row[0])
        except Exception as e:
            print(f"读取乡镇补贴标准失败: {e}")
        
        result_data['subsidies']['total'] = result_data['subsidies']['count'] * result_data['subsidies']['standard']
        
        # 有绩效标签但没有乡镇补贴的人员名单
        no_subsidy_names = []
        try:
            print("=== 开始查询无乡镇补贴人员 ===")
            cursor.execute("""
                SELECT t.name 
                FROM teacher_basic_info t
                JOIN employee_tag_relations etr1 ON t.id = etr1.employee_id
                JOIN personal_dict_dictionary pdd1 ON etr1.tag_id = pdd1.id
                WHERE pdd1.biao_qian = '绩效工资'
                AND NOT EXISTS (
                    SELECT 1 FROM employee_tag_relations etr2
                    JOIN personal_dict_dictionary pdd2 ON etr2.tag_id = pdd2.id
                    WHERE etr2.employee_id = t.id AND pdd2.biao_qian = '乡镇补贴'
                )
            """)
            
            for row in cursor.fetchall():
                if row[0]:
                    no_subsidy_names.append(row[0])
            
            print(f"有绩效但无乡镇补贴的人员名单: {no_subsidy_names}")
            
            result_data['no_subsidy_names'] = '、'.join(no_subsidy_names) if no_subsidy_names else ''
            result_data['no_subsidy_count'] = len(no_subsidy_names)
        except Exception as e:
            print(f"读取无乡镇补贴人员失败: {e}")
            result_data['no_subsidy_names'] = ''
            result_data['no_subsidy_count'] = 0
        
        # 退休人员统计 - 支持数字和中文两种存储方式
        try:
            # 退休干部 = 任职状态为"退休" 且 个人身份为"干部"或"1"
            cursor.execute("""
                SELECT COUNT(*)
                FROM teacher_basic_info tbi
                JOIN teacher_personal_identity tpi ON tbi.id_card = tpi.id_card
                WHERE tbi.employment_status = '退休' AND (tpi.ge_ren_shen_fen = '1' OR tpi.ge_ren_shen_fen = '干部')
            """)
            row = cursor.fetchone()
            result_data['retirees']['cadre_count'] = int(row[0] or 0) if row else 0
            
            # 退休工人 = 任职状态为"退休" 且 个人身份为"工人"或"2"
            cursor.execute("""
                SELECT COUNT(*)
                FROM teacher_basic_info tbi
                JOIN teacher_personal_identity tpi ON tbi.id_card = tpi.id_card
                WHERE tbi.employment_status = '退休' AND (tpi.ge_ren_shen_fen = '2' OR tpi.ge_ren_shen_fen = '工人')
            """)
            row = cursor.fetchone()
            result_data['retirees']['worker_count'] = int(row[0] or 0) if row else 0
            
            # 离休干部 = 任职状态为"离休"
            cursor.execute("SELECT COUNT(*) FROM teacher_basic_info WHERE employment_status = '离休'")
            row = cursor.fetchone()
            result_data['retirees']['retired_count'] = int(row[0] or 0) if row else 0
            
            print(f"退休干部: {result_data['retirees']['cadre_count']}, 退休职工: {result_data['retirees']['worker_count']}, 离休干部: {result_data['retirees']['retired_count']}")
        except Exception as e:
            print(f"读取退休人数失败: {e}")
        
        # 遗留问题 - 从 personal_statistics 表读取
        try:
            cursor.execute("""
                SELECT name, field_63 
                FROM personal_statistics 
                WHERE field_63 IS NOT NULL AND field_63 != ''
            """)
            rows = cursor.fetchall()
            
            if rows:
                names = []
                total_amount = 0
                for row in rows:
                    names.append(row[0])
                    try:
                        total_amount += float(row[1]) if row[1] else 0
                    except:
                        pass
                
                result_data['totals']['legacy_count'] = len(names)
                result_data['totals']['legacy_total'] = total_amount
                result_data['legacy'] = [{'name': row[0], 'amount': float(row[1]) if row[1] else 0} for row in rows]
                
            print(f"遗留问题人数: {result_data['totals']['legacy_count']}, 金额: {result_data['totals']['legacy_total']}")
        except Exception as e:
            print(f"读取遗留问题失败: {e}")
        
        try:
            report_month = f"{req.year}-{req.month:02d}"
            
            cursor.execute("""
                SELECT remark_type, teacher_name, original_status, new_status, 
                       original_post, new_post, change_category, change_detail
                FROM performance_pay_remarks
                WHERE report_period = %s
                ORDER BY id
            """, (report_month,))
            
            remarks_records = cursor.fetchall()
            
            notes_groups = {}
            
            for row in remarks_records:
                remark_type = row[0]
                teacher_name = row[1]
                original_status = row[2] if row[2] else ''
                new_status = row[3] if row[3] else ''
                original_post = row[4] if row[4] else ''
                new_post = row[5] if row[5] else ''
                change_category = row[6] if row[6] else ''
                change_detail = row[7] if row[7] else ''
                
                key = None
                group_label = ''
                
                if change_category == 'status_change':
                    if new_status in ['调离']:
                        level = original_post if original_post else '教师'
                        key = f'调离_{level}'
                        group_label = f'{level}调离'
                    elif new_status in ['调出']:
                        level = original_post if original_post else '教师'
                        key = f'调出_{level}'
                        group_label = f'{level}调出'
                    elif new_status in ['离职']:
                        level = original_post if original_post else '教师'
                        key = f'离职_{level}'
                        group_label = f'{level}离职'
                    elif new_status in ['辞职']:
                        level = original_post if original_post else '教师'
                        key = f'辞职_{level}'
                        group_label = f'{level}辞职'
                    elif new_status in ['死亡']:
                        if original_status == '退休':
                            key = '去世_退休'
                            group_label = '退休教师死亡'
                        else:
                            level = original_post if original_post else '教师'
                            key = f'死亡_{level}'
                            if level == '教师':
                                group_label = '教师死亡'
                            else:
                                group_label = f'{level}死亡'
                    elif new_status in ['退休'] and original_status == '在职':
                        level = original_post if original_post else '教师'
                        key = f'退休_{level}'
                        if level == '教师':
                            group_label = '教师退休'
                        else:
                            group_label = f'{level}退休'
                    elif new_status in ['病休']:
                        level = original_post if original_post else '教师'
                        key = f'病休_{level}'
                        group_label = f'{level}病休'
                    elif new_status in ['延迟退休']:
                        level = original_post if original_post else '教师'
                        key = f'延迟退休_{level}'
                        group_label = f'{level}延迟退休'
                    elif new_status in ['在职'] and original_status == '退休':
                        level = original_post if original_post else '教师'
                        key = f'返聘_{level}'
                        group_label = f'{level}返聘'
                    elif new_status in ['挂职锻炼']:
                        level = original_post if original_post else '教师'
                        key = f'挂职_{level}'
                        group_label = f'{level}挂职锻炼'
                    elif new_status in ['待岗']:
                        level = original_post if original_post else '教师'
                        key = f'待岗_{level}'
                        group_label = f'{level}待岗'
                    elif new_status in ['停薪留职']:
                        level = original_post if original_post else '教师'
                        key = f'停薪留职_{level}'
                        group_label = f'{level}停薪留职'
                
                elif change_category == 'position_change':
                    if original_post == '一级教师' and new_post == '高级教师':
                        key = '晋升_一级_高级'
                        group_label = '一级教师晋升高级教师'
                    elif original_post == '二级教师' and new_post == '一级教师':
                        key = '晋升_二级_一级'
                        group_label = '二级教师晋升一级教师'
                    elif original_post == '三级教师' and new_post == '二级教师':
                        key = '晋升_三级_二级'
                        group_label = '三级教师晋升二级教师'
                    elif original_post == '三级教师' and new_post == '一级教师':
                        key = '晋升_三级_一级'
                        group_label = '三级教师晋升一级教师'
                    elif original_post == '二级教师' and new_post == '高级教师':
                        key = '晋升_二级_高级'
                        group_label = '二级教师晋升高级教师'
                    elif '高级工' in original_post and '技师' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    elif '技师' in original_post and '高级技师' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    elif '初级工' in original_post and '中级工' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    elif '中级工' in original_post and '高级工' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    elif '九级管理' in original_post and '八级管理' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    elif '八级管理' in original_post and '七级管理' in new_post:
                        key = f'晋升_{original_post}_{new_post}'
                        group_label = f'{original_post}晋升{new_post}'
                    else:
                        # 其他岗位变更
                        key = f'岗位变更_{original_post}_{new_post}'
                        group_label = f'{original_post}变更为{new_post}'
                
                elif change_category == 'new_add':
                    if change_detail == 'transfer_in' or '调入' in change_detail:
                        level = new_post if new_post else (original_post if original_post else '教师')
                        key = f'调入_{level}'
                        group_label = f'{level}调入'
                    elif change_detail == 'new_hire' or '新录聘' in change_detail:
                        level = new_post if new_post else (original_post if original_post else '教师')
                        key = f'新录聘_{level}'
                        group_label = f'{level}新录聘'
                    elif change_detail == 'management':
                        level = new_post if new_post else (original_post if original_post else '九级管理')
                        key = f'管理新增_{level}'
                        group_label = f'{level}新增'
                    elif change_detail == 'graduate' or '应届' in change_detail or '毕业生' in change_detail:
                        level = new_post if new_post else (original_post if original_post else '教师')
                        key = f'应届_{level}'
                        group_label = f'{level}应届毕业生'
                    elif change_detail == 'talent' or '引进' in change_detail:
                        level = new_post if new_post else (original_post if original_post else '教师')
                        key = f'引进_{level}'
                        group_label = f'{level}人才引进'
                    elif change_detail == 'intern' or '见习' in change_detail:
                        level = new_post if new_post else (original_post if original_post else '教师')
                        key = f'见习_{level}'
                        group_label = f'{level}见习期'
                    else:
                        # 默认处理新增人员
                        level = new_post if new_post else '教师'
                        key = f'新增_{level}'
                        group_label = f'{level}调入'
                
                if key and teacher_name:
                    if key not in notes_groups:
                        notes_groups[key] = {'label': group_label, 'names': []}
                    notes_groups[key]['names'].append(teacher_name)
            
            notes_parts = []
            seq = 1
            for key, group in notes_groups.items():
                count = len(group['names'])
                names_str = '、'.join(group['names'])
                if count > 0:
                    notes_parts.append(f"{seq}.{group['label']}{count}人：{names_str}")
                    seq += 1
            
            result_data['notes'] = '\n     '.join(notes_parts) if notes_parts else ''
            print(f"备注信息: {result_data['notes']}")
        except Exception as e:
            print(f"读取备注信息失败: {e}")
            import traceback
            print(traceback.format_exc())
            result_data['notes'] = ''
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": result_data}
        
    except Exception as e:
        import traceback
        print(f"加载数据失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
def export_data(data: PerformancePayData, format: str = "excel"):
    """导出数据"""
    try:
        if format == 'excel':
            from app.utils.excel_export_new import export_performance_pay_approval_new
            filepath = export_performance_pay_approval_new(data.dict())
            return FileResponse(filepath, filename=f"绩效工资审批表_{data.年月}.xlsx")
        elif format == 'pdf':
            from app.utils.pdf_export import export_performance_pay_approval_pdf
            filepath = export_performance_pay_approval_pdf(data.dict())
            return FileResponse(filepath, filename=f"绩效工资审批表_{data.年月}.pdf")
        else:
            raise HTTPException(status_code=400, detail="不支持的格式")
            
    except Exception as e:
        import traceback
        print(f"导出失败: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def get_history():
    """获取历史记录列表"""
    return get_history_list()


@router.get("/list")
def get_list(page: int = 1, size: int = 20, year: str = None):
    """获取绩效工资审批列表（支持分页和年份过滤）"""
    result = get_history_list(year)
    
    # 分页处理
    data = result['data']
    total = len(data)
    
    # 计算分页范围
    start = (page - 1) * size
    end = start + size
    paginated_data = data[start:end]
    
    return {"status": "success", "data": paginated_data, "total": total}


def get_history_list(year: str = None):
    """获取历史记录列表（可过滤年份）"""
    history = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.startswith('performance_pay_') and filename.endswith('.json'):
            # 从文件名解析年份（格式: performance_pay_2026_05.json）
            file_year = None
            try:
                parts = filename.replace('performance_pay_', '').replace('.json', '').split('_')
                if len(parts) >= 1:
                    file_year = parts[0]
            except:
                pass
            
            # 如果指定了年份，过滤不匹配的文件
            if year and file_year != year:
                continue
            
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从文件名解析年月
            year_month = ''
            try:
                parts = filename.replace('performance_pay_', '').replace('.json', '').split('_')
                if len(parts) == 2:
                    year_month = f"{parts[0]}-{parts[1]}"
            except:
                pass
            
            history.append({
                'id': filename.replace('.json', ''),
                'year_month': year_month,
                'report_unit': data.get('填报单位', '') or data.get('report_unit', ''),
                'total_people': data.get('绩效人数合计', 0) or data.get('total_people', 0),
                'total_amount': data.get('绩效工资合计', 0) or data.get('total_amount', 0),
                'town_subsidy_amount': data.get('乡镇补贴合计', 0) or data.get('town_subsidy_amount', 0),
                'town_subsidy_people': data.get('乡镇补贴人数', 0) or data.get('town_subsidy_people', 0),
                'retired_cadre_count': data.get('退休干部人数', 0) or data.get('retired_cadre_count', 0),
                'retired_worker_count': data.get('退休工人数', 0) or data.get('retired_worker_count', 0),
                'retired_cadre_office_count': data.get('离休干部人数', 0) or data.get('retired_cadre_office_count', 0),
                'legacy_total_people': data.get('遗留问题人数', 0) or data.get('legacy_total_people', 0),
                'legacy_total_amount': data.get('遗留问题金额', 0) or data.get('legacy_total_amount', 0),
                'remarks': data.get('备注', '') or data.get('notes', ''),
                'status': 'generated',
                'has_excel': False,
                'has_pdf': False,
                'has_scanned': False,
                'created_at': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 按年月倒序排序
    history.sort(key=lambda x: x['year_month'], reverse=True)
    
    return {"status": "success", "data": history, "total": len(history)}


@router.get("/download/{id}")
def download_file(id: str):
    """下载历史文件"""
    filename = f"{id}.xlsx"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename)
    
    raise HTTPException(status_code=404, detail="文件不存在")


@router.get("/download-pdf/{id}")
def download_pdf(id: str):
    """下载PDF文件"""
    filename = f"{id}.pdf"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if os.path.exists(filepath):
        return FileResponse(filepath, filename=filename)
    
    raise HTTPException(status_code=404, detail="文件不存在")


@router.post("/upload-scan")
def upload_scan(file: UploadFile = File(...), 年月: str = Form(...)):
    """上传签字盖章扫描件"""
    try:
        # 保存文件
        filename = f"绩效工资审批表_{年月}_签字盖章{os.path.splitext(file.filename)[1]}"
        filepath = os.path.join(SCAN_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file.file.read())
        
        return {
            "status": "success",
            "message": "上传成功",
            "filename": filename,
            "path": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scans")
def get_scans():
    """获取扫描件列表"""
    scans = []
    
    for filename in os.listdir(SCAN_DIR):
        filepath = os.path.join(SCAN_DIR, filename)
        scans.append({
            'filename': filename,
            'upload_time': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S'),
            'size': os.path.getsize(filepath)
        })
    
    scans.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return {"status": "success", "data": scans}


@router.get("/yearly-summary")
def get_yearly_summary(year: int = datetime.now().year):
    """获取年度汇总数据"""
    try:
        # 查找该年份的所有月度数据
        yearly_data = {}
        months = []
        
        for filename in os.listdir(DATA_DIR):
            if filename.startswith(f'performance_pay_{year}_') and filename.endswith('.json'):
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 提取月份
                month_str = filename.replace(f'performance_pay_{year}_', '').replace('.json', '')
                month = int(month_str)
                months.append(month)
                
                # 累加数据
                for key, value in data.items():
                    if '人数' in key or '合计' in key or '金额' in key:
                        if isinstance(value, (int, float)):
                            if key not in yearly_data:
                                yearly_data[key] = 0
                            yearly_data[key] += value
        
        months.sort()
        
        # 构建汇总信息
        if months:
            start_month = months[0]
            end_month = months[-1]
            summary_note = f"从{year}年{start_month}月汇总至{year}年{end_month}月"
        else:
            summary_note = f"{year}年暂无数据"
        
        return {
            "status": "success",
            "data": yearly_data,
            "months": months,
            "summary_note": summary_note,
            "year": year
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
