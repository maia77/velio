#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد قاعدة بيانات PostgreSQL محلية كبديل
"""

import sqlite3
import subprocess
import os
import sys

def check_postgresql_installed():
    """فحص إذا كان PostgreSQL مثبت"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL مثبت: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL غير مثبت")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL غير مثبت")
        return False

def install_postgresql():
    """تثبيت PostgreSQL"""
    print("📦 تثبيت PostgreSQL...")
    try:
        # تثبيت PostgreSQL باستخدام Homebrew
        subprocess.run(['brew', 'install', 'postgresql'], check=True)
        print("✅ تم تثبيت PostgreSQL بنجاح")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت PostgreSQL")
        return False
    except FileNotFoundError:
        print("❌ Homebrew غير مثبت. يرجى تثبيت PostgreSQL يدوياً")
        return False

def create_local_database():
    """إنشاء قاعدة بيانات محلية"""
    print("🗄️ إنشاء قاعدة بيانات محلية...")
    
    # إعدادات قاعدة البيانات المحلية
    local_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'velio_local',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=local_config['host'],
            port=local_config['port'],
            user=local_config['user'],
            password=local_config['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # إنشاء قاعدة البيانات
        cursor.execute(f"CREATE DATABASE {local_config['database']}")
        print(f"✅ تم إنشاء قاعدة البيانات: {local_config['database']}")
        
        conn.close()
        return local_config
        
    except Exception as e:
        print(f"❌ فشل في إنشاء قاعدة البيانات: {str(e)}")
        return None

def migrate_from_sqlite(local_config):
    """نقل البيانات من SQLite إلى PostgreSQL المحلي"""
    print("📦 نقل البيانات من SQLite إلى PostgreSQL المحلي...")
    
    # استخراج البيانات من SQLite
    sqlite_conn = sqlite3.connect('shared_instance/products.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # استخراج المنتجات
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM orders")
    orders = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM product_images")
    images = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM order_status_history")
    status_history = [dict(row) for row in cursor.fetchall()]
    
    sqlite_conn.close()
    
    # نقل البيانات إلى PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(**local_config)
        cursor = conn.cursor()
        
        # إنشاء الجداول
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(100),
                stock_quantity INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                image_path VARCHAR(500) NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                customer_phone VARCHAR(20) NOT NULL,
                customer_email VARCHAR(255),
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_status_history (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                status VARCHAR(50) NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # نقل المنتجات
        for product in products:
            cursor.execute("""
                INSERT INTO products (id, name, description, price, category, stock_quantity, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                product['id'], product['name'], product['description'], 
                product['price'], product['category'], product['stock_quantity'],
                product['is_active'], product['created_at'], product['updated_at']
            ))
        
        # نقل الصور
        for image in images:
            cursor.execute("""
                INSERT INTO product_images (id, product_id, image_path, is_primary, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                image['id'], image['product_id'], image['image_path'],
                image['is_primary'], image['created_at']
            ))
        
        # نقل الطلبات
        for order in orders:
            cursor.execute("""
                INSERT INTO orders (id, order_number, customer_name, customer_phone, customer_email, 
                                 total_amount, status, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                order['id'], order['order_number'], order['customer_name'],
                order['customer_phone'], order['customer_email'], order['total_amount'],
                order['status'], order['notes'], order['created_at'], order['updated_at']
            ))
        
        # نقل تاريخ الحالة
        for status in status_history:
            cursor.execute("""
                INSERT INTO order_status_history (id, order_id, status, notes, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                status['id'], status['order_id'], status['status'],
                status['notes'], status['created_at']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ تم نقل البيانات بنجاح!")
        print(f"   المنتجات: {len(products)}")
        print(f"   الطلبات: {len(orders)}")
        print(f"   الصور: {len(images)}")
        print(f"   تاريخ الحالة: {len(status_history)}")
        
        return True
        
    except Exception as e:
        print(f"❌ فشل في نقل البيانات: {str(e)}")
        return False

def main():
    print("🚀 إعداد قاعدة بيانات PostgreSQL محلية...")
    print("=" * 50)
    
    # فحص PostgreSQL
    if not check_postgresql_installed():
        print("📦 محاولة تثبيت PostgreSQL...")
        if not install_postgresql():
            print("❌ لا يمكن المتابعة بدون PostgreSQL")
            return False
    
    # إنشاء قاعدة البيانات
    local_config = create_local_database()
    if not local_config:
        print("❌ فشل في إنشاء قاعدة البيانات المحلية")
        return False
    
    # نقل البيانات
    if migrate_from_sqlite(local_config):
        print("\n🎉 تم إعداد قاعدة البيانات المحلية بنجاح!")
        print(f"📊 إعدادات قاعدة البيانات:")
        print(f"   Host: {local_config['host']}")
        print(f"   Port: {local_config['port']}")
        print(f"   Database: {local_config['database']}")
        print(f"   User: {local_config['user']}")
        print(f"   Password: {local_config['password']}")
        return True
    else:
        print("❌ فشل في نقل البيانات")
        return False

if __name__ == "__main__":
    main()
