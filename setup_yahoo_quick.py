#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد سريع لـ Yahoo Mail
"""

import os

def setup_yahoo_quick():
    """
    إعداد سريع لـ Yahoo Mail
    """
    print("🔵 إعداد سريع لـ Yahoo Mail")
    print("=" * 35)
    
    # الحصول على الإيميل
    print("📧 أدخل إيميل Yahoo الخاص بك:")
    sender_email = input("   الإيميل: ").strip()
    
    if not sender_email or '@yahoo.com' not in sender_email:
        print("❌ يجب أن يكون الإيميل من Yahoo")
        return False
    
    # كلمة المرور المعطاة
    sender_password = "rhpctpddhclirxqp"
    
    print(f"✅ الإيميل: {sender_email}")
    print(f"✅ كلمة المرور: {sender_password[:4]}...{sender_password[-4:]}")
    print(f"📬 الإيميل المستقبل: velio.contact@yahoo.com")
    
    # إنشاء ملف .env
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
EMAIL_PROVIDER=yahoo
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ تم حفظ الإعدادات في ملف .env")
        
        # تعيين متغيرات البيئة
        os.environ['EMAIL_PROVIDER'] = 'yahoo'
        os.environ['SENDER_EMAIL'] = sender_email
        os.environ['SENDER_PASSWORD'] = sender_password
        
        print("✅ تم تعيين متغيرات البيئة")
        
        # اختبار سريع
        print("\n🧪 اختبار سريع...")
        test_email()
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في حفظ الإعدادات: {e}")
        return False

def test_email():
    """
    اختبار إرسال إيميل
    """
    try:
        import sys
        sys.path.append('web')
        from app import send_email
        
        subject = "🧪 اختبار Yahoo Mail - Velio Store"
        body = f"""هذه رسالة اختبار من نظام Velio Store

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
            print("🔍 تحقق من إعدادات Yahoo")
        
        return result
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {e}")
        return False

if __name__ == "__main__":
    print("🚀 إعداد سريع لـ Yahoo Mail")
    print()
    
    if setup_yahoo_quick():
        print("\n🎉 تم الإعداد بنجاح!")
        print("📧 ستصل جميع الإشعارات إلى velio.contact@yahoo.com")
    else:
        print("\n❌ فشل في الإعداد")
        print("🔧 يرجى المحاولة مرة أخرى")
