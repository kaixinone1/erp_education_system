"""
数据迁移路由 - 宽表转长表等ETL操作
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional
import sys
import os

# 添加services目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tag_migration_service import execute_tag_migration

router = APIRouter(prefix="/api/migration", tags=["migration"])


@router.post("/transform-tags")
async def transform_tags(data: Dict[str, Any]):
    """
    执行标签宽表转长表迁移
    
    请求参数:
    {
        "source_table": "raw_teacher_tags_wide",  # 源宽表名
        "teacher_table": "teacher_basic_info",     # 教师主表名
        "tag_table": "person_tags",                # 标签字典表名
        "relation_table": "employee_tag_relations", # 关系表名
        "id_card_column": "身份证号码",             # 身份证号码列名
        "name_column": "姓名"                      # 姓名列名
    }
    
    返回:
    {
        "success": true/false,
        "processed_count": 1000,    # 处理的记录数
        "success_count": 950,       # 成功写入的记录数
        "failed_count": 50,         # 失败的记录数
        "failed_records": [...],    # 失败记录详情（前10条）
        "message": "成功迁移 950 条标签关系"
    }
    """
    try:
        # 获取参数（使用默认值）
        source_table = data.get("source_table", "raw_teacher_tags_wide")
        teacher_table = data.get("teacher_table", "teacher_basic_info")
        tag_table = data.get("tag_table", "personal_dict_dictionary")
        relation_table = data.get("relation_table", "employee_tag_relations")
        id_card_column = data.get("id_card_column", "身份证号码")
        name_column = data.get("name_column", "姓名")
        
        # 执行迁移
        result = execute_tag_migration(
            source_table=source_table,
            teacher_table=teacher_table,
            tag_table=tag_table,
            relation_table=relation_table,
            id_card_column=id_card_column,
            name_column=name_column
        )
        
        return result
        
    except Exception as e:
        print(f"标签迁移API失败: {e}")
        raise HTTPException(status_code=500, detail=f"迁移失败: {str(e)}")


@router.get("/preview")
async def preview_migration(
    source_table: str = "raw_teacher_tags_wide",
    limit: int = 10
):
    """
    预览迁移数据
    
    参数:
    - source_table: 源表名
    - limit: 预览行数
    
    返回:
    {
        "status": "success",
        "data": [...],  # 预览数据
        "total_rows": 1000,  # 总行数
        "tag_columns": [...]  # 标签列名列表
    }
    """
    try:
        from services.tag_migration_service import transform_wide_to_long
        import pandas as pd
        
        # 读取宽表数据
        from sqlalchemy import create_engine
        engine = create_engine("postgresql://taiping_user:taiping_password@localhost:5432/taiping_education")
        
        # 获取总行数
        count_query = f"SELECT COUNT(*) FROM {source_table}"
        total_rows = pd.read_sql(count_query, engine).iloc[0, 0]
        
        # 获取列信息
        columns_query = f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{source_table}' AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        columns_df = pd.read_sql(columns_query, engine)
        all_columns = columns_df['column_name'].tolist()
        
        # 识别标识列和标签列
        id_columns = ["身份证号码", "姓名", "id_card", "name"]
        id_columns = [col for col in id_columns if col in all_columns]
        tag_columns = [col for col in all_columns if col not in id_columns]
        
        # 转换长表（限制行数）
        query = f"SELECT * FROM {source_table} LIMIT {limit}"
        df_wide = pd.read_sql(query, engine)
        
        if len(df_wide) == 0:
            return {
                "status": "success",
                "data": [],
                "total_rows": 0,
                "tag_columns": tag_columns,
                "message": "源表为空"
            }
        
        # 转换为长表
        df_long = df_wide.melt(
            id_vars=id_columns,
            var_name="标签名称",
            value_name="标签值"
        )
        
        # 只保留值为"是"的记录
        df_long = df_long[df_long["标签值"] == "是"]
        
        return {
            "status": "success",
            "data": df_long.to_dict('records'),
            "total_rows": int(total_rows),
            "tag_columns": tag_columns,
            "preview_count": len(df_long)
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"预览迁移数据失败: {e}")
        
        # 检查是否是表不存在的错误
        if "does not exist" in error_msg or "UndefinedTable" in error_msg:
            return {
                "status": "error",
                "message": f"表 '{source_table}' 不存在，请先导入数据",
                "data": [],
                "total_rows": 0,
                "tag_columns": []
            }
        
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.get("/tables")
async def get_migration_tables():
    """
    获取可用于迁移的表列表（带中文名）
    
    返回:
    {
        "status": "success",
        "tables": [
            {"name": "raw_teacher_tags_wide", "chinese_name": "教师标签宽表", "type": "source", "description": "原始宽表数据"},
            ...
        ]
    }
    """
    try:
        from sqlalchemy import create_engine
        import pandas as pd
        import json
        import os
        
        engine = create_engine("postgresql://taiping_user:taiping_password@localhost:5432/taiping_education")
        
        # 加载表名映射配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'merged_schema_mappings.json')
        chinese_names = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                tables_config = config.get('tables', {})
                for table_name, table_info in tables_config.items():
                    chinese_names[table_name] = table_info.get('chinese_name', table_name)
        
        # 获取所有表
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        df = pd.read_sql(query, engine)
        
        tables = []
        for _, row in df.iterrows():
            table_name = row['table_name']
            chinese_name = chinese_names.get(table_name, table_name)
            
            # 判断表类型
            if 'raw_' in table_name or 'wide' in table_name:
                table_type = "source"
                description = "原始宽表数据"
            elif 'teacher' in table_name or table_name == 'id_card':
                table_type = "master"
                description = "教师主表"
            elif 'dict' in table_name or 'dictionary' in table_name:
                table_type = "dictionary"
                description = "标签/字典表"
            else:
                table_type = "other"
                description = "其他表"
            
            tables.append({
                "name": table_name,
                "chinese_name": chinese_name,
                "type": table_type,
                "description": description
            })
        
        return {
            "status": "success",
            "tables": tables
        }
        
    except Exception as e:
        print(f"获取表列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表列表失败: {str(e)}")


@router.get("/download-unmatched")
async def download_unmatched_file(file: str):
    """
    下载未匹配教师列表Excel文件
    
    参数:
    - file: 文件名
    
    返回:
    - Excel文件下载
    """
    try:
        # 构建文件路径
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        file_path = os.path.join(exports_dir, file)
        
        # 安全检查：确保文件在exports目录下
        if not os.path.abspath(file_path).startswith(os.path.abspath(exports_dir)):
            raise HTTPException(status_code=400, detail="非法文件路径")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=file
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"下载文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")
