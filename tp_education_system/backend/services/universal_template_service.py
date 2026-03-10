"""
通用模板服务 - 全自动导入、填报、导出
核心原则：零配置，全自动，100%保留格式
"""
import os
import re
import shutil
from typing import Dict, List, Any, Optional
from docx import Document


class UniversalTemplateService:
    """通用模板服务类"""
    
    def __init__(self):
        self.supported_formats = ['docx', 'html', 'htm', 'xlsx', 'xls']
    
    def extract_placeholders(self, file_path: str) -> List[str]:
        """
        从模板文件中提取所有 {{占位符}}
        支持：Word, Excel, HTML
        """
        if not os.path.exists(file_path):
            return []
        
        # 根据文件扩展名判断格式
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        
        try:
            if ext == 'docx':
                return self._extract_from_docx(file_path)
            elif ext in ['html', 'htm']:
                return self._extract_from_html(file_path)
            elif ext in ['xlsx', 'xls']:
                return self._extract_from_excel(file_path)
            else:
                # 默认按文本处理
                return self._extract_from_text_file(file_path)
        except Exception as e:
            print(f"提取占位符失败: {e}")
            return []
    
    def _extract_from_docx(self, file_path: str) -> List[str]:
        """从Word文档提取占位符"""
        doc = Document(file_path)
        placeholders = []
        
        # 从段落提取
        for para in doc.paragraphs:
            placeholders.extend(self._find_placeholders(para.text))
        
        # 从表格提取
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    placeholders.extend(self._find_placeholders(cell.text))
        
        return list(set(placeholders))
    
    def _extract_from_html(self, file_path: str) -> List[str]:
        """从HTML文件提取占位符"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self._find_placeholders(content)
    
    def _extract_from_excel(self, file_path: str) -> List[str]:
        """从Excel文件提取占位符"""
        from openpyxl import load_workbook
        wb = load_workbook(file_path)
        ws = wb.active
        
        placeholders = []
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    placeholders.extend(self._find_placeholders(str(cell.value)))
        
        return list(set(placeholders))
    
    def _extract_from_text_file(self, file_path: str) -> List[str]:
        """从文本文件提取占位符"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return self._find_placeholders(content)
    
    def _find_placeholders(self, text: str) -> List[str]:
        """从文本中查找 {{占位符}}"""
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, text)
        return [f'{{{{{match}}}}}' for match in matches]
    
    def fill_template(self, template_path: str, output_path: str, data: Dict[str, Any]) -> str:
        """
        填充模板
        复制模板，替换占位符，100%保留格式
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"模板不存在: {template_path}")
        
        # 复制模板
        shutil.copy(template_path, output_path)
        
        # 根据格式处理
        ext = os.path.splitext(template_path)[1].lower().lstrip('.')
        
        if ext == 'docx':
            self._fill_docx(output_path, data)
        elif ext in ['html', 'htm']:
            self._fill_html(output_path, data)
        elif ext in ['xlsx', 'xls']:
            self._fill_excel(output_path, data)
        
        return output_path
    
    def _fill_docx(self, file_path: str, data: Dict[str, Any]):
        """填充Word文档 - 只替换文本，保留格式"""
        doc = Document(file_path)
        
        # 处理段落
        for para in doc.paragraphs:
            self._replace_in_paragraph(para, data)
        
        # 处理表格
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._replace_in_paragraph(para, data)
        
        doc.save(file_path)
    
    def _replace_in_paragraph(self, paragraph, data: Dict[str, Any]):
        """在段落中替换占位符 - 保留格式
        规则：有值则替换，无值（None或空字符串）则保留原占位符
        """
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            if placeholder in paragraph.text:
                # 判断是否有有效值
                if value is not None and str(value).strip() != '':
                    # 有值，进行替换
                    for run in paragraph.runs:
                        if placeholder in run.text:
                            run.text = run.text.replace(placeholder, str(value))
                            # 不修改任何格式属性
                # 无值时保留原占位符，不做任何替换
    
    def _fill_html(self, file_path: str, data: Dict[str, Any]):
        """填充HTML文件
        规则：有值则替换，无值（None或空字符串）则保留原占位符
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            # 判断是否有有效值
            if value is not None and str(value).strip() != '':
                # 有值，进行替换
                content = content.replace(placeholder, str(value))
            # 无值时保留原占位符，不做任何替换
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _fill_excel(self, file_path: str, data: Dict[str, Any]):
        """填充Excel文件
        规则：有值则替换，无值（None或空字符串）则保留原占位符
        """
        from openpyxl import load_workbook
        wb = load_workbook(file_path)
        ws = wb.active
        
        for row in ws.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for key, value in data.items():
                        placeholder = f'{{{{{key}}}}}'
                        if placeholder in cell.value:
                            # 判断是否有有效值
                            if value is not None and str(value).strip() != '':
                                # 有值，进行替换
                                cell.value = cell.value.replace(placeholder, str(value))
                            # 无值时保留原占位符，不做任何替换
        
        wb.save(file_path)


# 全局服务实例
template_service = UniversalTemplateService()
