#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام البريد الإلكتروني
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

def quick_test():
    """
    اختبار سريع للنظام
    """
    print("🧪 اختبار سريع لنظام البريد الإلكتروني")
    print("=" * 45)
    
    # فحص متغيرات البيئة
    email_provider = os.environ.get('EMAIL_PROVIDER', 'yahoo')
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    
    print(f"🔧 المزود: {email_provider.upper()}")
    print(f"📧 الإيميل المرسل: {sender_email if sender_email else '❌ غير محدد'}")
    print(f"🔑 كلمة المرور: {'✅ محددة' if sender_password else '❌ غير محددة'}")
    print(f"📬 الإيميل المستقبل: velio.contact@yahoo.com")
    print()
    
    if not sender_email or not sender_password:
        print("❌ المشكلة: إعدادات البريد الإلكتروني غير مكتملة")
        print()
        print("🔧 الحل:")
        print("1. أنشئ ملف .env في مجلد المشروع")
        print("2. أضف:")
        print("   EMAIL_PROVIDER=yahoo")
        print("   SENDER_EMAIL=your-email@yahoo.com")
        print("   SENDER_PASSWORD=your-app-password")
        print()
        print("أو استخدم السكريبت التفاعلي:")
        print("   python3 setup_email_config.py")
        return False
    
    # اختبار إرسال رسالة
    try:
        print("📤 إرسال رسالة اختبار...")
        
        # استيراد دالة الإرسال
        sys.path.append('web')
        from web.app import send_email
        
        subject = "🧪 اختبار سريع - Velio Store"
        body = f"""هذه رسالة اختبار من نظام Velio Store

التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
الوقت: {datetime.now().strftime('%H:%M:%S')}

إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح! ✅

---
تم إرسال هذه الرسالة تلقائياً من نظام اختبار Velio Store"""
        
        result = send_email(subject, body)
        
        if result:
            print("✅ تم إرسال رسالة الاختبار بنجاح!")
            print("📧 تحقق من صندوق الوارد في velio.contact@yahoo.com")
            print("📁 تحقق أيضاً من مجلد Spam/Junk")
            print()
            print("🎉 النظام يعمل بشكل صحيح!")
            return True
        else:
            print("❌ فشل في إرسال رسالة الاختبار")
            print("🔍 تحقق من:")
            print("   - كلمة مرور التطبيقات صحيحة")
            print("   - 2-Step Verification مفعل")
            print("   - الإيميل من Gmail")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        print("🔍 تحقق من إعدادات المشروع")
        return False

if __name__ == "__main__":
    print("🚀 بدء الاختبار السريع")
    print()
    
    if quick_test():
        print("\n✅ النتيجة: النظام يعمل بشكل صحيح!")
        print("📧 ستصل جميع الإشعارات إلى velio.contact@yahoo.com")
    else:
        print("\n❌ النتيجة: النظام لا يعمل")
        print("🔧 يرجى إكمال الإعداد أولاً")
        print("\n📖 للمساعدة: اقرأ QUICK_EMAIL_SETUP.md")
