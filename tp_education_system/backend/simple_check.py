
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg2

def check():
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='taiping_education',
        user='taiping_user',
        password='taiping_password'
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM retirement_reminder_stats")
        print("retirement_reminder_stats:", cursor.fetchone()[0])
        
        cursor.execute("SELECT COUNT(*) FROM death_registration_stats")
        print("death_registration_stats:", cursor.fetchone()[0])
        
        cursor.execute("SELECT COUNT(*) FROM octogenarian_subsidy_stats")
        print("octogenarian_subsidy_stats:", cursor.fetchone()[0])
        
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    check()
