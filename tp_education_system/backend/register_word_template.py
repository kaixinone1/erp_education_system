"""注册Word模板到数据库"""
import psycopg2, json, datetime, uuid

conn = psycopg2.connect(host='localhost',dbname='taiping_education',user='taiping_user',password='taiping_password')
cur = conn.cursor()

# 生成模板id
template_id = f"tpl_{uuid.uuid4().hex[:8]}"

# 构建Word模板的配置JSON
word_config = {
    "模板类型": "word",
    "模板文件": r"D:\erp_thirteen\数据库信息\模板\职工退休呈报表.docx",
    "占位符": [
        "姓名","性别","出生年月","民族","文化程度","是否独生子女",
        "入党年月","职务","技术职称","参加工作时间","工作年限",
        "籍贯","现住址","自何年何月","至何年何月","在何单位任何职","证明人及其住址",
        "退休原因","直系亲属信息","退休后居住地址","发给退休费的单位",
        "退休方式序号","退休执行年月","审批退休方式序号","审批退休执行年月",
        "独生子女费金额","特殊贡献奖金额","补贴执行年月",
        "最后一次职务（技术职称升降时间",
        "岗位2","职务2","薪级2","岗位5","职务5","薪级5","岗位8","职务8","薪级8"
    ]
}

# 先检查是否已存在
cur.execute("SELECT COUNT(*) FROM template_configs WHERE 模板名称 = %s", ('职工退休呈报表（Word版）',))
cur.execute("SELECT 模板id FROM template_configs WHERE 模板名称 = %s", ('职工退休呈报表（Word版）',))
row = cur.fetchone()
if row:
    cur.execute("""
        UPDATE template_configs 
        SET 模板类型=%s, 原始文件路径=%s, 配置json=%s, 更新时间=%s
        WHERE 模板名称=%s
    """, ('审批表', r'D:\erp_thirteen\数据库信息\模板\职工退休呈报表.docx', 
          json.dumps(word_config, ensure_ascii=False), datetime.datetime.now(),
          '职工退休呈报表（Word版）'))
    print("Word模板已更新")
else:
    cur.execute("""
        INSERT INTO template_configs (模板id, 模板名称, 模板类型, 原始文件路径, 配置json, 创建时间, 更新时间)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (template_id, '职工退休呈报表（Word版）', '审批表', 
          r'D:\erp_thirteen\数据库信息\模板\职工退休呈报表.docx',
          json.dumps(word_config, ensure_ascii=False), 
          datetime.datetime.now(), datetime.datetime.now()))
    print(f"Word模板已注册 (id={template_id})")

conn.commit()

# 验证
cur.execute("SELECT 模板名称, 模板类型, 原始文件路径 FROM template_configs WHERE 模板名称 LIKE '%退休%'")
for r in cur.fetchall():
    print(f"  {r[0]} | {r[1]} | {r[2]}")

conn.close()