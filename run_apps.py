#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف تشغيل التطبيقين مع قاعدة البيانات المشتركة
"""

import subprocess
import sys
import os
import time
import threading
from shared_database_config_fallback import test_connection

def run_web_app():
    """تشغيل تطبيق الويب على المنفذ 5003"""
    try:
        print("🌐 بدء تشغيل تطبيق الويب على المنفذ 5003...")
        web_dir = os.path.join(os.path.dirname(__file__), 'web')
        os.chdir(web_dir)
        subprocess.run([sys.executable, 'app.py'], check=True)
    except Exception as e:
        print(f"❌ خطأ في تشغيل تطبيق الويب: {e}")

def run_admin_app():
    """تشغيل تطبيق الإدارة على المنفذ 5007"""
    try:
        print("🔧 بدء تشغيل تطبيق الإدارة على المنفذ 5007...")
        admin_dir = os.path.join(os.path.dirname(__file__), 'admin-app')
        os.chdir(admin_dir)
        subprocess.run([sys.executable, 'admin_app_fixed.py'], check=True)
    except Exception as e:
        print(f"❌ خطأ في تشغيل تطبيق الإدارة: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء تشغيل التطبيقين مع قاعدة البيانات المشتركة")
    print("=" * 60)
    
    # اختبار الاتصال بقاعدة البيانات
    success, message = test_connection()
    if not success:
        print(f"❌ فشل الاتصال بقاعدة البيانات: {message}")
        print("🛑 لا يمكن تشغيل التطبيق بدون قاعدة البيانات")
        return
    
    print(f"✅ {message}")
    if "PostgreSQL" in message:
        print("🎯 نوع قاعدة البيانات: PostgreSQL على Render")
    else:
        print("🎯 نوع قاعدة البيانات: SQLite محلية (احتياطي)")
    print()
    
    # إنشاء مؤشرات ترقيم للمنافذ
    print("📋 معلومات التشغيل:")
    print("   🌐 تطبيق الويب: http://127.0.0.1:5003")
    print("   🔧 تطبيق الإدارة: http://127.0.0.1:5007")
    print("   💾 قاعدة البيانات: مشتركة بين التطبيقين")
    print()
    
    try:
        # تشغيل التطبيقين في خيوط منفصلة
        web_thread = threading.Thread(target=run_web_app, daemon=True)
        admin_thread = threading.Thread(target=run_admin_app, daemon=True)
        
        web_thread.start()
        time.sleep(2)  # انتظار قصير بين بدء التطبيقين
        admin_thread.start()
        
        print("✅ تم بدء تشغيل التطبيقين بنجاح!")
        print("🔄 اضغط Ctrl+C لإيقاف التطبيقين")
        
        # انتظار حتى انتهاء الخيوط
        web_thread.join()
        admin_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف التطبيقين بواسطة المستخدم")
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيقين: {e}")

if __name__ == "__main__":
    main()