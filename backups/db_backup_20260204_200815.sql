-- 数据库备份 20260204_200815
-- 表结构和数据


-- 表: data_043854
-- 结构: [('id', 'integer', None), ('姓名', 'character varying', 255), ('身份证号码', 'character varying', 255), ('档案出生日期', 'date', None), ('民族', 'character varying', 255), ('籍贯', 'character varying', 255), ('联系电话', 'character varying', 255), ('参加工作日期', 'date', None), ('进入本单位日期', 'date', None), ('任职状态', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50)]
-- 数据条数: 927
-- 列名: ['id', '姓名', '身份证号码', '档案出生日期', '民族', '籍贯', '联系电话', '参加工作日期', '进入本单位日期', '任职状态', 'created_at', 'updated_at', 'import_batch']
-- (1, '李恩源', '341203199612261536', None, '汉族', '安徽省阜阳市', '17771167309', datetime.date(2018, 9, 1), datetime.date(2024, 9, 1), '在职', None, None, None)
-- (3, '冯锐', '420626199602143021', None, '汉族', '保康市歇马镇', '18827510528', datetime.date(2019, 9, 1), datetime.date(2019, 9, 1), '在职', None, None, None)
-- (4, '周玉美', '420626199412132524', None, '汉族', '保康县马桥镇', '13128878530', datetime.date(2021, 9, 1), datetime.date(1997, 12, 1), '在职', None, None, None)
-- (5, '蔡甜甜', '420626199404061025', None, '汉族', '保康县寺坪镇', '18772100497', datetime.date(2018, 9, 1), datetime.date(1995, 8, 1), '在职', None, None, None)
-- (6, '宋稀', '510722199608207120', None, '汉族', '恩施州巴东县', '18281904401', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (7, '谭玉', '422823199612270220', None, '土家族', '恩施州巴东县', '18807268910', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (8, '徐明星', '422823199706120020', None, '汉族', '恩施州巴东县', '18271851386', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (9, '杨玉琴', '422802200008222701', None, '土家', '恩施州恩施市', '15707279917', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (10, '洪杨尚怡', '420621199906227425', None, '汉族', '樊城区牛首镇', '18371051823', datetime.date(2021, 9, 1), datetime.date(2000, 8, 1), '在职', None, None, None)
-- (11, '李艳', '420625199508285625', None, '汉族', '谷城县紫金镇', '17362634517', datetime.date(2020, 12, 1), datetime.date(1994, 8, 1), '在职', None, None, None)


-- 表: dict_data_dictionary
-- 结构: [('code', 'character varying', 50), ('人才类型', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None)]
-- 数据条数: 4
-- 列名: ['code', '人才类型', 'created_at', 'updated_at']
-- ('专业技术人才', '专业技术人才', None, None)
-- ('技术人才', '技术人才', None, None)
-- ('管理人员', '管理人员', None, None)
-- ('退休人员', '退休人员', None, None)


-- 表: dict_data_personal_identity
-- 结构: [('id', 'integer', None), ('code', 'character varying', 30), ('name', 'character varying', 50), ('sort_order', 'integer', None), ('status', 'boolean', None), ('created_at', 'timestamp without time zone', None)]
-- 数据条数: 2
-- 列名: ['id', 'code', 'name', 'sort_order', 'status', 'created_at']
-- (1, '干部', '干部', None, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 620000))
-- (2, '工人', '工人', None, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 620000))


-- 表: dict_education_dictionary
-- 结构: [('id', 'integer', None), ('code', 'character varying', 30), ('name', 'character varying', 50), ('sort_order', 'integer', None), ('status', 'boolean', None), ('created_at', 'timestamp without time zone', None)]
-- 数据条数: 8
-- 列名: ['id', 'code', 'name', 'sort_order', 'status', 'created_at']
-- (1, '1', '小学', 1, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (2, '2', '初中', 2, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (3, '3', '高中', 3, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (4, '4', '中专', 4, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (5, '5', '专科', 5, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (6, '6', '本科', 6, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (7, '7', '硕士', 7, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))
-- (8, '8', '博士', 8, True, datetime.datetime(2026, 2, 4, 14, 3, 7, 882984))


-- 表: dict_position
-- 结构: [('id', 'integer', None), ('code', 'character varying', 30), ('name', 'character varying', 50), ('sort_order', 'integer', None), ('status', 'boolean', None), ('created_at', 'timestamp without time zone', None)]
-- 数据条数: 5
-- 列名: ['id', 'code', 'name', 'sort_order', 'status', 'created_at']
-- (1, '1', '正高级', 1, True, datetime.datetime(2026, 2, 4, 11, 46, 18, 23281))
-- (2, '2', '高级', 2, True, datetime.datetime(2026, 2, 4, 11, 46, 18, 23281))
-- (3, '3', '中级', 3, True, datetime.datetime(2026, 2, 4, 11, 46, 18, 23281))
-- (4, '4', '助理级', 4, True, datetime.datetime(2026, 2, 4, 11, 46, 18, 23281))
-- (5, '5', '员级', 5, True, datetime.datetime(2026, 2, 4, 11, 46, 18, 23281))


-- 表: dict_teacher_info
-- 结构: [('id', 'integer', None), ('teacher_id', 'integer', None), ('姓名', 'character varying', 255), ('身份证号码', 'character varying', 255), ('人才类型', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50)]
-- 数据条数: 927
-- 列名: ['id', 'teacher_id', '姓名', '身份证号码', '人才类型', 'created_at', 'updated_at', 'import_batch']
-- (1, 1, '李恩源', '341203199612261536', '1', None, None, None)
-- (2, 2, '杨静', '422823199411120226', '1', None, None, None)
-- (3, 3, '冯锐', '420626199602143021', '1', None, None, None)
-- (4, 4, '周玉美', '420626199412132524', '1', None, None, None)
-- (5, 5, '蔡甜甜', '420626199404061025', '1', None, None, None)
-- (6, 6, '宋稀', '510722199608207120', '1', None, None, None)
-- (7, 7, '谭玉', '422823199612270220', '1', None, None, None)
-- (8, 8, '徐明星', '422823199706120020', '1', None, None, None)
-- (9, 9, '杨玉琴', '422802200008222701', '1', None, None, None)
-- (10, 10, '洪杨尚怡', '420621199906227425', '1', None, None, None)


-- 表: dict_teacher_position_dictionary
-- 结构: [('code', 'character varying', 50), ('职务', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None)]
-- 数据条数: 5
-- 列名: ['code', '职务', 'created_at', 'updated_at']
-- ('1', '正高级', None, None)
-- ('2', '高级', None, None)
-- ('3', '中级', None, None)
-- ('4', '助理级', None, None)
-- ('5', '员级', None, None)


-- 表: education_dictionary
-- 结构: [('id', 'integer', None), ('学历类型', 'character varying', 255), ('类型名称', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50)]
-- 数据条数: 3
-- 列名: ['id', '学历类型', '类型名称', 'created_at', 'updated_at', 'import_batch']
-- (1, '1', '全日制', None, None, None)
-- (2, '2', '进修学历', None, None, None)
-- (3, '3', '提升学历', None, None, None)


-- 表: teacher_basic
-- 结构: [('id', 'integer', None), ('姓名', 'character varying', 255), ('身份证号码', 'character varying', 255), ('档案出生日期', 'date', None), ('民族', 'character varying', 255), ('籍贯', 'character varying', 255), ('联系电话', 'character varying', 255), ('参加工作日期', 'date', None), ('进入本单位日期', 'date', None), ('任职状态', 'character varying', 255), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50)]
-- 数据条数: 927
-- 列名: ['id', '姓名', '身份证号码', '档案出生日期', '民族', '籍贯', '联系电话', '参加工作日期', '进入本单位日期', '任职状态', 'created_at', 'updated_at', 'import_batch']
-- (9, '杨玉琴', '422802200008222701', None, '土家族', '恩施州恩施市', '15707279917', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (1, '李恩源', '341203199612261536', None, '汉族', '安徽省阜阳市', '17771167309', datetime.date(2018, 9, 1), datetime.date(2024, 9, 1), '在职', None, None, None)
-- (2, '杨静', '422823199411120226', None, '汉族', '巴东县溪丘湾乡', '18773772895', datetime.date(2020, 12, 1), datetime.date(2020, 12, 1), '在职', None, None, None)
-- (3, '冯锐', '420626199602143021', None, '汉族', '保康市歇马镇', '18827510528', datetime.date(2019, 9, 1), datetime.date(2019, 9, 1), '在职', None, None, None)
-- (4, '周玉美', '420626199412132524', None, '汉族', '保康县马桥镇', '13128878530', datetime.date(2021, 9, 1), datetime.date(1997, 12, 1), '在职', None, None, None)
-- (5, '蔡甜甜', '420626199404061025', None, '汉族', '保康县寺坪镇', '18772100497', datetime.date(2018, 9, 1), datetime.date(1995, 8, 1), '在职', None, None, None)
-- (6, '宋稀', '510722199608207120', None, '汉族', '恩施州巴东县', '18281904401', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (7, '谭玉', '422823199612270220', None, '土家族', '恩施州巴东县', '18807268910', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (8, '徐明星', '422823199706120020', None, '汉族', '恩施州巴东县', '18271851386', datetime.date(2023, 8, 1), datetime.date(2023, 8, 1), '在职', None, None, None)
-- (644, '刘华村', '420622194412052518', None, '汉族', '湖北枣阳', None, datetime.date(1965, 3, 1), datetime.date(1965, 3, 1), '退休', None, None, None)


-- 表: teacher_log
-- 结构: [('id', 'integer', None), ('teacher_id', 'integer', None), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50), ('name', 'character varying', 50), ('id_card', 'character varying', 18), ('position_level', 'character varying', 20), ('appointment_no', 'character varying', 50), ('start_date', 'date', None), ('confirm_date', 'date', None), ('position_level_id', 'integer', None), ('position_level_名称', 'character varying', 50), ('position_level_code', 'character varying', 30)]
-- 数据条数: 295
-- 列名: ['id', 'teacher_id', 'created_at', 'updated_at', 'import_batch', 'name', 'id_card', 'position_level', 'appointment_no', 'start_date', 'confirm_date', 'position_level_id', 'position_level_名称', 'position_level_code']
-- (1, 146, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '赵锋', '420683197509011057', '3', None, datetime.date(2006, 12, 1), None, 3, '中级', '3')
-- (2, 189, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '曹锋', '420683197510282516', '3', None, datetime.date(2006, 12, 1), None, 3, '中级', '3')
-- (3, 240, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '崔华梅', '420683198004180060', '2', None, datetime.date(2024, 5, 1), None, 2, '高级', '2')
-- (4, 330, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '崔云武', '42068319830226211X', '4', None, datetime.date(2006, 12, 1), None, 4, '助理级', '4')
-- (5, 336, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '胡玉梅', '420683198106012527', '4', None, datetime.date(2006, 12, 1), None, 4, '助理级', '4')
-- (6, 878, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '贾本平', '420622196204202533', '3', None, datetime.date(2017, 9, 1), None, 3, '中级', '3')
-- (7, 816, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '李传学', '420683196112202117', '3', None, datetime.date(2008, 2, 1), None, 3, '中级', '3')
-- (8, 404, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '马洪山', '429003197308155410', '3', None, datetime.date(2006, 12, 1), None, 3, '中级', '3')
-- (9, 315, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '孟宪清', '420683197202182548', '3', None, datetime.date(2017, 9, 1), None, 3, '中级', '3')
-- (10, 122, datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), datetime.datetime(2026, 2, 4, 11, 46, 18, 429043), None, '聂萍', '42068319761118216X', '3', None, datetime.date(2017, 9, 1), None, 3, '中级', '3')


-- 表: teacher_personal_identity
-- 结构: [('id', 'integer', None), ('teacher_id', 'integer', None), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50), ('name', 'character varying', 50), ('id_card', 'character varying', 18), ('personal_identity', 'character varying', 20), ('personal_identity_id', 'integer', None), ('personal_identity_name', 'character varying', 50), ('personal_identity_code', 'character varying', 30)]
-- 数据条数: 925
-- 列名: ['id', 'teacher_id', 'created_at', 'updated_at', 'import_batch', 'name', 'id_card', 'personal_identity', 'personal_identity_id', 'personal_identity_name', 'personal_identity_code']
-- (1, 1, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '李恩源', '341203199612261536', '1', 1, '干部', '干部')
-- (2, 2, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '杨静', '422823199411120226', '1', 1, '干部', '干部')
-- (3, 3, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '冯锐', '420626199602143021', '1', 1, '干部', '干部')
-- (4, 4, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '周玉美', '420626199412132524', '1', 1, '干部', '干部')
-- (5, 5, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '蔡甜甜', '420626199404061025', '1', 1, '干部', '干部')
-- (6, 6, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '宋稀', '510722199608207120', '1', 1, '干部', '干部')
-- (7, 7, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '谭玉', '422823199612270220', '1', 1, '干部', '干部')
-- (8, 8, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '徐明星', '422823199706120020', '1', 1, '干部', '干部')
-- (9, 9, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '杨玉琴', '422802200008222701', '1', 1, '干部', '干部')
-- (10, 10, datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), datetime.datetime(2026, 2, 4, 15, 34, 0, 562463), None, '洪杨尚怡', '420621199906227425', '1', 1, '干部', '干部')


-- 表: teacher_record
-- 结构: [('id', 'integer', None), ('teacher_id', 'integer', None), ('姓名', 'character varying', 255), ('身份证号码', 'character varying', 255), ('学历类型', 'character varying', 255), ('学历', 'character varying', 255), ('学位', 'character varying', 255), ('毕业院校', 'character varying', 255), ('专业', 'character varying', 255), ('毕业日期', 'date', None), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50)]
-- 数据条数: 860
-- 列名: ['id', 'teacher_id', '姓名', '身份证号码', '学历类型', '学历', '学位', '毕业院校', '专业', '毕业日期', 'created_at', 'updated_at', 'import_batch']
-- (23, 27, '朱素丹', '420321199205252429', '2', '6', '法学学士', '华中师范大学', '思想政治教育', datetime.date(2014, 6, 30), None, None, None)
-- (25, 257, '侯玉兰', '42060119710717174X', '2', '6', None, '湖北大学', '汉语言文学', datetime.date(2003, 6, 30), None, None, None)
-- (26, 885, '董锐', '420602196702031524', '1', '6', None, None, None, None, None, None, None)
-- (28, 148, '赵庆华', '420602197609061520', '2', '6', None, '中央广播电视大学', '数学与应用数学', datetime.date(2010, 1, 31), None, None, None)
-- (30, 226, '杨华琴', '420602197610191541', '2', '6', None, '中央广播电视大学', '汉语言文学', datetime.date(2006, 7, 31), None, None, None)
-- (32, 128, '王春艳', '420602197707201523', '2', '6', None, '湖北大学', '汉语言文学', datetime.date(2008, 6, 30), None, None, None)
-- (33, 345, '舒华', '420602197708121525', '1', '6', None, None, None, None, None, None, None)
-- (35, 121, '毛业伟', '420602197711011538', '2', '6', None, '中央广播电视大学', '数学2', datetime.date(2005, 8, 31), None, None, None)
-- (37, 86, '张峰', '42060219771115159X', '2', '6', None, '中央广播电视大学', '英语', datetime.date(2010, 6, 30), None, None, None)
-- (39, 359, '张建明', '420602197712021519', '2', '6', None, '湖北大学', '汉语言文学', datetime.date(2009, 12, 31), None, None, None)


-- 表: test
-- 结构: [('id', 'integer', None), ('name', 'character varying', None), ('value', 'character varying', None)]
-- 数据条数: 0


-- 表: test_import_table
-- 结构: [('id', 'integer', None), ('created_at', 'timestamp without time zone', None), ('updated_at', 'timestamp without time zone', None), ('import_batch', 'character varying', 50), ('name', 'character varying', 50), ('gender', 'character varying', 10), ('birth_date', 'date', None), ('age', 'integer', None)]
-- 数据条数: 2
-- 列名: ['id', 'created_at', 'updated_at', 'import_batch', 'name', 'gender', 'birth_date', 'age']
-- (1, datetime.datetime(2026, 2, 3, 23, 8, 49, 525178), datetime.datetime(2026, 2, 3, 23, 8, 49, 525178), None, '张三', '男', datetime.date(2001, 1, 1), 25)
-- (2, datetime.datetime(2026, 2, 3, 23, 8, 49, 525178), datetime.datetime(2026, 2, 3, 23, 8, 49, 525178), None, '李四', '女', datetime.date(2001, 1, 15), 26)

