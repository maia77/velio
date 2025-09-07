#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 اختبار اتصال Yahoo Mail
هذا السكريبت يختبر الاتصال بخادم Yahoo Mail مع إعدادات مختلفة
"""

import smtplib
import ssl
import os
from dotenv import load_dotenv

def test_yahoo_connection():
    """اختبار الاتصال بخادم Yahoo"""
    print("🧪 اختبار اتصال Yahoo Mail")
    print("=" * 50)
    
    # تحميل متغيرات البيئة
    load_dotenv()
    
    email = os.environ.get('SENDER_EMAIL', '')
    password = os.environ.get('SENDER_PASSWORD', '')
    
    if not email or not password:
        print("❌ بيانات البريد الإلكتروني غير مكتملة")
        return False
    
    print(f"📧 البريد: {email}")
    print(f"🔑 كلمة المرور: {password[:3]}***{password[-3:]}")
    
    # إعدادات Yahoo المختلفة
    yahoo_configs = [
        {
            'name': 'Yahoo SMTP (TLS)',
            'server': 'smtp.mail.yahoo.com',
            'port': 587,
            'use_tls': True,
            'use_ssl': False
        },
        {
            'name': 'Yahoo SMTP (SSL)',
            'server': 'smtp.mail.yahoo.com',
            'port': 465,
            'use_tls': False,
            'use_ssl': True
        },
        {
            'name': 'Yahoo SMTP (Alternative)',
            'server': 'smtp.mail.yahoo.com',
            'port': 25,
            'use_tls': True,
            'use_ssl': False
        }
    ]
    
    for config in yahoo_configs:
        print(f"\n🔧 اختبار: {config['name']}")
        print(f"   الخادم: {config['server']}:{config['port']}")
        
        try:
            if config['use_ssl']:
                # استخدام SSL
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(config['server'], config['port'], context=context) as server:
                    print("   🔐 استخدام SSL...")
                    print("   🔑 محاولة تسجيل الدخول...")
                    server.login(email, password)
                    print("   ✅ نجح الاتصال!")
                    return True
            else:
                # استخدام TLS
                with smtplib.SMTP(config['server'], config['port']) as server:
                    print("   🔒 تفعيل TLS...")
                    server.starttls()
                    print("   🔑 محاولة تسجيل الدخول...")
                    server.login(email, password)
                    print("   ✅ نجح الاتصال!")
                    return True
                    
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ خطأ في المصادقة: {e}")
            print("   💡 تحقق من كلمة مرور التطبيقات")
        except smtplib.SMTPConnectError as e:
            print(f"   ❌ خطأ في الاتصال: {e}")
        except smtplib.SMTPServerDisconnected as e:
            print(f"   ❌ انقطع الاتصال: {e}")
        except Exception as e:
            print(f"   ❌ خطأ عام: {e}")
    
    print("\n❌ فشل في الاتصال بجميع الإعدادات")
    return False

def show_troubleshooting():
    """عرض نصائح استكشاف الأخطاء"""
    print("\n" + "=" * 50)
    print("🔧 نصائح استكشاف الأخطاء")
    print("=" * 50)
    
    print("\n1. 🔑 تحقق من كلمة مرور التطبيقات:")
    print("   - اذهب إلى: https://login.yahoo.com/")
    print("   - Account Info > Account Security")
    print("   - App passwords > Generate app password")
    print("   - اختر 'Mail' وادخل اسم للتطبيق")
    
    print("\n2. 🔐 تأكد من تفعيل Two-step verification:")
    print("   - يجب تفعيل Two-step verification أولاً")
    print("   - ثم إنشاء كلمة مرور التطبيقات")
    
    print("\n3. 🌐 تحقق من الاتصال بالإنترنت:")
    print("   - تأكد من اتصال الإنترنت")
    print("   - جرب إعادة تشغيل الراوتر")
    
    print("\n4. 🔄 جرب مزود بريد آخر:")
    print("   - Gmail: smtp.gmail.com:465")
    print("   - Outlook: smtp-mail.outlook.com:587")
    
    print("\n5. 📧 تحقق من صحة البريد الإلكتروني:")
    print("   - تأكد من كتابة البريد بشكل صحيح")
    print("   - تأكد من أن الحساب نشط")

def main():
    """الدالة الرئيسية"""
    success = test_yahoo_connection()
    
    if not success:
        show_troubleshooting()
        
        print("\n" + "=" * 50)
        print("💡 الحلول المقترحة")
        print("=" * 50)
        
        print("\n1. 🔄 أعد إنشاء كلمة مرور التطبيقات:")
        print("   - اذهب إلى Yahoo Account Security")
        print("   - احذف كلمة المرور القديمة")
        print("   - أنشئ كلمة مرور جديدة")
        
        print("\n2. 🔄 جرب مزود بريد آخر:")
        print("   python3 fix_contact_form_unified.py")
        print("   اختر Gmail أو Outlook")
        
        print("\n3. 🔧 تحقق من إعدادات الحساب:")
        print("   - تأكد من تفعيل Two-step verification")
        print("   - تأكد من أن الحساب نشط")
        print("   - جرب تسجيل الدخول من المتصفح")

if __name__ == "__main__":
    main()
