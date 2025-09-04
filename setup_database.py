#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف إعداد قاعدة البيانات
ينشئ الجداول المطلوبة في قاعدة البيانات
"""

import sys
import os

# إضافة مسارات التطبيقين
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin-app'))

def setup_web_database():
    """إعداد قاعدة البيانات لتطبيق الويب"""
    try:
        print("🌐 إعداد قاعدة البيانات لتطبيق الويب...")
        
        from web.app import app, db
        with app.app_context():
            db.create_all()
            print("✅ تم إنشاء جداول تطبيق الويب بنجاح")
            return True
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة بيانات تطبيق الويب: {e}")
        return False

def setup_admin_database():
    """إعداد قاعدة البيانات لتطبيق الإدارة"""
    try:
        print("🔧 إعداد قاعدة البيانات لتطبيق الإدارة...")
        
        from admin_app.admin_app_fixed import app, db
        with app.app_context():
            db.create_all()
            print("✅ تم إنشاء جداول تطبيق الإدارة بنجاح")
            return True
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة بيانات تطبيق الإدارة: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إعداد قاعدة البيانات للتطبيقين")
    print("=" * 50)
    
    # إعداد قاعدة البيانات لتطبيق الويب
    web_success = setup_web_database()
    
    # إعداد قاعدة البيانات لتطبيق الإدارة
    admin_success = setup_admin_database()
    
    if web_success and admin_success:
        print("\n🎉 تم إعداد قاعدة البيانات بنجاح لكلا التطبيقين!")
        print("🚀 يمكنك الآن تشغيل التطبيقين")
    else:
        print("\n❌ فشل في إعداد قاعدة البيانات")
        if not web_success:
            print("   - مشكلة في تطبيق الويب")
        if not admin_success:
            print("   - مشكلة في تطبيق الإدارة")

if __name__ == "__main__":
    main()
