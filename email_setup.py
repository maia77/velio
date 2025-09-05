#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف إعداد البريد الإلكتروني لموقع Velio Store
يجب إضافة متغيرات البيئة قبل تشغيل التطبيق
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env إذا كان موجوداً
load_dotenv()

def setup_email_config():
    """
    إعداد تكوين البريد الإلكتروني
    """
    print("🔧 إعداد تكوين البريد الإلكتروني لموقع Velio Store")
    print("=" * 60)
    
    # التحقق من وجود متغيرات البيئة
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = 'velio.contact@yahoo.com'  # الإيميل المطلوب
    
    print(f"📧 الإيميل المرسل: {sender_email if sender_email else 'غير محدد'}")
    print(f"🔑 كلمة المرور: {'محددة' if sender_password else 'غير محددة'}")
    print(f"📬 الإيميل المستقبل: {receiver_email}")
    print()
    
    if not sender_email or not sender_password:
        print("⚠️ تحذير: إعدادات البريد الإلكتروني غير مكتملة!")
        print()
        print("لإكمال الإعداد، قم بإنشاء ملف .env في مجلد المشروع وأضف:")
        print("SENDER_EMAIL=your-email@gmail.com")
        print("SENDER_PASSWORD=your-app-password")
        print()
        print("أو قم بتعيين متغيرات البيئة:")
        print("export SENDER_EMAIL='your-email@gmail.com'")
        print("export SENDER_PASSWORD='your-app-password'")
        print()
        print("ملاحظة: استخدم كلمة مرور التطبيقات وليس كلمة مرور الحساب العادية")
        print("للحصول على كلمة مرور التطبيقات:")
        print("1. اذهب إلى إعدادات Google Account")
        print("2. Security > 2-Step Verification > App passwords")
        print("3. أنشئ كلمة مرور جديدة للتطبيق")
        return False
    else:
        print("✅ إعدادات البريد الإلكتروني مكتملة!")
        print("📧 سيتم إرسال جميع الإشعارات إلى:", receiver_email)
        return True

def test_email_connection():
    """
    اختبار اتصال البريد الإلكتروني
    """
    try:
        import smtplib
        import ssl
        from datetime import datetime
        
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')
        receiver_email = 'velio.contact@yahoo.com'
        
        if not sender_email or not sender_password:
            print("❌ لا يمكن اختبار الاتصال: إعدادات البريد الإلكتروني غير مكتملة")
            return False
        
        print("🧪 اختبار اتصال البريد الإلكتروني...")
        
        # إنشاء رسالة اختبار
        subject = "🧪 اختبار اتصال - Velio Store"
        body = f"""هذه رسالة اختبار من نظام إشعارات Velio Store

التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
الوقت: {datetime.now().strftime('%H:%M:%S')}

إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح! ✅

---
تم إرسال هذه الرسالة تلقائياً من نظام اختبار Velio Store"""
        
        message = f"""From: Velio Store <{sender_email}>
To: {receiver_email}
Subject: {subject}
Content-Type: text/plain; charset=UTF-8

{body}

---
تم إرسال هذه الرسالة تلقائياً من نظام اختبار Velio Store
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.encode('utf-8')
        
        # إرسال الرسالة
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        
        print("✅ تم إرسال رسالة الاختبار بنجاح!")
        print(f"📧 تحقق من صندوق الوارد في {receiver_email}")
        return True
        
    except Exception as e:
        print(f"❌ فشل في اختبار الاتصال: {e}")
        return False

if __name__ == "__main__":
    print("🚀 بدء إعداد نظام البريد الإلكتروني")
    print()
    
    # إعداد التكوين
    if setup_email_config():
        print()
        # اختبار الاتصال
        test_email_connection()
    
    print()
    print("📋 ملخص الإعداد:")
    print("- الإيميل المستقبل: velio.contact@yahoo.com")
    print("- سيتم إرسال إشعارات عند:")
    print("  • إرسال رسالة تواصل جديدة")
    print("  • إنشاء طلب جديد")
    print("  • إتمام عملية شراء")
    print("  • استلام موقع GPS")
    print()
    print("🎉 تم إكمال الإعداد!")
