from sqlalchemy import create_engine, text

# 创建数据库连接
engine = create_engine('postgresql://taiping_user:taiping_password@localhost:5432/taiping_education')

with engine.connect() as conn:
    # 查询表结构
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = :table_name
        ORDER BY ordinal_position
    """), {'table_name': 'teacher_record'})
    
    # 打印结果
    print('teacher_record表结构:')
    print('-' * 80)
    print(f'{"列名":<20} {"数据类型":<20} {"是否可为空":<10} {"长度":<10}')
    print('-' * 80)
    
    for row in result:
        length = row.character_maximum_length or '-'
        print(f'{row.column_name:<20} {row.data_type:<20} {row.is_nullable:<10} {str(length):<10}')
    
    print('-' * 80)
    
    # 查询表中的数据行数
    count_result = conn.execute(text("SELECT COUNT(*) FROM teacher_record"))
    count = count_result.scalar()
    print(f'teacher_record表中的数据行数: {count}')
    
    # 如果有数据，查询前3行
    if count > 0:
        print('\n前3行数据:')
        print('-' * 80)
        data_result = conn.execute(text("SELECT * FROM teacher_record LIMIT 3"))
        
        # 获取列名
        columns = data_result.keys()
        print(' | '.join(columns))
        print('-' * 80)
        
        # 打印数据
        for row in data_result:
            print(' | '.join(str(val) for val in row))
        print('-' * 80)
