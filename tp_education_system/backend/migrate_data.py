#!/usr/bin/env python3
"""
数据迁移脚本：将英文表数据迁移到中文表
"""
import psycopg2

def migrate_data():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()

    # 迁移数据
    cursor.execute("""
        INSERT INTO "高龄老人补贴信息" (
            序号, 姓名, 性别, 身份证号码, 退休单位, 户籍地, 现住址,
            银行账号, 开户行, 本人联系电话, 代理人姓名, 与本人关系,
            代理人联系电话, 备注, 状态, 信息来源
        )
        SELECT
            sequence::int, name, gender, id_card, retired_unit, household,
            field_53, account, field_55, contact_phone_1, name_1, field_58,
            contact_phone_2, field_60, '创建', '手动录入'
        FROM octogenarian_elderly_subsidy_info
        WHERE id_card NOT IN (
            SELECT 身份证号码 FROM "高龄老人补贴信息"
        )
    """)

    conn.commit()
    print(f'迁移了 {cursor.rowcount} 条记录')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    migrate_data()
