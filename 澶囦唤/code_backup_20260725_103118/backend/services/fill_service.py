from sqlalchemy import create_engine, text
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

DATABASE_URL = 'postgresql://taiping_user:taiping_password@localhost:5432/taiping_education'
engine = create_engine(DATABASE_URL)

class FillService:
    def __init__(self):
        self.engine = engine
    
    def save_field_mapping(self, template_id: int, mappings: List[Dict]) -> Dict:
        """
        保存字段映射配置
        
        Args:
            template_id: 模板ID
            mappings: 映射配置列表
                [{
                    "field_name": "姓名",
                    "field_position": "C3",
                    "source_table": "教师基础信息表",
                    "source_field": "姓名",
                    "stat_type": "直接取值",
                    "stat_formula": None
                }]
        
        Returns:
            {"success": True, "mapping_count": 5}
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM data_filling_field_mappings WHERE template_id = :template_id"),
                    {"template_id": template_id}
                )
                
                for mapping in mappings:
                    conn.execute(
                        text("""
                            INSERT INTO data_filling_field_mappings 
                            (template_id, field_name, field_position, source_table, source_field, stat_type, stat_formula)
                            VALUES (:template_id, :field_name, :field_position, :source_table, :source_field, :stat_type, :stat_formula)
                        """),
                        {
                            "template_id": template_id,
                            "field_name": mapping.get("field_name"),
                            "field_position": mapping.get("field_position"),
                            "source_table": mapping.get("source_table"),
                            "source_field": mapping.get("source_field"),
                            "stat_type": mapping.get("stat_type", "直接取值"),
                            "stat_formula": mapping.get("stat_formula")
                        }
                    )
                
                conn.commit()
            
            return {
                "success": True,
                "mapping_count": len(mappings),
                "message": f"成功保存{len(mappings)}个字段映射配置"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_field_mapping(self, template_id: int) -> Dict:
        """
        获取字段映射配置
        
        Args:
            template_id: 模板ID
        
        Returns:
            {
                "success": True,
                "mappings": [...]
            }
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM data_filling_field_mappings WHERE template_id = :template_id ORDER BY mapping_id"),
                    {"template_id": template_id}
                )
                
                mappings = []
                for row in result:
                    mappings.append({
                        "mapping_id": row.mapping_id,
                        "field_name": row.field_name,
                        "field_position": row.field_position,
                        "source_table": row.source_table,
                        "source_field": row.source_field,
                        "stat_type": row.stat_type,
                        "stat_formula": row.stat_formula
                    })
            
            return {
                "success": True,
                "mappings": mappings
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_fill_record(self, template_id: int, fill_type: str, fill_target: str, 
                          teacher_id: Optional[int] = None, filled_by: str = "系统") -> Dict:
        """
        创建填报记录
        
        Args:
            template_id: 模板ID
            fill_type: 填报类型（unit/personal）
            fill_target: 填报目标（单位名称或个人姓名）
            teacher_id: 教师ID（个人填报时）
            filled_by: 填报人
        
        Returns:
            {
                "success": True,
                "record_id": 123
            }
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO fill_records 
                        (template_id, fill_type, fill_target, teacher_id, filled_by, status)
                        VALUES (:template_id, :fill_type, :fill_target, :teacher_id, :filled_by, 'draft')
                        RETURNING record_id
                    """),
                    {
                        "template_id": template_id,
                        "fill_type": fill_type,
                        "fill_target": fill_target,
                        "teacher_id": teacher_id,
                        "filled_by": filled_by
                    }
                )
                
                record_id = result.fetchone()[0]
                conn.commit()
            
            return {
                "success": True,
                "record_id": record_id,
                "message": "填报记录创建成功"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_fill_record(self, record_id: int, file_path: str, status: str = "submitted") -> Dict:
        """
        更新填报记录
        
        Args:
            record_id: 记录ID
            file_path: 生成的文件路径
            status: 状态（draft/submitted/approved）
        
        Returns:
            {"success": True}
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("""
                        UPDATE fill_records 
                        SET file_path = :file_path, status = :status, updated_at = NOW()
                        WHERE record_id = :record_id
                    """),
                    {
                        "record_id": record_id,
                        "file_path": file_path,
                        "status": status
                    }
                )
                
                conn.commit()
            
            return {
                "success": True,
                "message": "填报记录更新成功"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_fill_records(self, template_id: Optional[int] = None, status: Optional[str] = None) -> Dict:
        """
        获取填报记录列表
        
        Args:
            template_id: 模板ID（可选）
            status: 状态（可选）
        
        Returns:
            {
                "success": True,
                "records": [...]
            }
        """
        try:
            with self.engine.connect() as conn:
                sql = "SELECT * FROM fill_records WHERE 1=1"
                params = {}
                
                if template_id:
                    sql += " AND template_id = :template_id"
                    params["template_id"] = template_id
                
                if status:
                    sql += " AND status = :status"
                    params["status"] = status
                
                sql += " ORDER BY created_at DESC"
                
                result = conn.execute(text(sql), params)
                
                records = []
                for row in result:
                    records.append({
                        "record_id": row.record_id,
                        "template_id": row.template_id,
                        "fill_type": row.fill_type,
                        "fill_target": row.fill_target,
                        "teacher_id": row.teacher_id,
                        "fill_date": str(row.fill_date) if row.fill_date else None,
                        "filled_by": row.filled_by,
                        "status": row.status,
                        "file_path": row.file_path,
                        "created_at": str(row.created_at) if row.created_at else None
                    })
            
            return {
                "success": True,
                "records": records
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
