#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد سريع للبريد الإلكتروني لموقع Velio Store
"""

import os
import sys

def setup_email_config():
    """إعداد إعدادات البريد الإلكتروني"""
    
    print("🔧 إعداد البريد الإلكتروني لموقع Velio Store")
    print("=" * 50)
    
    # اختيار مزود البريد الإلكتروني
    print("\n📧 اختر مزود البريد الإلكتروني:")
    print("1. Yahoo Mail")
    print("2. Gmail")
    print("3. Outlook")
    
    choice = input("\nاختر رقم (1-3): ").strip()
    
    email_provider = ""
    smtp_server = ""
    smtp_port = ""
    
    if choice == "1":
        email_provider = "yahoo"
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = "587"
    elif choice == "2":
        email_provider = "gmail"
        smtp_server = "smtp.gmail.com"
        smtp_port = "465"
    elif choice == "3":
        email_provider = "outlook"
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = "587"
    else:
        print("❌ اختيار غير صحيح. سيتم استخدام Yahoo كافتراضي.")
        email_provider = "yahoo"
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = "587"
    
    print(f"\n✅ تم اختيار: {email_provider.upper()}")
    print(f"🖥️  الخادم: {smtp_server}:{smtp_port}")
    
    # إدخال بيانات البريد الإلكتروني
    print("\n📝 أدخل بيانات البريد الإلكتروني:")
    sender_email = input("البريد الإلكتروني للمرسل: ").strip()
    sender_password = input("كلمة مرور التطبيقات: ").strip()
    receiver_email = input("البريد الإلكتروني لاستقبال الرسائل: ").strip()
    
    if not receiver_email:
        receiver_email = sender_email
    
    # إنشاء محتوى ملف البيئة
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
# تم إنشاؤها تلقائياً بواسطة setup_email_quick.py

# نوع مزود البريد الإلكتروني
EMAIL_PROVIDER={email_provider}

# إعدادات البريد الإلكتروني للمرسل
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}

# البريد الإلكتروني لاستقبال رسائل التواصل
RECEIVER_EMAIL={receiver_email}

# إعدادات SMTP
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}

# مفتاح الأمان للتطبيق
SECRET_KEY=velio-store-secret-key-{os.urandom(16).hex()}

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///instance/products.db
"""
    
    # حفظ الملف
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ تم إنشاء ملف .env بنجاح!")
        print(f"📁 الموقع: {os.path.abspath('.env')}")
        
        # تعيين متغيرات البيئة للجلسة الحالية
        os.environ['EMAIL_PROVIDER'] = email_provider
        os.environ['SENDER_EMAIL'] = sender_email
        os.environ['SENDER_PASSWORD'] = sender_password
        os.environ['RECEIVER_EMAIL'] = receiver_email
        os.environ['SMTP_SERVER'] = smtp_server
        os.environ['SMTP_PORT'] = smtp_port
        
        print("\n🔧 تم تعيين متغيرات البيئة للجلسة الحالية")
        
        # اختبار الإعداد
        print("\n🧪 اختبار إعداد البريد الإلكتروني...")
        test_email_setup()
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف .env: {e}")
        return False
    
    return True

def test_email_setup():
    """اختبار إعداد البريد الإلكتروني"""
    try:
        import smtplib
        import ssl
        from datetime import datetime
        
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')
        receiver_email = os.environ.get('RECEIVER_EMAIL')
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        email_provider = os.environ.get('EMAIL_PROVIDER', 'yahoo')
        
        if not all([sender_email, sender_password, receiver_email, smtp_server]):
            print("❌ إعدادات البريد الإلكتروني غير مكتملة")
            return False
        
        # إنشاء رسالة اختبار
        subject = "🧪 اختبار إعداد البريد الإلكتروني - Velio Store"
        body = f"""هذه رسالة اختبار من موقع Velio Store

التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
المزود: {email_provider.upper()}
الخادم: {smtp_server}:{smtp_port}

إذا وصلتك هذه الرسالة، فالإعداد يعمل بشكل صحيح! ✅

---
تم إرسالها تلقائياً من نظام Velio Store"""
        
        message = f"""From: Velio Store <{sender_email}>
To: {receiver_email}
Subject: {subject}
Content-Type: text/plain; charset=UTF-8

{body}""".encode('utf-8')
        
        print(f"📧 محاولة الإرسال عبر {email_provider.upper()}...")
        
        # إرسال حسب نوع المزود
        if email_provider == 'gmail':
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message)
        
        print(f"✅ تم إرسال رسالة الاختبار بنجاح إلى {receiver_email}")
        print("📬 تحقق من صندوق الوارد (والمجلد المهمل) لرسالة الاختبار")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ خطأ في المصادقة: {e}")
        print("💡 تأكد من:")
        print("   - صحة البريد الإلكتروني")
        print("   - استخدام كلمة مرور التطبيقات وليس كلمة المرور العادية")
        print("   - تفعيل المصادقة الثنائية")
        return False
    except Exception as e:
        print(f"❌ خطأ في إرسال رسالة الاختبار: {e}")
        return False

def show_instructions():
    """عرض تعليمات إعداد كلمة مرور التطبيقات"""
    print("\n📋 تعليمات إعداد كلمة مرور التطبيقات:")
    print("=" * 50)
    
    print("\n🔹 لـ Yahoo Mail:")
    print("1. اذهب إلى إعدادات الحساب")
    print("2. اختر 'الأمان'")
    print("3. فعّل 'المصادقة الثنائية'")
    print("4. أنشئ 'كلمة مرور التطبيقات'")
    print("5. استخدم كلمة مرور التطبيقات في الإعداد")
    
    print("\n🔹 لـ Gmail:")
    print("1. اذهب إلى إعدادات Google")
    print("2. اختر 'الأمان'")
    print("3. فعّل 'التحقق بخطوتين'")
    print("4. أنشئ 'كلمة مرور التطبيقات'")
    print("5. استخدم كلمة مرور التطبيقات في الإعداد")
    
    print("\n🔹 لـ Outlook:")
    print("1. اذهب إلى إعدادات Microsoft")
    print("2. اختر 'الأمان'")
    print("3. فعّل 'التحقق بخطوتين'")
    print("4. أنشئ 'كلمة مرور التطبيقات'")
    print("5. استخدم كلمة مرور التطبيقات في الإعداد")

if __name__ == "__main__":
    print("🚀 مرحباً بك في إعداد البريد الإلكتروني لموقع Velio Store")
    
    show_instructions()
    
    if setup_email_config():
        print("\n🎉 تم إعداد البريد الإلكتروني بنجاح!")
        print("\n📝 الخطوات التالية:")
        print("1. تحقق من رسالة الاختبار في صندوق الوارد")
        print("2. شغّل التطبيق: python3 web/app.py")
        print("3. اختبر نموذج 'اتصل بنا' في الموقع")
    else:
        print("\n❌ فشل في إعداد البريد الإلكتروني")
        print("يرجى المحاولة مرة أخرى أو التحقق من البيانات المدخلة")
