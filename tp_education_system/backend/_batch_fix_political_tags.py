"""
批量修复政治标签（共青团员、团籍、群众）
数据源：id_card 表（通过身份证号关联 teacher_basic_info）
判定规则：
  - 共青团员 (tag_id=13): id_card.league_member = '是'
  - 团籍 (tag_id=14): id_card.league_member = '是'（tuan_ji 字段当前全为空，暂用 league_member）
  - 群众 (tag_id=15): id_card.party_member != '是' AND id_card.league_member != '是'
"""
import psycopg2

DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "taiping_education",
    "user": "taiping_user",
    "password": "taiping_password"
}

TAG_IDS = {
    'gqty': 13,   # 共青团员
    'tj': 14,     # 团籍
    '群众': 15,   # 群众
}


def _is_yes(val):
    """判断字段值是否为'是'"""
    if val is None:
        return False
    return str(val).strip() == '是'


def main():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()

    # 1. 获取所有教师及其身份证号
    cursor.execute('SELECT id, "姓名", "身份证号码" FROM teacher_basic_info')
    teachers = cursor.fetchall()
    print(f"=== 教师总数: {len(teachers)} ===")

    # 2. 获取 id_card 表中的政治面貌数据
    cursor.execute('SELECT id_card, party_member, league_member, tuan_ji, masses FROM id_card')
    id_card_rows = cursor.fetchall()
    id_card_map = {}
    for row in id_card_rows:
        id_card_map[row[0]] = {
            'party_member': row[1],
            'league_member': row[2],
            'tuan_ji': row[3],
            'masses': row[4],
        }
    print(f"=== id_card 表记录数: {len(id_card_map)} ===")

    # 统计
    stats = {
        "共青团员新增": 0,
        "团籍新增": 0,
        "群众新增": 0,
        "共青团员移除": 0,
        "团籍移除": 0,
        "群众移除": 0,
        "无id_card记录": 0,
        "无身份证号": 0,
        "处理总数": 0,
    }

    # 3. 批量获取当前政治标签（13, 14, 15）
    cursor.execute(
        "SELECT employee_id, tag_id FROM employee_tag_relations WHERE tag_id IN (13, 14, 15)"
    )
    existing_tags = {}
    for row in cursor.fetchall():
        eid = row[0]
        tid = row[1]
        if eid not in existing_tags:
            existing_tags[eid] = set()
        existing_tags[eid].add(tid)

    # 4. 逐教师处理
    batch_inserts = []
    batch_deletes = []

    for teacher_id, name, id_card in teachers:
        stats["处理总数"] += 1

        if not id_card:
            stats["无身份证号"] += 1
            continue

        # 查找 id_card 表记录
        card_data = id_card_map.get(id_card)
        if not card_data:
            stats["无id_card记录"] += 1
            continue

        is_party = _is_yes(card_data['party_member'])
        is_league = _is_yes(card_data['league_member'])
        is_tuan_ji = _is_yes(card_data['tuan_ji'])

        current_tags = existing_tags.get(teacher_id, set())

        # 共青团员判定
        if is_league:
            if TAG_IDS['gqty'] not in current_tags:
                batch_inserts.append((teacher_id, TAG_IDS['gqty']))
                stats["共青团员新增"] += 1
        else:
            if TAG_IDS['gqty'] in current_tags:
                batch_deletes.append((teacher_id, TAG_IDS['gqty']))
                stats["共青团员移除"] += 1

        # 团籍判定
        if is_tuan_ji or is_league:
            if TAG_IDS['tj'] not in current_tags:
                batch_inserts.append((teacher_id, TAG_IDS['tj']))
                stats["团籍新增"] += 1
        else:
            if TAG_IDS['tj'] in current_tags:
                batch_deletes.append((teacher_id, TAG_IDS['tj']))
                stats["团籍移除"] += 1

        # 群众判定
        if not is_party and not is_league:
            if TAG_IDS['群众'] not in current_tags:
                batch_inserts.append((teacher_id, TAG_IDS['群众']))
                stats["群众新增"] += 1
        else:
            if TAG_IDS['群众'] in current_tags:
                batch_deletes.append((teacher_id, TAG_IDS['群众']))
                stats["群众移除"] += 1

    # 5. 执行批量删除
    if batch_deletes:
        print(f"\n=== 执行批量删除: {len(batch_deletes)} 条 ===")
        for teacher_id, tag_id in batch_deletes:
            cursor.execute(
                "DELETE FROM employee_tag_relations WHERE employee_id = %s AND tag_id = %s",
                (teacher_id, tag_id)
            )
        conn.commit()
        print("批量删除完成")

    # 6. 执行批量插入
    if batch_inserts:
        print(f"\n=== 执行批量插入: {len(batch_inserts)} 条 ===")
        for teacher_id, tag_id in batch_inserts:
            cursor.execute(
                "INSERT INTO employee_tag_relations (employee_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (teacher_id, tag_id)
            )
        conn.commit()
        print("批量插入完成")

    # 7. 验证结果
    print()
    print("=== 统计结果 ===")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 8. 验证标签分布
    cursor.execute("""
        SELECT tag_id, COUNT(*) FROM employee_tag_relations 
        WHERE tag_id IN (13, 14, 15) 
        GROUP BY tag_id ORDER BY tag_id
    """)
    print()
    print("=== 修复后政治标签分布: ===")
    for row in cursor.fetchall():
        tag_names = {13: '共青团员', 14: '团籍', 15: '群众'}
        print(f"  {tag_names.get(row[0], row[0])} (tag_id={row[0]}): {row[1]} 人")

    # 9. 验证交叉情况
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT CASE WHEN r.tag_id = 13 THEN r.employee_id END) as 共青团员,
            COUNT(DISTINCT CASE WHEN r.tag_id = 14 THEN r.employee_id END) as 团籍,
            COUNT(DISTINCT CASE WHEN r.tag_id = 15 THEN r.employee_id END) as 群众
        FROM employee_tag_relations r
        WHERE r.tag_id IN (13, 14, 15)
    """)
    row = cursor.fetchone()
    print()
    print(f"=== 政治标签去重统计: ===")
    print(f"  共青团员: {row[0]} 人")
    print(f"  团籍: {row[1]} 人")
    print(f"  群众: {row[2]} 人")

    cursor.close()
    conn.close()
    print("\n=== 政治标签批量修复完成 ===")


if __name__ == '__main__':
    main()