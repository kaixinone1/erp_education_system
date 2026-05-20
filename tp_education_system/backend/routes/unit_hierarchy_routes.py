"""
单位层级API路由
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

router = APIRouter(prefix="/api/unit", tags=["单位管理"])

DATABASE_URL = "postgresql://taiping_user:taiping_password@localhost:5432/taiping_education"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@router.get("/tree")
async def get_unit_tree():
    """
    获取单位树形结构
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT id, unit_level, unit_name, parent_id, school_dict_id, full_path
            FROM unit_hierarchy
            ORDER BY id
        """))
        
        units = []
        for row in result:
            units.append({
                "id": row.id,
                "unit_level": row.unit_level,
                "unit_name": row.unit_name,
                "parent_id": row.parent_id,
                "school_dict_id": row.school_dict_id,
                "full_path": row.full_path
            })
        
        return {
            "success": True,
            "units": units
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/children/{parent_id}")
async def get_unit_children(parent_id: int):
    """
    获取指定单位的子单位
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT id, unit_level, unit_name, parent_id, school_dict_id, full_path
            FROM unit_hierarchy
            WHERE parent_id = :parent_id
            ORDER BY unit_name
        """), {"parent_id": parent_id})
        
        units = []
        for row in result:
            units.append({
                "id": row.id,
                "unit_level": row.unit_level,
                "unit_name": row.unit_name,
                "parent_id": row.parent_id,
                "school_dict_id": row.school_dict_id,
                "full_path": row.full_path
            })
        
        return {
            "success": True,
            "units": units
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.get("/teachers/{unit_id}")
async def get_unit_teachers(unit_id: int):
    """
    获取指定单位的教师列表
    
    如果选择的是省/市/镇级单位，返回该单位下所有教师
    如果选择的是校级单位，返回该校所有教师
    """
    session = SessionLocal()
    try:
        result = session.execute(text("""
            SELECT 
                tbi.id as teacher_id,
                tbi.name,
                tbi.id_card,
                tuv.school_name,
                tuv.full_path
            FROM teacher_basic_info tbi
            INNER JOIN teacher_unit_view tuv ON tbi.id = tuv.teacher_id
            WHERE tuv.unit_hierarchy_id = :unit_id
               OR tuv.full_path LIKE (
                   SELECT full_path || '%'
                   FROM unit_hierarchy
                   WHERE id = :unit_id
               )
            ORDER BY tbi.name
        """), {"unit_id": unit_id})
        
        teachers = []
        for row in result:
            teachers.append({
                "teacher_id": row.teacher_id,
                "name": row.name,
                "id_card": row.id_card,
                "school_name": row.school_name,
                "full_path": row.full_path
            })
        
        return {
            "success": True,
            "teachers": teachers,
            "count": len(teachers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
