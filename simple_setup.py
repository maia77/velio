#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف إعداد مبسط لقاعدة البيانات
"""

import os
import sqlite3

def create_database():
    """إنشاء قاعدة البيانات المحلية"""
    try:
        # إنشاء المجلد
        db_dir = os.path.join(os.path.dirname(__file__), 'shared_instance')
        os.makedirs(db_dir, exist_ok=True)
        
        # مسار قاعدة البيانات
        db_path = os.path.join(db_dir, 'products.db')
        
        # إنشاء الاتصال
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # إنشاء جدول المنتجات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_home_essentials BOOLEAN DEFAULT 1,
                is_new_arrival BOOLEAN DEFAULT 0
            )
        ''')
        
        # إنشاء جدول التعليقات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                name VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                rating INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_approved BOOLEAN DEFAULT 1,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ تم إنشاء قاعدة البيانات بنجاح: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إعداد قاعدة البيانات المحلية")
    print("=" * 40)
    
    success = create_database()
    
    if success:
        print("\n🎉 تم إعداد قاعدة البيانات بنجاح!")
        print("🚀 يمكنك الآن تشغيل التطبيقين")
    else:
        print("\n❌ فشل في إعداد قاعدة البيانات")

if __name__ == "__main__":
    main()

