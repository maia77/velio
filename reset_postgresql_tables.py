#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعادة تعيين جداول PostgreSQL
"""

import psycopg2

# إعدادات قاعدة البيانات PostgreSQL
POSTGRESQL_CONFIG = {
    'host': 'dpg-d2r155je5dus73cn11fg-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'ty_bmmw',
    'user': 'ty_bmmw_user',
    'password': 'p7wcWLN75Iqu1lkaAyveSOu7QP4TP5gu'
}

def reset_tables():
    """حذف وإعادة إنشاء الجداول"""
    conn = psycopg2.connect(**POSTGRESQL_CONFIG)
    cursor = conn.cursor()
    
    try:
        # حذف الجداول بالترتيب الصحيح
        print("🗑️ حذف الجداول الموجودة...")
        cursor.execute("DROP TABLE IF EXISTS order_status_history CASCADE")
        cursor.execute("DROP TABLE IF EXISTS product_images CASCADE")
        cursor.execute("DROP TABLE IF EXISTS comments CASCADE")
        cursor.execute("DROP TABLE IF EXISTS orders CASCADE")
        cursor.execute("DROP TABLE IF EXISTS products CASCADE")
        
        conn.commit()
        print("✅ تم حذف الجداول بنجاح")
        
    except Exception as e:
        print(f"❌ خطأ في حذف الجداول: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_tables()
