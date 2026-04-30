import zipfile
import xml.etree.ElementTree as ET

# 解析Excel模板
with zipfile.ZipFile(r'd:\erp_thirteen\数据库信息\模板\义务教育学校教职工绩效工资审批表(1).html', 'r') as z:
    # 读取sheet数据
    with z.open('xl/worksheets/sheet1.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        
        ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        # 获取列宽
        cols = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}col')
        print('=== 列宽配置 ===')
        for col in cols:
            print(f"列{col.get('min')}-{col.get('max')}: {col.get('width')} 字符")
        
        # 获取行高
        rows = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')
        print(f'\n=== 总行数: {len(rows)} ===')
        print('行高配置:')
        for i, row in enumerate(rows):
            print(f"行{i+1}: {row.get('ht')}pt")
        
        # 获取合并单元格
        merges = root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}mergeCell')
        print(f'\n=== 合并单元格数量: {len(merges)} ===')
        for merge in merges[:20]:
            print(f"  {merge.get('ref')}")