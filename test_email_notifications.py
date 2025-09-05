#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نظام الإشعارات الإلكترونية لموقع Velio Store
"""

import os
import sys
from datetime import datetime

# إضافة مسار المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_system():
    """
    اختبار نظام الإيميل
    """
    print("🧪 اختبار نظام الإشعارات الإلكترونية")
    print("=" * 50)
    
    try:
        # استيراد دالة إرسال الإيميل
        from web.app import send_email
        
        # اختبار 1: رسالة تواصل
        print("📧 اختبار 1: رسالة تواصل جديدة")
        contact_subject = "📧 رسالة تواصل جديدة من أحمد محمد"
        contact_body = """🔔 إشعار جديد من موقع Velio Store

👤 معلومات المرسل:
الاسم: أحمد محمد
البريد الإلكتروني: ahmed@example.com
التاريخ: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

📝 محتوى الرسالة:
مرحباً، أريد الاستفسار عن منتج معين

📞 للرد على العميل:
- البريد الإلكتروني: ahmed@example.com
- الوقت: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
        
        result1 = send_email(contact_subject, contact_body)
        print(f"   النتيجة: {'✅ نجح' if result1 else '❌ فشل'}")
        
        # اختبار 2: طلب منتج
        print("\n🛒 اختبار 2: طلب منتج جديد")
        order_subject = "🛒 طلب جديد #123 - كرسي حديث"
        order_body = """🛒 إشعار طلب جديد من موقع Velio Store

📋 تفاصيل الطلب:
رقم الطلب: #123
المنتج: كرسي حديث
الكمية: 2
السعر الواحد: 150.0 $
السعر الإجمالي: 300.0 $
التاريخ: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

👤 معلومات العميل:
name: سارة أحمد
phone: +966501234567
email: sara@example.com
address: الرياض، المملكة العربية السعودية

📞 للتواصل مع العميل:
- رقم الطلب: #123
- الوقت: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
        
        result2 = send_email(order_subject, order_body)
        print(f"   النتيجة: {'✅ نجح' if result2 else '❌ فشل'}")
        
        # اختبار 3: طلب شامل
        print("\n🛍️ اختبار 3: طلب شامل من سلة التسوق")
        cart_subject = "🛒 طلب شامل جديد #124 - 3 منتج"
        cart_body = """🛒 إشعار طلب شامل جديد من موقع Velio Store

📋 ملخص الطلب:
رقم الطلب: #124
عدد المنتجات: 3
المبلغ الإجمالي: 750.0 $
المبلغ المطلوب الآن (50%): 375.0 $
المبلغ المتبقي عند التسليم: 375.0 $
التاريخ: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

🛍️ تفاصيل المنتجات:

1. كرسي حديث
   - الكمية: 2
   - السعر الإجمالي: 300.0 $

2. طاولة خشبية
   - الكمية: 1
   - السعر الإجمالي: 450.0 $

👤 معلومات العميل:
الاسم: محمد علي
الهاتف: +966501234567
البريد الإلكتروني: mohammed@example.com
العنوان: جدة، المملكة العربية السعودية
طريقة الدفع: bank_transfer

📞 للتواصل مع العميل:
- رقم الطلب: #124
- البريد الإلكتروني: mohammed@example.com
- الهاتف: +966501234567

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
        
        result3 = send_email(cart_subject, cart_body)
        print(f"   النتيجة: {'✅ نجح' if result3 else '❌ فشل'}")
        
        # ملخص النتائج
        print("\n📊 ملخص النتائج:")
        print(f"   رسائل التواصل: {'✅' if result1 else '❌'}")
        print(f"   طلبات المنتجات: {'✅' if result2 else '❌'}")
        print(f"   طلبات شاملة: {'✅' if result3 else '❌'}")
        
        if all([result1, result2, result3]):
            print("\n🎉 جميع الاختبارات نجحت! نظام الإشعارات يعمل بشكل صحيح.")
            print("📧 تحقق من صندوق الوارد في velio.contact@yahoo.com")
        else:
            print("\n⚠️ بعض الاختبارات فشلت. تحقق من إعدادات البريد الإلكتروني.")
            
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        print("تأكد من تشغيل السكريبت من مجلد المشروع الرئيسي")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

def check_email_config():
    """
    فحص إعدادات البريد الإلكتروني
    """
    print("🔍 فحص إعدادات البريد الإلكتروني")
    print("=" * 40)
    
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = 'velio.contact@yahoo.com'
    
    print(f"📧 الإيميل المرسل: {sender_email if sender_email else 'غير محدد'}")
    print(f"🔑 كلمة المرور: {'محددة' if sender_password else 'غير محددة'}")
    print(f"📬 الإيميل المستقبل: {receiver_email}")
    
    if sender_email and sender_password:
        print("✅ الإعدادات مكتملة")
        return True
    else:
        print("❌ الإعدادات غير مكتملة")
        print("\nلإكمال الإعداد:")
        print("1. أنشئ ملف .env في مجلد المشروع")
        print("2. أضف:")
        print("   SENDER_EMAIL=your-email@gmail.com")
        print("   SENDER_PASSWORD=your-app-password")
        return False

if __name__ == "__main__":
    print("🚀 بدء اختبار نظام الإشعارات الإلكترونية")
    print()
    
    # فحص الإعدادات
    if check_email_config():
        print()
        # اختبار النظام
        test_email_system()
    else:
        print("\n⚠️ يرجى إكمال إعدادات البريد الإلكتروني أولاً")
    
    print("\n📋 ملاحظات:")
    print("- جميع الإشعارات تُرسل إلى: velio.contact@yahoo.com")
    print("- تأكد من فحص مجلد Spam/Junk")
    print("- استخدم كلمة مرور التطبيقات وليس كلمة مرور الحساب")
