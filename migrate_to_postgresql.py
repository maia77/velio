#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت نقل البيانات من SQLite إلى PostgreSQL
"""

import sqlite3
import psycopg2
import os
from datetime import datetime

# إعدادات قاعدة البيانات المحلية
SQLITE_DB = 'shared_instance/products.db'

# إعدادات قاعدة البيانات PostgreSQL
POSTGRESQL_CONFIG = {
    'host': 'dpg-d2r155je5dus73cn11fg-a.oregon-postgres.render.com',
    'port': '5432',
    'database': 'ty_bmmw',
    'user': 'ty_bmmw_user',
    'password': 'p7wcWLN75Iqu1lkaAyveSOu7QP4TP5gu'
}

def test_postgresql_connection():
    """اختبار الاتصال بقاعدة البيانات PostgreSQL"""
    try:
        conn = psycopg2.connect(**POSTGRESQL_CONFIG)
        conn.close()
        return True, "تم الاتصال بنجاح"
    except Exception as e:
        return False, f"فشل الاتصال: {str(e)}"

def get_sqlite_data():
    """استخراج البيانات من SQLite"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {}
    
    # استخراج المنتجات
    cursor.execute("SELECT * FROM products")
    data['products'] = [dict(row) for row in cursor.fetchall()]
    
    # استخراج الطلبات
    cursor.execute("SELECT * FROM orders")
    data['orders'] = [dict(row) for row in cursor.fetchall()]
    
    # استخراج صور المنتجات
    cursor.execute("SELECT * FROM product_images")
    data['product_images'] = [dict(row) for row in cursor.fetchall()]
    
    # استخراج تاريخ حالة الطلبات
    cursor.execute("SELECT * FROM order_status_history")
    data['order_status_history'] = [dict(row) for row in cursor.fetchall()]
    
    # استخراج التعليقات
    cursor.execute("SELECT * FROM comments")
    data['comments'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return data

def create_postgresql_tables():
    """إنشاء الجداول في PostgreSQL"""
    conn = psycopg2.connect(**POSTGRESQL_CONFIG)
    cursor = conn.cursor()
    
    # إنشاء جدول المنتجات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            name_ar VARCHAR(200),
            description TEXT NOT NULL,
            description_ar TEXT,
            price FLOAT NOT NULL,
            category VARCHAR(100),
            category_ar VARCHAR(100),
            brand VARCHAR(100),
            brand_ar VARCHAR(100),
            image_url VARCHAR(500),
            main_category VARCHAR(100) DEFAULT 'أصالة معاصرة',
            main_category_ar VARCHAR(100) DEFAULT 'أصالة معاصرة',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            is_home_essentials BOOLEAN DEFAULT TRUE,
            is_new_arrival BOOLEAN DEFAULT FALSE
        )
    """)
    
    # إنشاء جدول صور المنتجات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            image_url VARCHAR(500) NOT NULL,
            alt_text VARCHAR(200),
            is_primary BOOLEAN DEFAULT FALSE,
            sort_order INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # إنشاء جدول الطلبات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number VARCHAR(50) UNIQUE NOT NULL,
            product_id INTEGER REFERENCES products(id),
            product_name VARCHAR(200) NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price FLOAT NOT NULL,
            total_price FLOAT NOT NULL,
            customer_name VARCHAR(100) NOT NULL,
            customer_email VARCHAR(100),
            customer_phone VARCHAR(20),
            customer_address TEXT,
            customer_country VARCHAR(50),
            payment_method VARCHAR(50),
            status VARCHAR(20) NOT NULL,
            status_ar VARCHAR(50),
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            processed_at TIMESTAMP,
            completed_at TIMESTAMP,
            admin_notes TEXT,
            rejection_reason TEXT
        )
    """)
    
    # إنشاء جدول تاريخ حالة الطلبات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_status_history (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            old_status VARCHAR(20),
            new_status VARCHAR(20) NOT NULL,
            changed_by VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # إنشاء جدول التعليقات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            customer_name VARCHAR(255) NOT NULL,
            comment_text TEXT NOT NULL,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            is_approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء الجداول في PostgreSQL")

def migrate_data():
    """نقل البيانات من SQLite إلى PostgreSQL"""
    # اختبار الاتصال
    success, message = test_postgresql_connection()
    if not success:
        print(f"❌ فشل الاتصال بقاعدة البيانات: {message}")
        return False
    
    print("✅ تم الاتصال بقاعدة البيانات PostgreSQL")
    
    # إنشاء الجداول
    create_postgresql_tables()
    
    # استخراج البيانات
    print("📥 استخراج البيانات من SQLite...")
    data = get_sqlite_data()
    
    # نقل البيانات
    conn = psycopg2.connect(**POSTGRESQL_CONFIG)
    cursor = conn.cursor()
    
    try:
        # نقل المنتجات
        print(f"📦 نقل {len(data['products'])} منتج...")
        for product in data['products']:
            cursor.execute("""
                INSERT INTO products (id, name, name_ar, description, description_ar, price, category, category_ar, 
                                   brand, brand_ar, image_url, main_category, main_category_ar, 
                                   created_at, updated_at, is_active, is_home_essentials, is_new_arrival)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                product['id'], product['name'], product.get('name_ar'), 
                product['description'], product.get('description_ar'),
                product['price'], product.get('category'), product.get('category_ar'),
                product.get('brand'), product.get('brand_ar'), product.get('image_url'),
                product.get('main_category', 'أصالة معاصرة'), product.get('main_category_ar', 'أصالة معاصرة'),
                product['created_at'], product['updated_at'], 
                bool(product['is_active']), bool(product.get('is_home_essentials', True)), bool(product.get('is_new_arrival', False))
            ))
        
        # نقل صور المنتجات
        print(f"🖼️ نقل {len(data['product_images'])} صورة...")
        for image in data['product_images']:
            cursor.execute("""
                INSERT INTO product_images (id, product_id, image_url, alt_text, is_primary, sort_order, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                image['id'], image['product_id'], image['image_url'],
                image.get('alt_text'), bool(image['is_primary']), 
                image.get('sort_order'), image['created_at']
            ))
        
        # نقل الطلبات
        print(f"🛒 نقل {len(data['orders'])} طلب...")
        for order in data['orders']:
            cursor.execute("""
                INSERT INTO orders (id, order_number, product_id, product_name, quantity, unit_price, total_price,
                                 customer_name, customer_email, customer_phone, customer_address, customer_country,
                                 payment_method, status, status_ar, created_at, updated_at, processed_at, completed_at,
                                 admin_notes, rejection_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                order['id'], order['order_number'], order['product_id'], order['product_name'],
                order['quantity'], order['unit_price'], order['total_price'],
                order['customer_name'], order.get('customer_email'), order.get('customer_phone'),
                order.get('customer_address'), order.get('customer_country'), order.get('payment_method'),
                order['status'], order.get('status_ar'), order['created_at'], order['updated_at'],
                order.get('processed_at'), order.get('completed_at'), order.get('admin_notes'), order.get('rejection_reason')
            ))
        
        # نقل تاريخ حالة الطلبات
        print(f"📋 نقل {len(data['order_status_history'])} سجل حالة...")
        for status in data['order_status_history']:
            cursor.execute("""
                INSERT INTO order_status_history (id, order_id, old_status, new_status, changed_by, notes, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                status['id'], status['order_id'], status.get('old_status'),
                status['new_status'], status.get('changed_by'), status.get('notes'), status['created_at']
            ))
        
        # نقل التعليقات
        print(f"💬 نقل {len(data['comments'])} تعليق...")
        for comment in data['comments']:
            cursor.execute("""
                INSERT INTO comments (id, product_id, customer_name, comment_text, rating, is_approved, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                comment['id'], comment['product_id'], comment['customer_name'],
                comment['comment_text'], comment['rating'], comment['is_approved'], comment['created_at']
            ))
        
        conn.commit()
        print("✅ تم نقل جميع البيانات بنجاح!")
        
        # عرض إحصائيات
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM product_images")
        images_count = cursor.fetchone()[0]
        
        print(f"\n📊 إحصائيات قاعدة البيانات الجديدة:")
        print(f"   المنتجات: {products_count}")
        print(f"   الطلبات: {orders_count}")
        print(f"   الصور: {images_count}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ خطأ في نقل البيانات: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 بدء عملية نقل البيانات من SQLite إلى PostgreSQL...")
    print("=" * 60)
    
    success = migrate_data()
    
    if success:
        print("\n🎉 تم نقل البيانات بنجاح!")
        print("يمكنك الآن استخدام قاعدة البيانات الخارجية")
    else:
        print("\n❌ فشل في نقل البيانات")
        print("سيستمر النظام في استخدام قاعدة البيانات المحلية")
