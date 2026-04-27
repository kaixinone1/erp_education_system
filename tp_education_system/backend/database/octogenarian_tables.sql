-- 高龄老人补贴信息表
CREATE TABLE IF NOT EXISTS 高龄老人补贴信息 (
    id SERIAL PRIMARY KEY,
    序号 INTEGER,
    姓名 VARCHAR(50) NOT NULL,
    性别 VARCHAR(10),
    身份证号码 VARCHAR(18) UNIQUE NOT NULL,
    退休单位 VARCHAR(100),
    户籍地 VARCHAR(200),
    现住址 VARCHAR(200),
    银行账号 VARCHAR(50),
    开户行 VARCHAR(100),
    本人联系电话 VARCHAR(20),
    代理人姓名 VARCHAR(50),
    与本人关系 VARCHAR(20),
    代理人联系电话 VARCHAR(20),
    备注 TEXT,
    状态 VARCHAR(20) DEFAULT '创建' CHECK (状态 IN ('创建', '死亡')),
    信息来源 VARCHAR(20) DEFAULT '手动录入' CHECK (信息来源 IN ('自动导入', '手动录入')),
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    更新时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_高龄老人补贴信息_身份证号码 ON 高龄老人补贴信息(身份证号码);
CREATE INDEX IF NOT EXISTS idx_高龄老人补贴信息_状态 ON 高龄老人补贴信息(状态);

-- 死亡登记信息表
CREATE TABLE IF NOT EXISTS 死亡登记信息 (
    id SERIAL PRIMARY KEY,
    序号 INTEGER,
    姓名 VARCHAR(50) NOT NULL,
    性别 VARCHAR(10),
    身份证号码 VARCHAR(18) NOT NULL,
    退休单位 VARCHAR(100),
    户籍地 VARCHAR(200),
    现住址 VARCHAR(200),
    银行账号 VARCHAR(50),
    开户行 VARCHAR(100),
    本人联系电话 VARCHAR(20),
    代理人姓名 VARCHAR(50),
    与本人关系 VARCHAR(20),
    代理人联系电话 VARCHAR(20),
    死亡日期 DATE NOT NULL,
    死亡原因 VARCHAR(200),
    备注 TEXT,
    原记录ID INTEGER,
    登记人 VARCHAR(50),
    登记时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_死亡登记信息_身份证号码 ON 死亡登记信息(身份证号码);
CREATE INDEX IF NOT EXISTS idx_死亡登记信息_死亡日期 ON 死亡登记信息(死亡日期);

-- 高龄提醒记录表
CREATE TABLE IF NOT EXISTS 高龄提醒记录 (
    id SERIAL PRIMARY KEY,
    教师ID INTEGER,
    教师姓名 VARCHAR(50) NOT NULL,
    身份证号码 VARCHAR(18) NOT NULL,
    出生日期 DATE,
    年满80周岁日期 DATE NOT NULL,
    提醒日期 DATE NOT NULL,
    状态 VARCHAR(20) DEFAULT '待处理' CHECK (状态 IN ('待处理', '处理中', '已完成')),
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    完成时间 TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_高龄提醒记录_身份证号码 ON 高龄提醒记录(身份证号码);
CREATE INDEX IF NOT EXISTS idx_高龄提醒记录_状态 ON 高龄提醒记录(状态);
CREATE INDEX IF NOT EXISTS idx_高龄提醒记录_提醒日期 ON 高龄提醒记录(提醒日期);

-- 高龄提醒处理记录表
CREATE TABLE IF NOT EXISTS 高龄提醒处理记录 (
    id SERIAL PRIMARY KEY,
    提醒ID INTEGER REFERENCES 高龄提醒记录(id) ON DELETE CASCADE,
    选项1_已通知家属 BOOLEAN DEFAULT FALSE,
    选项2_已收到申请表 BOOLEAN DEFAULT FALSE,
    选项3_已上报 BOOLEAN DEFAULT FALSE,
    选项4_已批准 BOOLEAN DEFAULT FALSE,
    完成进度 INTEGER DEFAULT 0 CHECK (完成进度 >= 0 AND 完成进度 <= 100),
    操作人 VARCHAR(50),
    操作时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    备注 TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_高龄提醒处理记录_提醒ID ON 高龄提醒处理记录(提醒ID);

-- 添加表注释
COMMENT ON TABLE 高龄老人补贴信息 IS '存储80周岁以上高龄老人补贴申请信息';
COMMENT ON TABLE 死亡登记信息 IS '存储已死亡的高龄老人信息';
COMMENT ON TABLE 高龄提醒记录 IS '存储即将满80周岁教师的提醒记录';
COMMENT ON TABLE 高龄提醒处理记录 IS '存储高龄提醒的处理进度记录';
