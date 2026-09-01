# -*- coding: utf-8 -*-
"""构造save请求，验证兼容性JSON写入"""
import json
import urllib.request

# 1. 调用fill获取填报配置
fill_payload = {
    "模板ID": "tpl_15cc984d",
    "查询条件": {"年月": "2026-08"},
    "统计范围": {
        "单位范围": {
            "学校": {"unit_name": "枣阳市太平镇中心学校"}
        }
    },
    "填报口径": {
        "统计类型": "在职+退休",
        "包含调离": False
    },
    "封面单位": "枣阳市太平镇中心学校"
}

print("=== 第1步：调用/fill获取填报配置 ===")
req = urllib.request.Request(
    "http://localhost:8000/api/universal-template/fill",
    data=json.dumps(fill_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=60) as resp:
    fill_result = json.loads(resp.read().decode('utf-8'))

print("fill成功:", fill_result.get('成功'))
data = fill_result.get('数据', {})
config = data.get('配置', {})
remark = data.get('备注', '')
print("备注长度:", len(remark))
print("配置中单元格数:", len(config.get('单元格数据', [])))

# 2. 调用save接口
print("\n=== 第2步：调用/save触发兼容性JSON写入 ===")
save_payload = {
    "模板ID": "tpl_15cc984d",
    "查询条件": {"年月": "2026-08"},
    "统计范围": fill_payload["统计范围"],
    "填报口径": fill_payload["填报口径"],
    "封面单位": "枣阳市太平镇中心学校",
    "填报配置": config,
    "备注": remark,
    "导出格式": "Excel"
}

req2 = urllib.request.Request(
    "http://localhost:8000/api/universal-template/save",
    data=json.dumps(save_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'},
    method='POST'
)
try:
    with urllib.request.urlopen(req2, timeout=120) as resp:
        save_result = json.loads(resp.read().decode('utf-8'))
    print("save成功:", save_result.get('成功'))
    print("save消息:", save_result.get('消息', ''))
    if not save_result.get('成功'):
        print("save错误详情:", json.dumps(save_result, ensure_ascii=False)[:500])
except Exception as e:
    print("save异常:", e)

# 3. 检查兼容性JSON
print("\n=== 第3步：检查兼容性JSON文件 ===")
import os, datetime
json_path = 'data/performance_pay_approval/performance_pay_2026_08.json'
if os.path.exists(json_path):
    mtime = os.path.getmtime(json_path)
    print("文件修改时间:", datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'))
    cj = json.load(open(json_path, encoding='utf-8'))
    print("绩效人数合计:", cj.get('绩效人数合计'))
    print("绩效工资合计:", cj.get('绩效工资合计'))
    print("在职人数:", cj.get('在职人数'))
    print("乡镇补贴合计:", cj.get('乡镇补贴合计'))
    print("退休干部:", cj.get('退休干部'))
    print("退休职工:", cj.get('退休职工'))
    print("离休干部人数:", cj.get('离休干部人数'))
    print("高级教师人数:", cj.get('高级教师人数'))
    print("一级教师人数:", cj.get('一级教师人数'))
    print("二级教师人数:", cj.get('二级教师人数'))
    print("遗留问题人数:", cj.get('遗留问题人数'))
    print("遗留问题金额:", cj.get('遗留问题金额'))
    print("备注长度:", len(cj.get('备注', '')))
    print("备注内容(前300字):", cj.get('备注', '')[:300])
