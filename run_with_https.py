#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشغيل التطبيق مع دعم HTTPS
هذا الملف يشغل التطبيق مع شهادة SSL لتحسين خدمة تحديد الموقع على الهواتف
"""

import os
import sys
import subprocess
from pathlib import Path

def check_openssl():
    """فحص وجود OpenSSL"""
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSSL متوفر: {result.stdout.strip()}")
            return True
        else:
            print("❌ OpenSSL غير متوفر")
            return False
    except FileNotFoundError:
        print("❌ OpenSSL غير مثبت")
        return False

def setup_ssl_certificates():
    """إعداد شهادات SSL"""
    print("🔐 إعداد شهادات SSL...")
    
    # تشغيل ملف إعداد SSL
    try:
        result = subprocess.run([sys.executable, 'ssl_setup.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ تم إعداد شهادات SSL بنجاح")
            return True
        else:
            print(f"❌ فشل في إعداد SSL: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ خطأ في إعداد SSL: {e}")
        return False

def run_app_with_https():
    """تشغيل التطبيق مع HTTPS"""
    print("🚀 تشغيل التطبيق مع HTTPS...")
    print("=" * 50)
    
    # فحص OpenSSL
    if not check_openssl():
        print("\n💡 لتثبيت OpenSSL:")
        print("   macOS: brew install openssl")
        print("   Ubuntu: sudo apt-get install openssl")
        print("\n🔄 سيتم التشغيل بدون HTTPS...")
        return run_app_without_https()
    
    # إعداد شهادات SSL
    if not setup_ssl_certificates():
        print("\n🔄 سيتم التشغيل بدون HTTPS...")
        return run_app_without_https()
    
    # تشغيل التطبيق مع HTTPS
    try:
        print("\n🌐 تشغيل التطبيق مع HTTPS...")
        print("📱 خدمة تحديد الموقع ستعمل بشكل أفضل على الهواتف")
        print("🔗 الرابط: https://localhost:5001")
        print("📱 للهاتف: https://192.168.0.240:5001")
        print("\n⚠️  قد يظهر تحذير أمان في المتصفح - اضغط 'متابعة' أو 'Advanced' ثم 'Proceed'")
        print("\n" + "=" * 50)
        
        # تشغيل التطبيق مع SSL
        os.chdir('web')
        subprocess.run([sys.executable, 'app.py', '--ssl'], check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف التطبيق")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ خطأ في تشغيل التطبيق: {e}")
        print("🔄 محاولة التشغيل بدون HTTPS...")
        return run_app_without_https()
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {e}")
        return run_app_without_https()

def run_app_without_https():
    """تشغيل التطبيق بدون HTTPS"""
    print("\n🌐 تشغيل التطبيق بدون HTTPS...")
    print("⚠️  خدمة تحديد الموقع قد لا تعمل بشكل مثالي على الهواتف")
    print("🔗 الرابط: http://localhost:5001")
    print("📱 للهاتف: http://192.168.0.240:5001")
    print("\n" + "=" * 50)
    
    try:
        os.chdir('web')
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف التطبيق")
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل التطبيق: {e}")

def main():
    """الدالة الرئيسية"""
    print("🔐 تشغيل تطبيق Velio مع دعم HTTPS")
    print("=" * 50)
    
    # فحص وجود ملفات التطبيق
    if not Path('web/app.py').exists():
        print("❌ ملف التطبيق غير موجود: web/app.py")
        return
    
    if not Path('ssl_setup.py').exists():
        print("❌ ملف إعداد SSL غير موجود: ssl_setup.py")
        return
    
    # تشغيل التطبيق
    run_app_with_https()

if __name__ == "__main__":
    main()
