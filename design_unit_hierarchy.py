from sqlalchemy import create_engine, text
import re

engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')
conn = engine.connect()

# 从学校名称中提取层级信息
result = conn.execute(text("SELECT id, unit FROM dict_unit_dictionary ORDER BY id"))
schools = result.fetchall()

print("学校名称层级分析：")
print("=" * 80)

hierarchy_data = []

for school_id, school_name in schools:
    # 提取层级信息
    province = "湖北省"  # 假设都是湖北省
    city = ""
    county = ""
    town = ""
    school = school_name
    
    # 提取市
    city_match = re.search(r'(.+?市)', school_name)
    if city_match:
        city = city_match.group(1)
    
    # 提取县（如果有）
    county_match = re.search(r'市(.+?县|市)', school_name)
    if county_match:
        county = county_match.group(1)
    
    # 提取镇
    town_match = re.search(r'(.+?镇)', school_name)
    if town_match:
        town = town_match.group(1)
    
    hierarchy_data.append({
        'school_id': school_id,
        'school_name': school_name,
        'province': province,
        'city': city,
        'county': county,
        'town': town
    })
    
    print(f"学校ID: {school_id:2d} | 学校名: {school_name:30s} | 省: {province} | 市: {city} | 县: {county} | 镇: {town}")

# 生成创建单位层级表的SQL
print("\n" + "=" * 80)
print("创建单位层级表的SQL：")
print("=" * 80)

sql = """
-- 创建单位层级表
CREATE TABLE IF NOT EXISTS unit_hierarchy (
    id SERIAL PRIMARY KEY,
    unit_level VARCHAR(20) NOT NULL,  -- 层级：province/city/county/town/school
    unit_name VARCHAR(100) NOT NULL,  -- 单位名称
    parent_id INTEGER REFERENCES unit_hierarchy(id),  -- 父单位ID
    school_id INTEGER,  -- 关联学校ID（仅校级单位）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(unit_level, unit_name, parent_id)
);

-- 插入省级单位
INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id)
VALUES ('province', '湖北省', NULL)
ON CONFLICT (unit_level, unit_name, parent_id) DO NOTHING;

-- 插入市级单位
INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id)
SELECT 'city', '枣阳市', (SELECT id FROM unit_hierarchy WHERE unit_level='province' AND unit_name='湖北省')
WHERE NOT EXISTS (
    SELECT 1 FROM unit_hierarchy WHERE unit_level='city' AND unit_name='枣阳市'
);

-- 插入镇级单位
INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id)
SELECT DISTINCT 'town', '枣阳市太平镇', 
       (SELECT id FROM unit_hierarchy WHERE unit_level='city' AND unit_name='枣阳市')
FROM dict_unit_dictionary
WHERE unit LIKE '%太平镇%'
ON CONFLICT (unit_level, unit_name, parent_id) DO NOTHING;

-- 插入校级单位
INSERT INTO unit_hierarchy (unit_level, unit_name, parent_id, school_id)
SELECT 'school', unit, 
       (SELECT id FROM unit_hierarchy WHERE unit_level='town' AND unit_name='枣阳市太平镇'),
       id
FROM dict_unit_dictionary
ON CONFLICT (unit_level, unit_name, parent_id) DO NOTHING;
"""

print(sql)

conn.close()
