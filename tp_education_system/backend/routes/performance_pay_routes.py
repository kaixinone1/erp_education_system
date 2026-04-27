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
    """获取当前月的数据"""
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
        
        data = {
            '填报单位': '太平中心学校',
            '年月': f"{req.year}年{req.month}月",
            '填报时间': datetime.now().strftime('%Y年%m月%d日'),
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
        
        data['副处级人数'] = position_counts.get('副处级', 0)
        data['副处级标准'] = salary_standards.get('副处级', 0)
        data['正科级人数'] = position_counts.get('正科级', 0)
        data['正科级标准'] = salary_standards.get('正科级', 0)
        data['副科级人数'] = position_counts.get('副科级', 0)
        data['副科级标准'] = salary_standards.get('副科级', 0)
        data['科员级人数'] = position_counts.get('九级管理', position_counts.get('科员级', 0))
        data['科员级标准'] = salary_standards.get('九级管理', salary_standards.get('科员级', 1185))
        data['办事员级人数'] = position_counts.get('办事员级', 0)
        data['办事员级标准'] = salary_standards.get('办事员级', 0)
        
        data['正高级教师人数'] = position_counts.get('正高级教师', 0)
        data['正高级教师标准'] = salary_standards.get('正高级教师', 1862)
        data['高级教师人数'] = position_counts.get('高级教师', 0)
        data['高级教师标准'] = salary_standards.get('高级教师', 1523)
        data['一级教师人数'] = position_counts.get('一级教师', 0)
        data['一级教师标准'] = salary_standards.get('一级教师', 1309)
        data['二级教师人数'] = position_counts.get('二级教师', 0)
        data['二级教师标准'] = salary_standards.get('二级教师', 1241)
        data['三级教师人数'] = position_counts.get('三级教师', 0)
        data['三级教师标准'] = salary_standards.get('三级教师', 1128)
        
        data['高级技师人数'] = position_counts.get('高级技师', 0)
        data['高级技师标准'] = salary_standards.get('高级技师', 0)
        data['技师人数'] = position_counts.get('技师', 0)
        data['技师标准'] = salary_standards.get('技师', 1331)
        data['高级工人数'] = position_counts.get('高级工', 0)
        data['高级工标准'] = salary_standards.get('高级工', 1219)
        data['中级工人数'] = position_counts.get('中级工', 0)
        data['中级工标准'] = salary_standards.get('中级工', 1185)
        data['初级工人数'] = position_counts.get('初级工', 0)
        data['初级工标准'] = salary_standards.get('初级工', 1106)
        data['普工人数'] = position_counts.get('普通工', position_counts.get('普工', 0))
        data['普工标准'] = salary_standards.get('普通工', salary_standards.get('普工', 1106))
        
        total_count = sum([
            data['副处级人数'], data['正科级人数'], data['副科级人数'],
            data['科员级人数'], data['办事员级人数'],
            data['正高级教师人数'], data['高级教师人数'],
            data['一级教师人数'], data['二级教师人数'], data['三级教师人数'],
            data['高级技师人数'], data['技师人数'], data['高级工人数'],
            data['中级工人数'], data['初级工人数'], data['普工人数']
        ])
        data['绩效人数合计'] = total_count
        
        total_amount = sum([
            data['副处级人数'] * data['副处级标准'],
            data['正科级人数'] * data['正科级标准'],
            data['副科级人数'] * data['副科级标准'],
            data['科员级人数'] * data['科员级标准'],
            data['办事员级人数'] * data['办事员级标准'],
            data['正高级教师人数'] * data['正高级教师标准'],
            data['高级教师人数'] * data['高级教师标准'],
            data['一级教师人数'] * data['一级教师标准'],
            data['二级教师人数'] * data['二级教师标准'],
            data['三级教师人数'] * data['三级教师标准'],
            data['高级技师人数'] * data['高级技师标准'],
            data['技师人数'] * data['技师标准'],
            data['高级工人数'] * data['高级工标准'],
            data['中级工人数'] * data['中级工标准'],
            data['初级工人数'] * data['初级工标准'],
            data['普工人数'] * data['普工标准']
        ])
        data['绩效工资合计'] = total_amount
        
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
                
                # 获取同时拥有这两个标签的人员ID（使用 intersect）
                cursor.execute("""
                    SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s
                    INTERSECT
                    SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s
                """, (performance_id, subsidy_id))
                
                for row in cursor.fetchall():
                    if row[0]:
                        subsidy_employee_ids.add(row[0])
                
                data['在职人数'] = len(subsidy_employee_ids)
                print(f"同时有绩效和乡镇补贴标签的人员数量: {len(subsidy_employee_ids)}")
            else:
                data['在职人数'] = 0
        except Exception as e:
            print(f"读取乡镇补贴人数失败: {e}")
            data['在职人数'] = 0
        
        # 乡镇补贴标准
        data['乡镇补贴标准'] = 350
        try:
            cursor.execute("SELECT subsidy_amount FROM town_subsidy_standards WHERE is_active = true LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                data['乡镇补贴标准'] = float(row[0])
        except Exception as e:
            print(f"读取乡镇补贴标准失败: {e}")
        
        data['乡镇补贴合计'] = data['在职人数'] * data['乡镇补贴标准']
        
        # 退休人员统计 - 支持数字和中文两种存储方式
        data['退休干部'] = 0
        data['退休职工'] = 0
        data['离休干部人数'] = 0
        try:
            # 退休干部 = 任职状态为"退休" 且 个人身份为"干部"或"1"
            cursor.execute("""
                SELECT COUNT(*)
                FROM teacher_basic_info tbi
                JOIN teacher_personal_identity tpi ON tbi.id_card = tpi.id_card
                WHERE tbi.employment_status = '退休' AND (tpi.ge_ren_shen_fen = '1' OR tpi.ge_ren_shen_fen = '干部')
            """)
            row = cursor.fetchone()
            data['退休干部'] = int(row[0] or 0) if row else 0
            
            # 退休工人 = 任职状态为"退休" 且 个人身份为"工人"或"2"
            cursor.execute("""
                SELECT COUNT(*)
                FROM teacher_basic_info tbi
                JOIN teacher_personal_identity tpi ON tbi.id_card = tpi.id_card
                WHERE tbi.employment_status = '退休' AND (tpi.ge_ren_shen_fen = '2' OR tpi.ge_ren_shen_fen = '工人')
            """)
            row = cursor.fetchone()
            data['退休职工'] = int(row[0] or 0) if row else 0
            
            # 离休干部 = 任职状态为"离休"
            cursor.execute("SELECT COUNT(*) FROM teacher_basic_info WHERE employment_status = '离休'")
            row = cursor.fetchone()
            data['离休干部人数'] = int(row[0] or 0) if row else 0
            
            print(f"退休干部: {data['退休干部']}, 退休职工: {data['退休职工']}, 离休干部: {data['离休干部人数']}")
        except Exception as e:
            print(f"读取退休人数失败: {e}")
        
        # 遗留问题 - 从 personal_statistics 表读取
        data['遗留问题详情'] = ''
        data['遗留问题人数'] = 0
        data['遗留问题金额'] = 0
        try:
            # 读取所有遗留问题人员 - field_63是字符串类型
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
                
                data['遗留问题人数'] = len(names)
                data['遗留问题金额'] = total_amount
                data['遗留问题详情'] = '、'.join(names)
                
            print(f"遗留问题人数: {data['遗留问题人数']}, 金额: {data['遗留问题金额']}, 详情: {data['遗留问题详情']}")
        except Exception as e:
            print(f"读取乡镇补贴标准失败: {e}")
        
        # 无补贴人数：有"绩效工资"标签但没有"乡镇补贴"标签的人员
        data['无补贴人数'] = 0
        data['无补贴名单'] = ''
        try:
            # 获取绩效工资标签的ID
            cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '绩效工资'")
            performance_tag = cursor.fetchone()
            # 获取乡镇补贴标签的ID
            cursor.execute("SELECT id FROM personal_dict_dictionary WHERE biao_qian = '乡镇补贴'")
            subsidy_tag = cursor.fetchone()
            
            if performance_tag:
                performance_id = performance_tag[0]
                
                # 获取所有有绩效工资标签的人员
                cursor.execute("SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s", (performance_id,))
                performance_employees = set(row[0] for row in cursor.fetchall() if row[0])
                
                if subsidy_tag:
                    subsidy_id = subsidy_tag[0]
                    # 获取有乡镇补贴标签的人员
                    cursor.execute("SELECT employee_id FROM employee_tag_relations WHERE tag_id = %s", (subsidy_id,))
                    subsidy_employees = set(row[0] for row in cursor.fetchall() if row[0])
                    
                    # 无补贴 = 有绩效但没有乡镇补贴
                    no_subsidy_ids = performance_employees - subsidy_employees
                else:
                    no_subsidy_ids = performance_employees
                
                data['无补贴人数'] = len(no_subsidy_ids)
                
                # 获取姓名列表
                if no_subsidy_ids:
                    placeholders = ','.join(['%s'] * len(no_subsidy_ids))
                    cursor.execute(f"""
                        SELECT name FROM teacher_basic_info 
                        WHERE id IN ({placeholders})
                    """, list(no_subsidy_ids))
                    names = [row[0] for row in cursor.fetchall() if row[0]]
                    data['无补贴名单'] = '、'.join(names)
                
                print(f"无补贴人数: {data['无补贴人数']}, 名单: {data['无补贴名单']}")
        except Exception as e:
            print(f"读取无补贴人数失败: {e}")
        
        data['备注'] = ''
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": data}
        
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
            from utils.excel_export import export_performance_pay_approval
            filepath = export_performance_pay_approval(data.dict())
            return FileResponse(filepath, filename=f"绩效工资审批表_{data.年月}.xlsx")
        elif format == 'pdf':
            from utils.pdf_export import export_performance_pay_approval_pdf
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
    history = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            history.append({
                'id': filename.replace('.json', ''),
                '年月': data.get('年月', ''),
                '填报单位': data.get('填报单位', ''),
                '绩效人数合计': data.get('绩效人数合计', 0),
                '绩效工资合计': data.get('绩效工资合计', 0),
                '创建时间': datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # 按年月倒序排序
    history.sort(key=lambda x: x['年月'], reverse=True)
    
    return {"status": "success", "data": history}


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
