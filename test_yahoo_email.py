#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار Yahoo Mail مباشرة
"""

import os
import smtplib
import ssl
from datetime import datetime
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def test_yahoo_email():
    """
    اختبار إرسال إيميل عبر Yahoo
    """
    print("🔵 اختبار Yahoo Mail")
    print("=" * 25)
    
    # قراءة الإعدادات
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = 'velio.contact@yahoo.com'
    
    print(f"📧 الإيميل المرسل: {sender_email}")
    print(f"🔑 كلمة المرور: {'✅ محددة' if sender_password else '❌ غير محددة'}")
    print(f"📬 الإيميل المستقبل: {receiver_email}")
    print()
    
    if not sender_email or not sender_password:
        print("❌ إعدادات البريد الإلكتروني غير مكتملة")
        return False
    
    try:
        # إنشاء رسالة
        subject = "🧪 اختبار Yahoo Mail - Velio Store"
        body = f"""هذه رسالة اختبار من نظام Velio Store

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
        
        print("📤 إرسال رسالة الاختبار...")
        print(f"🔧 الخادم: smtp.mail.yahoo.com:587")
        
        # إرسال عبر Yahoo
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()  # تفعيل TLS
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        
        print("✅ تم إرسال رسالة الاختبار بنجاح!")
        print("📧 تحقق من صندوق الوارد في velio.contact@yahoo.com")
        print("📁 تحقق أيضاً من مجلد Spam/Junk")
        print()
        print("🎉 النظام يعمل بشكل صحيح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")
        print()
        print("🔍 تحقق من:")
        print("   - كلمة مرور التطبيقات صحيحة")
        print("   - Two-step verification مفعل")
        print("   - الإيميل من Yahoo")
        return False

if __name__ == "__main__":
    print("🚀 اختبار Yahoo Mail")
    print()
    
    if test_yahoo_email():
        print("\n✅ النتيجة: النظام يعمل بشكل صحيح!")
        print("📧 ستصل جميع الإشعارات إلى velio.contact@yahoo.com")
    else:
        print("\n❌ النتيجة: النظام لا يعمل")
        print("🔧 يرجى التحقق من الإعدادات")
