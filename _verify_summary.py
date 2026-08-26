import psycopg2

conn = psycopg2.connect(host='localhost', port='5432', database='taiping_education', user='taiping_user', password='taiping_password')
cursor = conn.cursor()

# 查看汇总表总支合计行
cursor.execute("""
    SELECT * FROM party_member_info_summary 
    WHERE "党组织名称" = '总支合计'
""")
col_names = [desc[0] for desc in cursor.description]
row = cursor.fetchone()
print("=== 汇总表总支合计: ===")
for name, val in zip(col_names, row):
    print(f"  {name}: {val}")

# 查看各支部明细
cursor.execute("""
    SELECT "党组织名称", "合计" 
    FROM party_member_info_summary 
    WHERE "党组织名称" != '总支合计'
    ORDER BY CAST("合计" AS INTEGER) DESC
""")
print("\n=== 各支部党员数: ===")
total = 0
for r in cursor.fetchall():
    count = int(r[1]) if r[1] and r[1].isdigit() else 0
    total += count
    print(f"  {r[0]}: {r[1]} 人")

print(f"\n各支部合计: {total} 人")

# 验证：对比过滤前后的数据
cursor.execute("""
    SELECT COUNT(*) FROM zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao
""")
raw_total = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*) FROM zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao
    WHERE organizational_relationship_status IS NULL
       OR organizational_relationship_status IN ('1', '正常', '4', '组织关系挂靠')
""")
filtered_total = cursor.fetchone()[0]

cursor.execute("""
    SELECT organizational_relationship_status, COUNT(*) 
    FROM zao_yang_shi_tai_ping_zhen_zhong_xin_xue_xiao_dang_yuan_xin_xi_biao 
    WHERE organizational_relationship_status NOT IN ('1', '正常', '4', '组织关系挂靠')
       AND organizational_relationship_status IS NOT NULL
    GROUP BY organizational_relationship_status
""")
print(f"\n=== 验证: ===")
print(f"  党员信息表总人数: {raw_total}")
print(f"  过滤后人数（正常+挂靠+NULL）: {filtered_total}")
print(f"  被排除的人数: {raw_total - filtered_total}")
print(f"  被排除的明细:")
for r in cursor.fetchall():
    print(f"    状态={r[0]}: {r[1]} 人")

cursor.close()
conn.close()