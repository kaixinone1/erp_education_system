"""
分析"从数据库获取数据"按钮的备注信息生成逻辑
"""

print("=" * 70)
print("备注信息生成逻辑分析")
print("=" * 70)

print("""
【1. 数据来源】
表名: performance_pay_remarks (绩效工资备注表)

【2. 查询字段】
- remark_type: 变动类型
- teacher_name: 教师姓名
- original_status: 原始状态
- new_status: 新状态
- original_post: 原始岗位
- new_post: 新岗位
- change_category: 变动类别
- change_detail: 变动详情

【3. 变动类型判断逻辑】

当 change_category == 'status_change' 时:

| 条件 | group_label | 示例输出 |
|------|-------------|----------|
| new_status='死亡' 且 original_status='退休' | 退休教师死亡 | 退休教师死亡2人：赵明安、候兴志 |
| new_status='死亡' 且 original_status!='退休' | 教师死亡/岗位死亡 | 教师死亡1人：张三 |
| new_status='调离' | 岗位调离 | 一级教师调离1人：李四 |
| new_status='调出' | 岗位调出 | 二级教师调出1人：王五 |
| new_status='离职' | 岗位离职 | 高级教师离职1人：赵六 |
| new_status='辞职' | 岗位辞职 | 教师辞职1人：钱七 |
| new_status='退休' | 岗位退休 | 一级教师退休2人：孙八、周九 |
| ... | ... | ... |

【4. 备注生成规则】
- 相同类型的变动记录合并
- 格式: "序号.类型人数：姓名列表"
- 多行用 '\n     ' 连接

【5. 返回结果】
result_data['notes'] = '退休教师死亡2人：赵明安、候兴志'

【6. 前端处理】
Object.assign(dynamicData, data)
→ dynamicData.notes = '退休教师死亡2人：赵明安、候兴志'

【7. 关键代码位置】
backend/routes/performance_pay_routes.py
- 第546-554行: 查询 performance_pay_remarks 表
- 第590-593行: 判断 '死亡' 且 '退休' 的逻辑
- 第708-717行: 生成备注字符串

【8. 结论】
备注信息来自数据库表 performance_pay_remarks，
不是硬编码，而是根据数据库中的变动记录自动计算生成。
""")

print("=" * 70)