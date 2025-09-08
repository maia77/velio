#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد سريع للبريد الإلكتروني لموقع Velio Store
"""

import os
import re

def setup_email_credentials():
    """إعداد بيانات البريد الإلكتروني"""
    print("🔧 إعداد البريد الإلكتروني لموقع Velio Store")
    print("=" * 50)
    
    # اختيار مزود البريد
    print("\n📧 اختر مزود البريد الإلكتروني:")
    print("1. Yahoo Mail")
    print("2. Gmail")
    print("3. Outlook")
    
    while True:
        choice = input("\nاختر (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ اختر رقم صحيح (1-3)")
    
    providers = {
        '1': {'name': 'yahoo', 'domain': '@yahoo.com'},
        '2': {'name': 'gmail', 'domain': '@gmail.com'},
        '3': {'name': 'outlook', 'domain': '@outlook.com'}
    }
    
    provider = providers[choice]
    
    # إدخال البريد الإلكتروني
    print(f"\n📧 أدخل بريدك الإلكتروني ({provider['domain']}):")
    while True:
        email = input("البريد الإلكتروني: ").strip()
        if email and '@' in email:
            break
        print("❌ أدخل بريد إلكتروني صحيح")
    
    # إدخال كلمة مرور التطبيقات
    print(f"\n🔑 أدخل كلمة مرور التطبيقات:")
    print("(هذه ليست كلمة المرور العادية - يجب إنشاؤها من إعدادات الحساب)")
    while True:
        password = input("كلمة مرور التطبيقات: ").strip()
        if password and len(password) >= 8:
            break
        print("❌ كلمة مرور التطبيقات يجب أن تكون 8 أحرف على الأقل")
    
    # البريد المستقبل (نفس المرسل أو مختلف)
    print(f"\n📨 البريد المستقبل لرسائل التواصل:")
    print("(يمكن أن يكون نفس البريد المرسل أو بريد مختلف)")
    receiver = input(f"البريد المستقبل (افتراضي: {email}): ").strip()
    if not receiver:
        receiver = email
    
    return {
        'provider': provider['name'],
        'sender_email': email,
        'sender_password': password,
        'receiver_email': receiver
    }

def update_render_yaml(credentials):
    """تحديث ملف render.yaml"""
    print("\n📝 تحديث ملف render.yaml...")
    
    render_file = 'render.yaml'
    if not os.path.exists(render_file):
        print(f"❌ ملف {render_file} غير موجود")
        return False
    
    # قراءة الملف
    with open(render_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # تحديث القيم
    replacements = {
        'YOUR_REAL_EMAIL@yahoo.com': credentials['sender_email'],
        'YOUR_APP_PASSWORD': credentials['sender_password'],
        'your-email@yahoo.com': credentials['sender_email'],
        'your-app-password': credentials['sender_password']
    }
    
    # استبدال القيم
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # تحديث مزود البريد
    content = re.sub(
        r'EMAIL_PROVIDER\s*:\s*\w+',
        f"EMAIL_PROVIDER: {credentials['provider']}",
        content
    )
    
    # حفظ الملف
    with open(render_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم تحديث render.yaml بنجاح")
    return True

def create_env_file(credentials):
    """إنشاء ملف .env للاختبار المحلي"""
    print("\n📄 إنشاء ملف .env للاختبار المحلي...")
    
    env_content = f"""# إعدادات البريد الإلكتروني لموقع Velio Store
EMAIL_PROVIDER={credentials['provider']}
SENDER_EMAIL={credentials['sender_email']}
SENDER_PASSWORD={credentials['sender_password']}
RECEIVER_EMAIL={credentials['receiver_email']}

# إعدادات SMTP
SMTP_SERVER=smtp.{credentials['provider']}.com
SMTP_PORT=587

# مفتاح الأمان
SECRET_KEY=your-secret-key-here
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ تم إنشاء ملف .env")

def main():
    """الدالة الرئيسية"""
    try:
        # إعداد البيانات
        credentials = setup_email_credentials()
        
        # تحديث render.yaml
        if update_render_yaml(credentials):
            # إنشاء ملف .env
            create_env_file(credentials)
            
            print("\n🎉 تم الإعداد بنجاح!")
            print("\n📋 الخطوات التالية:")
            print("1. git add render.yaml .env")
            print("2. git commit -m 'Setup email configuration'")
            print("3. git push origin main")
            print("\n🔍 بعد النشر، اختبر نموذج 'تواصل معنا'")
            
        else:
            print("❌ فشل في تحديث render.yaml")
            
    except KeyboardInterrupt:
        print("\n\n❌ تم إلغاء العملية")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")

if __name__ == "__main__":
    main()