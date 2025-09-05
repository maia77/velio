#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف تكوين قاعدة البيانات مع نظام احتياطي
يحاول الاتصال بـ PostgreSQL أولاً، ثم ينتقل لـ SQLite في حالة الفشل
"""

import os

# إعدادات قاعدة البيانات PostgreSQL على Render
POSTGRESQL_CONFIG = {
    'host': 'dpg-d2r155je5dus73cn11fg-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'ty_bmmw',
    'user': 'ty_bmmw_user',
    'password': 'p7wcWLN75Iqu1lkaAyveSOu7QP4TP5gu'
}

# إعدادات قاعدة البيانات المحلية (SQLite) كاحتياطي
LOCAL_DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'shared_instance', 'products.db')
LOCAL_DATABASE_URL = f"sqlite:///{LOCAL_DATABASE_PATH}"

# رابط الاتصال بقاعدة البيانات PostgreSQL
POSTGRESQL_URL = f"postgresql://{POSTGRESQL_CONFIG['user']}:{POSTGRESQL_CONFIG['password']}@{POSTGRESQL_CONFIG['host']}:{POSTGRESQL_CONFIG['port']}/{POSTGRESQL_CONFIG['database']}"

# إعدادات Flask-SQLAlchemy
POSTGRESQL_SQLALCHEMY_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': POSTGRESQL_URL,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'velio_shared_app'
        }
    }
}

LOCAL_SQLALCHEMY_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': LOCAL_DATABASE_URL,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}

def test_postgresql_connection():
    """اختبار الاتصال بقاعدة البيانات PostgreSQL"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=POSTGRESQL_CONFIG['host'],
            port=POSTGRESQL_CONFIG['port'],
            database=POSTGRESQL_CONFIG['database'],
            user=POSTGRESQL_CONFIG['user'],
            password=POSTGRESQL_CONFIG['password']
        )
        conn.close()
        return True, "تم الاتصال بقاعدة البيانات PostgreSQL بنجاح"
    except Exception as e:
        return False, f"فشل الاتصال بقاعدة البيانات PostgreSQL: {str(e)}"

def test_sqlite_connection():
    """اختبار الاتصال بقاعدة البيانات SQLite"""
    try:
        import sqlite3
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(LOCAL_DATABASE_PATH), exist_ok=True)
        conn = sqlite3.connect(LOCAL_DATABASE_PATH)
        conn.close()
        return True, "تم الاتصال بقاعدة البيانات SQLite بنجاح"
    except Exception as e:
        return False, f"فشل الاتصال بقاعدة البيانات SQLite: {str(e)}"

def get_database_config():
    """إرجاع إعدادات قاعدة البيانات مع نظام احتياطي"""
    # محاولة الاتصال بـ PostgreSQL أولاً
    success, message = test_postgresql_connection()
    if success:
        print("🌐 استخدام قاعدة البيانات PostgreSQL على Render")
        return POSTGRESQL_SQLALCHEMY_CONFIG, True
    else:
        print(f"⚠️ فشل الاتصال بـ PostgreSQL: {message}")
        print("💾 استخدام قاعدة البيانات المحلية SQLite كاحتياطي")
        return LOCAL_SQLALCHEMY_CONFIG, False

def get_database_url():
    """إرجاع رابط قاعدة البيانات مع نظام احتياطي"""
    success, _ = test_postgresql_connection()
    if success:
        return POSTGRESQL_URL
    else:
        return LOCAL_DATABASE_URL

def test_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    # محاولة PostgreSQL أولاً
    success, message = test_postgresql_connection()
    if success:
        return True, message
    
    # في حالة الفشل، جرب SQLite
    success, message = test_sqlite_connection()
    if success:
        return True, f"PostgreSQL غير متاح، {message}"
    
    return False, "فشل الاتصال بجميع قواعد البيانات"

if __name__ == "__main__":
    # اختبار الاتصال عند تشغيل الملف مباشرة
    print("🔍 اختبار الاتصال بقاعدة البيانات...")
    print("=" * 50)
    
    # اختبار PostgreSQL
    success, message = test_postgresql_connection()
    print(f"🌐 PostgreSQL: {'✅' if success else '❌'} {message}")
    
    # اختبار SQLite
    success, message = test_sqlite_connection()
    print(f"💾 SQLite: {'✅' if success else '❌'} {message}")
    
    # اختيار قاعدة البيانات
    config, is_postgresql = get_database_config()
    database_type = "PostgreSQL" if is_postgresql else "SQLite"
    print(f"🎯 تم اختيار: {database_type}")
