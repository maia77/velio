#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعداد البريد الإلكتروني لموقع Velio Store
"""

import os
import getpass

def setup_email_config():
    """
    إعداد تكوين البريد الإلكتروني
    """
    print("🔧 إعداد البريد الإلكتروني لموقع Velio Store")
    print("=" * 50)
    
    print("📧 سيتم إرسال جميع الإشعارات إلى: velio.contact@yahoo.com")
    print()
    
    # الحصول على إيميل (Yahoo, Gmail, أو Outlook)
    print("1️⃣ أدخل إيميلك (Yahoo, Gmail, أو Outlook):")
    sender_email = input("   الإيميل: ").strip()
    
    # تحديد نوع المزود
    if '@yahoo.com' in sender_email or '@ymail.com' in sender_email:
        email_provider = 'yahoo'
    elif '@gmail.com' in sender_email:
        email_provider = 'gmail'
    elif '@outlook.com' in sender_email or '@hotmail.com' in sender_email:
        email_provider = 'outlook'
    else:
        print("❌ يجب أن يكون الإيميل من Yahoo, Gmail, أو Outlook")
        return False
    
    print(f"✅ تم تحديد المزود: {email_provider.upper()}")
    
    # الحصول على كلمة مرور التطبيقات
    print("\n2️⃣ أدخل كلمة مرور التطبيقات:")
    print("   (ليس كلمة مرور الحساب العادية)")
    sender_password = getpass.getpass("   كلمة المرور: ").strip()
    
    if not sender_password:
        print("❌ كلمة المرور مطلوبة")
        return False
    
    # إنشاء ملف .env
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
EMAIL_PROVIDER={email_provider}
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ تم حفظ الإعدادات في ملف .env")
        
        # تعيين متغيرات البيئة للجلسة الحالية
        os.environ['EMAIL_PROVIDER'] = email_provider
        os.environ['SENDER_EMAIL'] = sender_email
        os.environ['SENDER_PASSWORD'] = sender_password
        
        print("✅ تم تعيين متغيرات البيئة")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في حفظ الإعدادات: {e}")
        return False

def test_email_after_setup():
    """
    اختبار البريد الإلكتروني بعد الإعداد
    """
    print("\n🧪 اختبار البريد الإلكتروني...")
    
    try:
        from web.app import send_email
        
        # رسالة اختبار
        subject = "🧪 اختبار اتصال - Velio Store"
        body = f"""هذه رسالة اختبار من نظام إشعارات Velio Store

التاريخ: {os.popen('date').read().strip()}

إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح! ✅

---
تم إرسال هذه الرسالة تلقائياً من نظام اختبار Velio Store"""
        
        result = send_email(subject, body)
        
        if result:
            print("✅ تم إرسال رسالة الاختبار بنجاح!")
            print("📧 تحقق من صندوق الوارد في velio.contact@yahoo.com")
            print("📁 تحقق أيضاً من مجلد Spam/Junk")
        else:
            print("❌ فشل في إرسال رسالة الاختبار")
            print("🔍 تحقق من إعدادات Gmail وكلمة مرور التطبيقات")
        
        return result
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def show_email_setup_instructions():
    """
    عرض تعليمات إعداد البريد الإلكتروني
    """
    print("\n📋 تعليمات إعداد البريد الإلكتروني:")
    print("=" * 40)
    
    print("🔵 Yahoo Mail:")
    print("1. اذهب إلى: https://login.yahoo.com/")
    print("2. اختر 'Account Info' > 'Account Security'")
    print("3. فعّل 'Two-step verification' إذا لم يكن مفعلاً")
    print("4. ابحث عن 'App passwords' أو 'Generate app password'")
    print("5. اختر 'Mail' وادخل اسم للتطبيق مثل 'Velio Store'")
    print("6. انسخ كلمة المرور التي تظهر")
    print()
    
    print("🔴 Gmail:")
    print("1. اذهب إلى: https://myaccount.google.com/")
    print("2. Security > 2-Step Verification > App passwords")
    print("3. اختر 'Mail' و'Other' كجهاز")
    print("4. أدخل اسم للتطبيق مثل 'Velio Store'")
    print("5. انسخ كلمة المرور (16 حرف)")
    print()
    
    print("🟠 Outlook/Hotmail:")
    print("1. اذهب إلى: https://account.microsoft.com/")
    print("2. Security > Advanced security options")
    print("3. App passwords > Create a new app password")
    print("4. أدخل اسم للتطبيق مثل 'Velio Store'")
    print("5. انسخ كلمة المرور")
    print()
    
    print("⚠️ مهم: استخدم كلمة مرور التطبيقات وليس كلمة مرور الحساب العادية")

if __name__ == "__main__":
    print("🚀 إعداد نظام البريد الإلكتروني")
    print()
    
    # عرض تعليمات البريد الإلكتروني
    show_email_setup_instructions()
    
    print("\n" + "="*50)
    choice = input("هل تريد المتابعة مع الإعداد؟ (y/n): ").lower().strip()
    
    if choice in ['y', 'yes', 'نعم']:
        if setup_email_config():
            test_email_after_setup()
        else:
            print("\n❌ فشل في الإعداد. يرجى المحاولة مرة أخرى.")
    else:
        print("\n👋 تم إلغاء الإعداد. يمكنك تشغيل السكريبت مرة أخرى لاحقاً.")
    
    print("\n📞 للدعم: تحقق من ملف EMAIL_SETUP_README.md")
