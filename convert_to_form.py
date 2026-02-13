#!/usr/bin/env python3
"""
将Excel导出的HTML转换为可填写的表单
保留100%原始样式，只在空白单元格添加输入框
"""
from bs4 import BeautifulSoup
import re
import os

def convert_html_to_form(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 添加表单样式
    style_tag = soup.find('style')
    if style_tag:
        form_styles = """
/* 表单输入框样式 */
.form-input {
    width: 95%;
    height: 90%;
    border: 1px solid #ccc;
    padding: 2px 5px;
    font-size: inherit;
    font-family: inherit;
    background: #fff;
    box-sizing: border-box;
}
.form-input:focus {
    border-color: #409eff;
    outline: none;
}
"""
        style_tag.string = style_tag.string + form_styles
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    field_count = 0
    
    for table in tables:
        # 查找所有单元格
        cells = table.find_all(['td', 'th'])
        
        for cell in cells:
            # 获取单元格文本内容
            text = cell.get_text(strip=True)
            
            # 如果单元格为空或只有空格，添加输入框
            if not text or text == '' or text.isspace():
                # 检查是否已经有输入元素
                if not cell.find(['input', 'select', 'textarea']):
                    # 创建输入框
                    input_tag = soup.new_tag('input')
                    input_tag['type'] = 'text'
                    input_tag['name'] = f'field_{field_count}'
                    input_tag['id'] = f'field_{field_count}'
                    input_tag['class'] = 'form-input'
                    input_tag['placeholder'] = ''
                    
                    # 清空单元格并添加输入框
                    cell.clear()
                    cell.append(input_tag)
                    
                    field_count += 1
    
    # 在body开始处添加表单标签
    body = soup.find('body')
    if body:
        form_tag = soup.new_tag('form')
        form_tag['id'] = 'retirement_form'
        form_tag['method'] = 'post'
        
        # 将body的所有内容移到form中
        for child in list(body.children):
            form_tag.append(child)
        
        body.append(form_tag)
    
    # 保存转换后的HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f'转换完成！')
    print(f'找到 {len(tables)} 个表格')
    print(f'添加了 {field_count} 个输入框')
    print(f'输出文件: {output_path}')
    
    return field_count

if __name__ == '__main__':
    input_file = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html.html'
    output_file = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html_form.html'
    
    if os.path.exists(input_file):
        convert_html_to_form(input_file, output_file)
    else:
        print(f'输入文件不存在: {input_file}')
