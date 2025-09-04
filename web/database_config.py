#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف تكوين قاعدة البيانات المشتركة
يحتوي على إعدادات قاعدة البيانات PostgreSQL على Render
"""

import os

# إعدادات قاعدة البيانات PostgreSQL على Render
DATABASE_CONFIG = {
    'host': 'dpg-d2r155je5dus73cn11fg-a',
    'port': '5432',
    'database': 'ty_bmmw',
    'username': 'ty_bmmw_user',
    'password': os.environ.get('DB_PASSWORD', '')
}

# رابط الاتصال بقاعدة البيانات
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# إعدادات Flask-SQLAlchemy
SQLALCHEMY_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': DATABASE_URL,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'velio_app'
        }
    }
}

def get_database_config():
    """إرجاع إعدادات قاعدة البيانات"""
    return SQLALCHEMY_CONFIG

def get_database_url():
    """إرجاع رابط قاعدة البيانات"""
    return DATABASE_URL

def test_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['username'],
            password=DATABASE_CONFIG['password']
        )
        conn.close()
        return True, "تم الاتصال بنجاح"
    except Exception as e:
        return False, f"فشل الاتصال: {str(e)}"

if __name__ == "__main__":
    # اختبار الاتصال عند تشغيل الملف مباشرة
    success, message = test_connection()
    print(f"اختبار الاتصال: {'✅' if success else '❌'} {message}")
