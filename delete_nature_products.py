#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لحذف منتجات زينة الطبيعة من قاعدة البيانات
"""

import os
import sys
import sqlite3
import psycopg2
from datetime import datetime

def get_database_connection():
    """الحصول على اتصال قاعدة البيانات"""
    try:
        # محاولة الاتصال بقاعدة البيانات المحلية SQLite أولاً
        db_path = os.path.join(os.path.dirname(__file__), 'shared_instance', 'products.db')
        if os.path.exists(db_path):
            print(f"🔍 تم العثور على قاعدة البيانات المحلية: {db_path}")
            return sqlite3.connect(db_path), 'sqlite'
        
        # محاولة الاتصال بقاعدة البيانات PostgreSQL
        try:
            from shared_database_config_fallback import POSTGRESQL_CONFIG as DATABASE_CONFIG
            conn = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password']
            )
            print("🔍 تم الاتصال بقاعدة البيانات PostgreSQL")
            return conn, 'postgresql'
        except Exception as e:
            print(f"⚠️ فشل الاتصال بقاعدة البيانات PostgreSQL: {e}")
            
        # محاولة الاتصال بقاعدة البيانات في مجلد web
        web_db_path = os.path.join(os.path.dirname(__file__), 'web', 'instance', 'products.db')
        if os.path.exists(web_db_path):
            print(f"🔍 تم العثور على قاعدة البيانات في مجلد web: {web_db_path}")
            return sqlite3.connect(web_db_path), 'sqlite'
            
        raise Exception("لم يتم العثور على قاعدة بيانات")
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return None, None

def find_nature_products(conn, db_type):
    """البحث عن منتجات زينة الطبيعة"""
    try:
        cursor = conn.cursor()
        
        if db_type == 'sqlite':
            # البحث في SQLite
            query = """
            SELECT id, name, name_ar, main_category, main_category_ar, category, category_ar, price
            FROM products 
            WHERE main_category = 'زينة الطبيعة' 
               OR main_category_ar = 'زينة الطبيعة'
               OR category = 'زينة الطبيعة'
               OR category_ar = 'زينة الطبيعة'
            """
        else:
            # البحث في PostgreSQL
            query = """
            SELECT id, name, name_ar, main_category, main_category_ar, category, category_ar, price
            FROM products 
            WHERE main_category = 'زينة الطبيعة' 
               OR main_category_ar = 'زينة الطبيعة'
               OR category = 'زينة الطبيعة'
               OR category_ar = 'زينة الطبيعة'
            """
        
        cursor.execute(query)
        products = cursor.fetchall()
        
        print(f"🌿 تم العثور على {len(products)} منتج في قسم زينة الطبيعة:")
        print("-" * 80)
        
        for product in products:
            product_id, name, name_ar, main_cat, main_cat_ar, cat, cat_ar, price = product
            print(f"ID: {product_id}")
            print(f"الاسم: {name}")
            if name_ar:
                print(f"الاسم العربي: {name_ar}")
            print(f"القسم الرئيسي: {main_cat}")
            if main_cat_ar:
                print(f"القسم الرئيسي العربي: {main_cat_ar}")
            print(f"القسم: {cat}")
            if cat_ar:
                print(f"القسم العربي: {cat_ar}")
            print(f"السعر: {price}")
            print("-" * 40)
        
        return products
        
    except Exception as e:
        print(f"❌ خطأ في البحث عن المنتجات: {e}")
        return []

def delete_nature_products(conn, db_type, products):
    """حذف منتجات زينة الطبيعة"""
    if not products:
        print("ℹ️ لا توجد منتجات لحذفها")
        return 0
    
    try:
        cursor = conn.cursor()
        deleted_count = 0
        
        print(f"🗑️ بدء حذف {len(products)} منتج...")
        
        for product in products:
            product_id = product[0]
            
            # حذف الصور المرتبطة بالمنتج أولاً
            if db_type == 'sqlite':
                cursor.execute("DELETE FROM product_images WHERE product_id = ?", (product_id,))
            else:
                cursor.execute("DELETE FROM product_images WHERE product_id = %s", (product_id,))
            
            # حذف التعليقات المرتبطة بالمنتج
            if db_type == 'sqlite':
                cursor.execute("DELETE FROM comments WHERE product_id = ?", (product_id,))
            else:
                cursor.execute("DELETE FROM comments WHERE product_id = %s", (product_id,))
            
            # حذف الطلبات المرتبطة بالمنتج
            if db_type == 'sqlite':
                cursor.execute("DELETE FROM orders WHERE product_id = ?", (product_id,))
            else:
                cursor.execute("DELETE FROM orders WHERE product_id = %s", (product_id,))
            
            # حذف المنتج نفسه
            if db_type == 'sqlite':
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            else:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            
            deleted_count += 1
            print(f"✅ تم حذف المنتج ID: {product_id}")
        
        # حفظ التغييرات
        conn.commit()
        print(f"🎉 تم حذف {deleted_count} منتج بنجاح!")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ خطأ في حذف المنتجات: {e}")
        conn.rollback()
        return 0

def main():
    """الدالة الرئيسية"""
    print("🌿 سكريبت حذف منتجات زينة الطبيعة")
    print("=" * 50)
    
    # الاتصال بقاعدة البيانات
    conn, db_type = get_database_connection()
    if not conn:
        print("❌ فشل في الاتصال بقاعدة البيانات")
        return
    
    try:
        # البحث عن المنتجات
        products = find_nature_products(conn, db_type)
        
        if not products:
            print("ℹ️ لا توجد منتجات في قسم زينة الطبيعة")
            return
        
        # تأكيد الحذف
        print(f"\n⚠️ هل تريد حذف {len(products)} منتج من قسم زينة الطبيعة؟")
        confirm = input("اكتب 'نعم' للتأكيد: ").strip()
        
        if confirm.lower() in ['نعم', 'yes', 'y']:
            deleted_count = delete_nature_products(conn, db_type, products)
            
            if deleted_count > 0:
                print(f"\n✅ تم حذف {deleted_count} منتج بنجاح!")
                print("🔄 يرجى إعادة تشغيل التطبيق لرؤية التغييرات")
            else:
                print("\n❌ فشل في حذف المنتجات")
        else:
            print("❌ تم إلغاء العملية")
    
    except Exception as e:
        print(f"❌ خطأ عام: {e}")
    
    finally:
        conn.close()
        print("🔌 تم إغلاق الاتصال بقاعدة البيانات")

if __name__ == "__main__":
    main()
