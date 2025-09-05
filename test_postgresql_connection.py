#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار الاتصال بقاعدة البيانات PostgreSQL
"""

import psycopg2
import os

# إعدادات قاعدة البيانات PostgreSQL
POSTGRESQL_CONFIG = {
    'host': 'dpg-d2r155je5dus73cn11fg-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'ty_bmmw',
    'user': 'ty_bmmw_user',
    'password': 'p7wcWLN75Iqu1lkaAyveSOu7QP4TP5gu'
}

def test_connection():
    """اختبار الاتصال بقاعدة البيانات PostgreSQL"""
    print("🔍 اختبار الاتصال بقاعدة البيانات PostgreSQL...")
    print(f"Host: {POSTGRESQL_CONFIG['host']}")
    print(f"Port: {POSTGRESQL_CONFIG['port']}")
    print(f"Database: {POSTGRESQL_CONFIG['database']}")
    print(f"User: {POSTGRESQL_CONFIG['user']}")
    print(f"Password: {'***' if POSTGRESQL_CONFIG['password'] else 'غير محدد'}")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**POSTGRESQL_CONFIG)
        cursor = conn.cursor()
        
        # اختبار بسيط
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ تم الاتصال بنجاح!")
        print(f"PostgreSQL Version: {version}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ فشل الاتصال: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if not success:
        print("\n💡 نصائح لحل المشكلة:")
        print("1. تأكد من تعيين كلمة مرور قاعدة البيانات:")
        print("   export DB_PASSWORD='your_password'")
        print("2. تحقق من اتصال الإنترنت")
        print("3. تحقق من إعدادات Render")
