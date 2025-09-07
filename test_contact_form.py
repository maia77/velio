#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 اختبار نموذج "اتصل بنا"
هذا السكريبت يختبر إعدادات البريد الإلكتروني وإرسال رسالة تجريبية
"""

import os
import sys
import json
from datetime import datetime

def print_header():
    print("=" * 60)
    print("🧪 اختبار نموذج 'اتصل بنا' - Velio Store")
    print("=" * 60)
    print()

def load_env_vars():
    """تحميل متغيرات البيئة"""
    print("📋 تحميل متغيرات البيئة...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ ملف .env غير موجود!")
        return False
    
    # تحميل متغيرات البيئة من ملف .env
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    return True

def check_email_config():
    """فحص إعدادات البريد الإلكتروني"""
    print("\n📧 فحص إعدادات البريد الإلكتروني...")
    
    required_vars = ['EMAIL_PROVIDER', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECEIVER_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var, '')
        if not value or value in ['your-email@yahoo.com', 'your-app-password', 'your-secret-key-here']:
            missing_vars.append(var)
            print(f"❌ {var}: {value}")
        else:
            print(f"✅ {var}: {value[:3]}***{value[-3:] if len(value) > 6 else '***'}")
    
    if missing_vars:
        print(f"\n❌ متغيرات مفقودة أو غير صحيحة: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ جميع الإعدادات تبدو صحيحة!")
    return True

def test_email_sending():
    """اختبار إرسال البريد الإلكتروني"""
    print("\n📤 اختبار إرسال البريد الإلكتروني...")
    
    try:
        # إضافة مسار التطبيق
        sys.path.append('web')
        
        # استيراد دالة الإرسال
        from app import send_email
        
        # إرسال رسالة اختبار
        subject = "🧪 اختبار نموذج اتصل بنا - Velio Store"
        body = f"""هذه رسالة اختبار من نظام Velio Store.

✅ إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح!

التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

تفاصيل الاختبار:
- المزود: {os.environ.get('EMAIL_PROVIDER', 'غير محدد')}
- المرسل: {os.environ.get('SENDER_EMAIL', 'غير محدد')}
- المستقبل: {os.environ.get('RECEIVER_EMAIL', 'غير محدد')}

---
هذه رسالة تلقائية من نظام اختبار Velio Store"""
        
        print("📧 إرسال رسالة الاختبار...")
        result = send_email(subject, body, "Velio Store - Test")
        
        if result:
            print("✅ تم إرسال رسالة الاختبار بنجاح!")
            print("📬 تحقق من صندوق الوارد (والبريد المهمل)")
            return True
        else:
            print("❌ فشل في إرسال رسالة الاختبار")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def test_contact_api():
    """اختبار API نموذج اتصل بنا"""
    print("\n🌐 اختبار API نموذج اتصل بنا...")
    
    try:
        import requests
        
        # بيانات اختبار
        test_data = {
            "name": "اختبار النظام",
            "email": "test@example.com",
            "phone": "+966501234567",
            "subject": "اختبار نموذج اتصل بنا",
            "message": "هذه رسالة اختبار من سكريبت الاختبار. إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح!"
        }
        
        # إرسال طلب إلى API
        print("📤 إرسال طلب إلى /api/contact/messages...")
        
        # محاولة الاتصال بالخادم المحلي
        try:
            response = requests.post(
                'http://localhost:5000/api/contact/messages',
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ API يعمل بشكل صحيح!")
                    print(f"📧 الرسالة: {result.get('message', 'تم الإرسال')}")
                    return True
                else:
                    print(f"❌ فشل API: {result.get('error', 'خطأ غير معروف')}")
                    return False
            else:
                print(f"❌ خطأ HTTP: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("⚠️ لا يمكن الاتصال بالخادم المحلي")
            print("   تأكد من تشغيل التطبيق: python3 web/app.py")
            return False
            
    except ImportError:
        print("⚠️ مكتبة requests غير مثبتة")
        print("   يمكنك تثبيتها: pip install requests")
        return False
    except Exception as e:
        print(f"❌ خطأ في اختبار API: {e}")
        return False

def show_results(email_test, api_test):
    """عرض النتائج"""
    print("\n" + "=" * 60)
    print("📊 نتائج الاختبار")
    print("=" * 60)
    
    print(f"📧 اختبار البريد الإلكتروني: {'✅ نجح' if email_test else '❌ فشل'}")
    print(f"🌐 اختبار API: {'✅ نجح' if api_test else '❌ فشل'}")
    
    if email_test and api_test:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("✅ نموذج 'اتصل بنا' يعمل بشكل صحيح")
        print("📧 ستصل إليك رسائل العملاء")
    elif email_test:
        print("\n⚠️ البريد الإلكتروني يعمل، لكن API لا يعمل")
        print("🔧 تأكد من تشغيل التطبيق: python3 web/app.py")
    elif api_test:
        print("\n⚠️ API يعمل، لكن البريد الإلكتروني لا يعمل")
        print("🔧 راجع إعدادات البريد الإلكتروني")
    else:
        print("\n❌ جميع الاختبارات فشلت")
        print("🔧 راجع الإعدادات وأعد المحاولة")
    
    print("\n📋 الخطوات التالية:")
    if not email_test:
        print("1. 🔧 أعد إعداد البريد الإلكتروني: python3 fix_contact_form.py")
    if not api_test:
        print("2. 🚀 شغل التطبيق: python3 web/app.py")
    print("3. 🌐 اختبر النموذج في المتصفح")
    print("4. 📧 تحقق من وصول الرسائل")

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # تحميل متغيرات البيئة
    if not load_env_vars():
        print("\n🔧 قم بإعداد البريد الإلكتروني أولاً:")
        print("   python3 fix_contact_form.py")
        return
    
    # فحص الإعدادات
    if not check_email_config():
        print("\n🔧 قم بإعداد البريد الإلكتروني أولاً:")
        print("   python3 fix_contact_form.py")
        return
    
    # اختبار البريد الإلكتروني
    email_test = test_email_sending()
    
    # اختبار API
    api_test = test_contact_api()
    
    # عرض النتائج
    show_results(email_test, api_test)

if __name__ == "__main__":
    from pathlib import Path
    main()