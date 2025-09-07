#!/usr/bin/env python3
"""
سكريبت لإضافة عمود الصور للتعليقات
"""

import sqlite3
import os
from datetime import datetime

def migrate_comments_table():
    """إضافة عمود image_url لجدول التعليقات"""
    
    # مسار قاعدة البيانات
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'products.db')
    
    if not os.path.exists(db_path):
        print(f"❌ قاعدة البيانات غير موجودة في: {db_path}")
        return False
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود العمود
        cursor.execute("PRAGMA table_info(comments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_url' in columns:
            print("✅ عمود image_url موجود بالفعل في جدول التعليقات")
            return True
        
        # إضافة العمود
        print("🔄 إضافة عمود image_url لجدول التعليقات...")
        cursor.execute("ALTER TABLE comments ADD COLUMN image_url VARCHAR(500)")
        
        # حفظ التغييرات
        conn.commit()
        print("✅ تم إضافة عمود image_url بنجاح")
        
        # التحقق من النتيجة
        cursor.execute("PRAGMA table_info(comments)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 أعمدة جدول التعليقات: {', '.join(columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تحديث قاعدة البيانات: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تحديث قاعدة البيانات لإضافة دعم صور التعليقات...")
    print("=" * 60)
    
    success = migrate_comments_table()
    
    print("=" * 60)
    if success:
        print("✅ تم تحديث قاعدة البيانات بنجاح!")
        print("🎉 يمكن الآن رفع الصور مع التعليقات")
    else:
        print("❌ فشل في تحديث قاعدة البيانات")
        print("💡 تأكد من وجود قاعدة البيانات في المسار الصحيح")

if __name__ == "__main__":
    main()
