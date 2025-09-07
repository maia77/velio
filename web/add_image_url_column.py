#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لإضافة عمود image_url لجدول التعليقات في PostgreSQL
"""

import sys
import os

# إضافة مسار التطبيق
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from shared_database_config_fallback import POSTGRESQL_CONFIG
import psycopg2

def add_image_url_column():
    """إضافة عمود image_url لجدول التعليقات"""
    try:
        print("🔧 إضافة عمود image_url لجدول التعليقات...")
        print("=" * 50)
        
        # الاتصال بقاعدة البيانات PostgreSQL
        conn = psycopg2.connect(
            host=POSTGRESQL_CONFIG['host'],
            port=POSTGRESQL_CONFIG['port'],
            database=POSTGRESQL_CONFIG['database'],
            user=POSTGRESQL_CONFIG['user'],
            password=POSTGRESQL_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # التحقق من وجود العمود
        print("🔍 التحقق من وجود عمود image_url...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'comments' AND column_name = 'image_url'
        """)
        
        if cursor.fetchone():
            print("✅ عمود image_url موجود بالفعل")
            return True
        
        # إضافة العمود
        print("➕ إضافة عمود image_url...")
        cursor.execute("""
            ALTER TABLE comments 
            ADD COLUMN image_url VARCHAR(500)
        """)
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم إضافة عمود image_url بنجاح")
        
        # التحقق من النتيجة
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'comments'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n📋 أعمدة جدول التعليقات:")
        for col in columns:
            print(f"   - {col[0]} ({col[1]}{f'({col[2]})' if col[2] else ''})")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إضافة العمود: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_comments_table():
    """التحقق من صحة جدول التعليقات"""
    try:
        print("\n🧪 التحقق من صحة جدول التعليقات...")
        print("=" * 40)
        
        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=POSTGRESQL_CONFIG['host'],
            port=POSTGRESQL_CONFIG['port'],
            database=POSTGRESQL_CONFIG['database'],
            user=POSTGRESQL_CONFIG['user'],
            password=POSTGRESQL_CONFIG['password']
        )
        
        cursor = conn.cursor()
        
        # اختبار إدراج تعليق تجريبي
        print("📝 اختبار إدراج تعليق تجريبي...")
        cursor.execute("""
            INSERT INTO comments (product_id, customer_name, comment_text, rating, image_url, created_at, is_approved)
            VALUES (1, 'مستخدم تجريبي', 'تعليق تجريبي', 5, NULL, NOW(), true)
            RETURNING id
        """)
        
        comment_id = cursor.fetchone()[0]
        print(f"✅ تم إنشاء تعليق تجريبي برقم: {comment_id}")
        
        # اختبار جلب التعليق
        print("📖 اختبار جلب التعليق...")
        cursor.execute("""
            SELECT id, customer_name, comment_text, rating, image_url
            FROM comments 
            WHERE id = %s
        """, (comment_id,))
        
        comment = cursor.fetchone()
        if comment:
            print(f"✅ تم جلب التعليق: {comment[1]} - {comment[2]}")
        
        # حذف التعليق التجريبي
        print("🗑️ حذف التعليق التجريبي...")
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم حذف التعليق التجريبي")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في التحقق من الجدول: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إضافة عمود image_url للتعليقات...")
    print("=" * 60)
    
    # إضافة العمود
    success = add_image_url_column()
    
    if success:
        # التحقق من صحة الجدول
        verify_success = verify_comments_table()
        
        print("\n" + "=" * 60)
        if verify_success:
            print("🎉 تم إضافة عمود image_url بنجاح!")
            print("✨ يمكن الآن:")
            print("   - رفع صور مع التعليقات")
            print("   - عرض صور التعليقات في الواجهة")
            print("   - استخدام جميع ميزات التعليقات")
        else:
            print("⚠️ تم إضافة العمود ولكن هناك مشاكل في الجدول")
    else:
        print("❌ فشل في إضافة العمود")
        print("💡 تأكد من إعدادات قاعدة البيانات")

if __name__ == "__main__":
    main()
