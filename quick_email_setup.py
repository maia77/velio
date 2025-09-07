#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد سريع للبريد الإلكتروني - ربط نفس الحساب للطلبات والتواصل
"""

import os
import shutil

def setup_unified_email():
    """إعداد موحد للبريد الإلكتروني للطلبات والتواصل"""
    
    print("🔧 إعداد البريد الإلكتروني الموحد لموقع Velio Store")
    print("=" * 60)
    print("📧 سيتم استخدام نفس الحساب للطلبات والتواصل")
    print("=" * 60)
    
    # إدخال بيانات البريد الإلكتروني
    print("\n📝 أدخل بيانات البريد الإلكتروني:")
    sender_email = input("البريد الإلكتروني: ").strip()
    sender_password = input("كلمة مرور التطبيقات: ").strip()
    
    # اختيار مزود البريد الإلكتروني
    print("\n📧 اختر مزود البريد الإلكتروني:")
    print("1. Yahoo Mail")
    print("2. Gmail") 
    print("3. Outlook")
    
    choice = input("اختر رقم (1-3): ").strip()
    
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
    
    # إنشاء محتوى ملف البيئة
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
# تم ربط نفس الحساب للطلبات والتواصل

# نوع مزود البريد الإلكتروني
EMAIL_PROVIDER={email_provider}

# إعدادات البريد الإلكتروني للمرسل (نفس الحساب للطلبات والتواصل)
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}

# البريد الإلكتروني لاستقبال رسائل التواصل والطلبات
# إذا لم يتم تحديده، سيستخدم نفس SENDER_EMAIL
RECEIVER_EMAIL={sender_email}

# إعدادات SMTP
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}

# مفتاح الأمان للتطبيق
SECRET_KEY=velio-store-secret-key-{os.urandom(8).hex()}

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///instance/products.db
"""
    
    try:
        # حفظ ملف .env
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"\n✅ تم إنشاء ملف .env بنجاح!")
        print(f"📁 الموقع: {os.path.abspath('.env')}")
        
        # تعيين متغيرات البيئة للجلسة الحالية
        os.environ['EMAIL_PROVIDER'] = email_provider
        os.environ['SENDER_EMAIL'] = sender_email
        os.environ['SENDER_PASSWORD'] = sender_password
        os.environ['RECEIVER_EMAIL'] = sender_email
        os.environ['SMTP_SERVER'] = smtp_server
        os.environ['SMTP_PORT'] = smtp_port
        
        print("\n🔧 تم تعيين متغيرات البيئة للجلسة الحالية")
        print(f"📧 المرسل: {sender_email}")
        print(f"📧 المستقبل: {sender_email} (نفس المرسل)")
        print(f"🖥️  المزود: {email_provider.upper()}")
        print(f"🖥️  الخادم: {smtp_server}:{smtp_port}")
        
        # اختبار الإعداد
        print("\n🧪 اختبار إعداد البريد الإلكتروني...")
        test_result = test_email_setup()
        
        if test_result:
            print("\n🎉 تم إعداد البريد الإلكتروني بنجاح!")
            print("\n📝 الخطوات التالية:")
            print("1. شغّل التطبيق: python3 web/app.py")
            print("2. اختبر نموذج 'اتصل بنا' في الموقع")
            print("3. اختبر إنشاء طلب جديد")
            print("4. تحقق من وصول الرسائل إلى صندوق الوارد")
        else:
            print("\n❌ فشل في اختبار البريد الإلكتروني")
            print("يرجى التحقق من البيانات المدخلة والمحاولة مرة أخرى")
        
        return test_result
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء ملف .env: {e}")
        return False

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
        subject = "🧪 اختبار البريد الإلكتروني الموحد - Velio Store"
        body = f"""هذه رسالة اختبار من موقع Velio Store

التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
المزود: {email_provider.upper()}
الخادم: {smtp_server}:{smtp_port}

✅ تم ربط نفس الحساب للطلبات والتواصل
📧 المرسل: {sender_email}
📧 المستقبل: {receiver_email}

إذا وصلتك هذه الرسالة، فالإعداد يعمل بشكل صحيح!

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

if __name__ == "__main__":
    print("🚀 مرحباً بك في إعداد البريد الإلكتروني الموحد")
    print("📧 سيتم استخدام نفس الحساب للطلبات والتواصل")
    
    setup_unified_email()

