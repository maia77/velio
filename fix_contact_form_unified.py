#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 إصلاح مشكلة نموذج "اتصل بنا" - إعداد موحد للطلبات والتواصل
هذا السكريبت يعد البريد الإلكتروني لخدمة الطلبات ونموذج "اتصل بنا" معاً
"""

import os
import sys
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🔧 إصلاح مشكلة نموذج 'اتصل بنا' - إعداد موحد")
    print("📧 نفس البريد الإلكتروني للطلبات والتواصل")
    print("=" * 70)
    print()

def check_current_config():
    """فحص الإعدادات الحالية"""
    print("📋 فحص الإعدادات الحالية...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ ملف .env غير موجود!")
        return False
    
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'your-email@yahoo.com' in content or 'your-app-password' in content:
        print("❌ الإعدادات تحتوي على قيم افتراضية")
        print("   SENDER_EMAIL=your-email@yahoo.com")
        print("   SENDER_PASSWORD=your-app-password")
        return False
    else:
        print("✅ الإعدادات تبدو صحيحة")
        return True

def show_unified_setup_info():
    """عرض معلومات الإعداد الموحد"""
    print("📧 إعداد موحد للبريد الإلكتروني")
    print("=" * 50)
    print()
    print("🎯 هذا الإعداد سيؤثر على:")
    print("   ✅ إشعارات الطلبات (للمدير)")
    print("   ✅ رسائل تأكيد الطلبات (للعملاء)")
    print("   ✅ رسائل نموذج 'اتصل بنا'")
    print("   ✅ جميع الإشعارات الأخرى")
    print()
    print("📬 البريد المستقبل:")
    print("   - إشعارات الطلبات → نفس البريد المرسل")
    print("   - رسائل 'اتصل بنا' → نفس البريد المرسل")
    print("   - رسائل تأكيد العملاء → بريد العميل")
    print()

def setup_email_config():
    """إعداد البريد الإلكتروني"""
    print("\n📧 إعداد البريد الإلكتروني الموحد...")
    print("=" * 50)
    
    # اختيار مزود البريد
    print("\nاختر مزود البريد الإلكتروني:")
    print("1. Yahoo Mail (موصى به)")
    print("2. Gmail")
    print("3. Outlook/Hotmail")
    
    while True:
        choice = input("\nاختر رقم (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ اختر رقم صحيح (1-3)")
    
    providers = {
        '1': 'yahoo',
        '2': 'gmail', 
        '3': 'outlook'
    }
    
    provider = providers[choice]
    print(f"✅ تم اختيار: {provider.upper()}")
    
    # إدخال بيانات البريد
    print(f"\n📝 أدخل بيانات البريد الإلكتروني ({provider.upper()}):")
    print("   هذا البريد سيستخدم لجميع الإشعارات")
    
    while True:
        email = input("البريد الإلكتروني: ").strip()
        if '@' in email and '.' in email:
            break
        print("❌ أدخل بريد إلكتروني صحيح")
    
    print(f"\n🔑 كلمة مرور التطبيقات:")
    print("   - لـ Yahoo: اذهب إلى Account Security > App passwords")
    print("   - لـ Gmail: اذهب إلى Security > App passwords")
    print("   - لـ Outlook: اذهب إلى Security > App passwords")
    print("   ⚠️ استخدم كلمة مرور التطبيقات وليس كلمة مرور الحساب!")
    
    password = input("كلمة مرور التطبيقات: ").strip()
    
    return {
        'provider': provider,
        'sender_email': email,
        'sender_password': password,
        'receiver_email': email  # نفس البريد للمرسل والمستقبل
    }

def update_env_file(config):
    """تحديث ملف .env"""
    print("\n💾 تحديث ملف .env...")
    
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
# تم إعدادها تلقائياً بواسطة fix_contact_form_unified.py
# نفس البريد الإلكتروني للطلبات ونموذج "اتصل بنا"

# نوع مزود البريد الإلكتروني (yahoo, gmail, outlook)
EMAIL_PROVIDER={config['provider']}

# إعدادات البريد الإلكتروني للمرسل (لجميع الإشعارات)
SENDER_EMAIL={config['sender_email']}
SENDER_PASSWORD={config['sender_password']}

# البريد الإلكتروني لاستقبال رسائل التواصل والطلبات
# نفس البريد المرسل (سيستقبل جميع الإشعارات)
RECEIVER_EMAIL={config['receiver_email']}

# إعدادات SMTP (سيتم تعيينها تلقائياً حسب EMAIL_PROVIDER)
# SMTP_SERVER=smtp.mail.yahoo.com
# SMTP_PORT=587

# مفتاح الأمان للتطبيق
SECRET_KEY=velio-store-secret-key-2024

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite:///instance/products.db
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم تحديث ملف .env بنجاح")

def test_email_config():
    """اختبار إعدادات البريد"""
    print("\n🧪 اختبار إعدادات البريد...")
    
    try:
        # تحميل متغيرات البيئة
        from dotenv import load_dotenv
        load_dotenv()
        
        # استيراد دالة الإرسال
        sys.path.append('web')
        from app import send_email
        
        # إرسال رسالة اختبار
        subject = "🧪 اختبار النظام الموحد - Velio Store"
        body = f"""هذه رسالة اختبار من نظام Velio Store الموحد.

✅ إذا وصلتك هذه الرسالة، فالنظام يعمل بشكل صحيح!

🎯 هذا البريد سيستقبل:
- 📧 رسائل نموذج "اتصل بنا"
- 🛒 إشعارات الطلبات الجديدة
- 📍 إشعارات المواقع
- 🔔 جميع الإشعارات الأخرى

التاريخ: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
هذه رسالة تلقائية من نظام اختبار Velio Store"""
        
        result = send_email(subject, body)
        
        if result:
            print("✅ تم إرسال رسالة الاختبار بنجاح!")
            print("📧 تحقق من صندوق الوارد (والبريد المهمل)")
            return True
        else:
            print("❌ فشل في إرسال رسالة الاختبار")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

def show_next_steps():
    """عرض الخطوات التالية"""
    print("\n" + "=" * 70)
    print("🎉 تم إعداد البريد الإلكتروني الموحد بنجاح!")
    print("=" * 70)
    print()
    print("📋 ما تم إعداده:")
    print("✅ البريد الإلكتروني للطلبات")
    print("✅ البريد الإلكتروني لنموذج 'اتصل بنا'")
    print("✅ جميع الإشعارات الأخرى")
    print()
    print("📋 الخطوات التالية:")
    print("1. ✅ تحقق من صندوق الوارد للرسالة التجريبية")
    print("2. 🔄 أعد تشغيل التطبيق:")
    print("   python3 web/app.py")
    print("3. 🌐 اذهب إلى صفحة 'اتصل بنا' واختبر النموذج")
    print("4. 🛒 جرب إنشاء طلب واختبر الإشعارات")
    print("5. 📧 يجب أن تصلك جميع الرسائل")
    print()
    print("🔧 إذا لم تصل الرسائل:")
    print("- تحقق من مجلد البريد المهمل")
    print("- تأكد من صحة كلمة مرور التطبيقات")
    print("- جرب مزود بريد آخر")
    print()
    print("📞 للدعم: تحقق من ملف CONTACT_FORM_FIX_GUIDE.md")

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # عرض معلومات الإعداد الموحد
    show_unified_setup_info()
    
    # فحص الإعدادات الحالية
    if check_current_config():
        print("\n✅ الإعدادات تبدو صحيحة بالفعل!")
        choice = input("هل تريد إعادة الإعداد؟ (y/n): ").strip().lower()
        if choice != 'y':
            print("👋 تم الإلغاء")
            return
    
    try:
        # إعداد البريد الإلكتروني
        config = setup_email_config()
        
        # تحديث ملف .env
        update_env_file(config)
        
        # اختبار الإعدادات
        if test_email_config():
            show_next_steps()
        else:
            print("\n⚠️ فشل الاختبار، لكن الإعدادات تم حفظها")
            print("🔧 يمكنك إعادة تشغيل السكريبت أو التحقق من الإعدادات يدوياً")
            
    except KeyboardInterrupt:
        print("\n\n👋 تم الإلغاء بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        print("🔧 يمكنك إعادة تشغيل السكريبت أو الإعداد يدوياً")

if __name__ == "__main__":
    main()
