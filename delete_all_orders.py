#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت حذف جميع الطلبات من قاعدة البيانات
يدعم SQLite و PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from datetime import datetime

def detect_database_type():
    """تحديد نوع قاعدة البيانات المستخدمة"""
    # فحص متغير البيئة أولاً
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
            return 'postgresql', database_url
        elif database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
            return 'sqlite', db_path
    
    # فحص الملفات المحلية
    possible_paths = [
        'shared_instance/products.db',
        'web/instance/products.db',
        'instance/products.db',
        'products.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return 'sqlite', path
    
    return None, None

def connect_to_database(db_type, db_path):
    """الاتصال بقاعدة البيانات"""
    try:
        if db_type == 'sqlite':
            conn = sqlite3.connect(db_path)
            print(f"✅ تم الاتصال بقاعدة البيانات SQLite: {db_path}")
            return conn
        elif db_type == 'postgresql':
            conn = psycopg2.connect(db_path)
            print(f"✅ تم الاتصال بقاعدة البيانات PostgreSQL")
            return conn
        else:
            print("❌ نوع قاعدة البيانات غير مدعوم")
            return None
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return None

def get_orders_count(conn, db_type):
    """الحصول على عدد الطلبات"""
    try:
        cursor = conn.cursor()
        if db_type == 'sqlite':
            cursor.execute("SELECT COUNT(*) FROM orders")
        else:
            cursor.execute("SELECT COUNT(*) FROM orders")
        
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"❌ خطأ في الحصول على عدد الطلبات: {e}")
        return 0

def delete_all_orders(conn, db_type):
    """حذف جميع الطلبات"""
    try:
        cursor = conn.cursor()
        
        # حذف تاريخ حالة الطلبات أولاً (لأنه مرتبط بالطلبات)
        if db_type == 'sqlite':
            cursor.execute("DELETE FROM order_status_history")
        else:
            cursor.execute("DELETE FROM order_status_history")
        
        print("✅ تم حذف تاريخ حالة الطلبات")
        
        # حذف جميع الطلبات
        if db_type == 'sqlite':
            cursor.execute("DELETE FROM orders")
        else:
            cursor.execute("DELETE FROM orders")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حذف جميع الطلبات بنجاح!")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في حذف الطلبات: {e}")
        conn.rollback()
        return False

def main():
    """الدالة الرئيسية"""
    print("🗑️ سكريبت حذف جميع الطلبات")
    print("=" * 50)
    
    # تحديد نوع قاعدة البيانات
    db_type, db_path = detect_database_type()
    
    if not db_type:
        print("❌ لم يتم العثور على قاعدة بيانات")
        print("تأكد من وجود ملف products.db أو متغير DATABASE_URL")
        return
    
    print(f"📊 نوع قاعدة البيانات: {db_type}")
    print(f"📁 مسار قاعدة البيانات: {db_path}")
    
    # الاتصال بقاعدة البيانات
    conn = connect_to_database(db_type, db_path)
    if not conn:
        return
    
    try:
        # الحصول على عدد الطلبات الحالي
        orders_count = get_orders_count(conn, db_type)
        print(f"📋 عدد الطلبات الحالي: {orders_count}")
        
        if orders_count == 0:
            print("ℹ️ لا توجد طلبات لحذفها")
            return
        
        # تأكيد الحذف
        print("\n⚠️ تحذير: سيتم حذف جميع الطلبات نهائياً!")
        confirm = input("هل أنت متأكد؟ اكتب 'نعم' للمتابعة: ")
        
        if confirm.strip() != 'نعم':
            print("❌ تم إلغاء العملية")
            return
        
        # حذف الطلبات
        print("\n🗑️ بدء حذف الطلبات...")
        success = delete_all_orders(conn, db_type)
        
        if success:
            # التحقق من النتيجة
            new_count = get_orders_count(conn, db_type)
            print(f"🎉 تم حذف {orders_count} طلب بنجاح!")
            print(f"📋 عدد الطلبات المتبقي: {new_count}")
        else:
            print("❌ فشل في حذف الطلبات")
    
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
    
    finally:
        conn.close()
        print("🔌 تم إغلاق الاتصال بقاعدة البيانات")

if __name__ == "__main__":
    main()
