import psycopg2

def create_tables():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()
    
    # 创建 template_page_settings 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_page_settings (
            id SERIAL PRIMARY KEY,
            template_id VARCHAR(255) NOT NULL UNIQUE,
            paper_size VARCHAR(20),
            orientation VARCHAR(20),
            width_cm NUMERIC(10, 2),
            height_cm NUMERIC(10, 2),
            margin_left_cm NUMERIC(10, 2),
            margin_right_cm NUMERIC(10, 2),
            margin_top_cm NUMERIC(10, 2),
            margin_bottom_cm NUMERIC(10, 2),
            word_tables JSONB,
            excel_sheets JSONB,
            pdf_pages JSONB,
            html_structure JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建 template_placeholders 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_placeholders (
            id SERIAL PRIMARY KEY,
            template_id VARCHAR(255) NOT NULL,
            placeholder_name VARCHAR(100) NOT NULL,
            format_type VARCHAR(20),
            table_index INTEGER,
            row_index INTEGER,
            cell_index INTEGER,
            page_num INTEGER,
            x_pos NUMERIC(10, 2),
            y_pos NUMERIC(10, 2),
            css_selector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(template_id, placeholder_name)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_placeholders_template_id 
        ON template_placeholders(template_id)
    """)
    
    conn.commit()
    print('数据库表创建成功！')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    create_tables()
