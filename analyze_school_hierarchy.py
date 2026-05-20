from sqlalchemy import create_engine, text
import re

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 检查教师基础信息表中是否有学校字段
result = conn.execute(text("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'teacher_basic_info' 
    ORDER BY ordinal_position
"""))
columns = [row[0] for row in result.fetchall()]

print("教师基础信息表字段：")
print(f"  {columns}")

# 检查是否有学校相关字段
school_fields = [col for col in columns if 'school' in col.lower() or 'unit' in col.lower() or '单位' in col or '学校' in col]
print(f"\n学校相关字段：{school_fields}")

# 检查学校名称的命名规律
result = conn.execute(text("SELECT school FROM school_information_table ORDER BY school"))
schools = [row[0] for row in result.fetchall()]

print("\n学校名称示例：")
for school in schools[:20]:
    print(f"  {school}")

# 分析学校名称的层级结构
print("\n学校名称层级分析：")
cities = set()
towns = set()

for school in schools:
    # 提取市名
    city_match = re.search(r'(.+?市)', school)
    if city_match:
        cities.add(city_match.group(1))
    
    # 提取镇名
    town_match = re.search(r'(.+?镇)', school)
    if town_match:
        towns.add(town_match.group(1))

print(f"市级单位：{sorted(cities)}")
print(f"镇级单位：{sorted(towns)}")

conn.close()
