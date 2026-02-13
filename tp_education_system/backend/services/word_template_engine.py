"""
WORD模板引擎 - 填充WORD模板
"""
import os
import psycopg2
from datetime import datetime

def fill_word_template(template_id: str, teacher_id: int, get_db_connection) -> str:
    """
    填充WORD模板
    
    参数:
        template_id: 模板ID
        teacher_id: 教师ID
        get_db_connection: 获取数据库连接的函数
    
    返回:
        生成的文件路径
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取模板信息
        cursor.execute("""
            SELECT template_name, file_path 
            FROM document_templates 
            WHERE template_id = %s
        """, (template_id,))
        template_row = cursor.fetchone()
        
        if not template_row:
            raise ValueError(f"模板不存在: {template_id}")
        
        template_name = template_row[0]
        template_path = template_row[1]
        
        # 获取教师姓名
        cursor.execute("""
            SELECT name FROM teacher_basic_info WHERE id = %s
        """, (teacher_id,))
        teacher_row = cursor.fetchone()
        teacher_name = teacher_row[0] if teacher_row else "未知"
        
        # 生成输出文件名: 模板名称+教师姓名.docx
        output_dir = r'd:\erp_thirteen\tp_education_system\backend\uploads\generated'
        os.makedirs(output_dir, exist_ok=True)
        
        # 清理文件名中的非法字符
        safe_template_name = "".join(c for c in template_name if c.isalnum() or c in (' ', '_', '-'))
        safe_teacher_name = "".join(c for c in teacher_name if c.isalnum() or c in (' ', '_', '-'))
        
        filename = f"{safe_template_name}_{safe_teacher_name}.docx"
        output_path = os.path.join(output_dir, filename)
        
        # TODO: 实现实际的WORD填充逻辑
        # 目前只是复制模板文件作为占位
        if os.path.exists(template_path):
            import shutil
            shutil.copy2(template_path, output_path)
        else:
            # 如果模板不存在，创建一个空文件
            with open(output_path, 'w') as f:
                f.write("")
        
        return output_path
        
    finally:
        cursor.close()
        conn.close()
