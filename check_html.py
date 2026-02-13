#!/usr/bin/env python3
from bs4 import BeautifulSoup
import os

file_path = r'd:\erp_thirteen\tp_education_system\backend\templates\职工退休申报表html_form.html'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        inputs = soup.find_all('input')
        print(f'找到 {len(inputs)} 个input元素')
        for idx, inp in enumerate(inputs[:10]):
            name = inp.get('name')
            id_val = inp.get('id')
            print(f'{idx}: name={name}, id={id_val}')
else:
    print('文件不存在')
