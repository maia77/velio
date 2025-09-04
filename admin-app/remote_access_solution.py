#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import requests
import subprocess
import time
from datetime import datetime

def get_network_info():
    """الحصول على معلومات الشبكة"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            public_ip = response.text
        except:
            public_ip = "غير متاح"
        
        return local_ip, public_ip
    except:
        return "127.0.0.1", "غير متاح"

def test_public_access():
    """اختبار الوصول العام"""
    local_ip, public_ip = get_network_info()
    
    print("🌐 اختبار الوصول العام...")
    print(f"📱 عنوان IP العام: {public_ip}")
    
    if public_ip != "غير متاح":
        try:
            response = requests.get(f'http://{public_ip}:5003', timeout=10)
            if response.status_code == 200:
                print("✅ الوصول العام يعمل!")
                return True, public_ip
            else:
                print("❌ الوصول العام لا يعمل")
                return False, public_ip
        except:
            print("❌ الوصول العام لا يعمل")
            return False, public_ip
    else:
        print("❌ لا يمكن الحصول على عنوان IP العام")
        return False, "غير متاح"

def create_remote_solutions():
    """إنشاء حلول للوصول عن بعد"""
    local_ip, public_ip = get_network_info()
    public_works, _ = test_public_access()
    
    solutions = f"""
🌐 حلول الوصول عن بعد (لأصدقاء في أماكن مختلفة)
{'='*60}

🎯 الحل الأول: الوصول العام (إذا كان يعمل)
{'='*40}
✅ يعمل: {'نعم' if public_works else 'لا'}
📱 الرابط: http://{public_ip}:5003/admin
🔧 لوحة التحكم: http://{public_ip}:5003/admin

📋 ملاحظة: قد لا يعمل بسبب إعدادات الراوتر

🎯 الحل الثاني: Port Forwarding
{'='*40}
💡 لتشغيل الوصول العام:

1. افتح إعدادات الراوتر
2. ابحث عن Port Forwarding
3. أضف قاعدة جديدة:
   - المنفذ: 5003
   - البروتوكول: TCP
   - عنوان IP المحلي: {local_ip}
4. احفظ الإعدادات

🎯 الحل الثالث: ngrok (الأكثر موثوقية)
{'='*40}
💡 للحصول على وصول مضمون:

1. تثبيت ngrok:
   brew install ngrok/ngrok/ngrok

2. إنشاء حساب:
   https://dashboard.ngrok.com/signup

3. الحصول على authtoken:
   https://dashboard.ngrok.com/get-started/your-authtoken

4. إعداد ngrok:
   ngrok config add-authtoken YOUR_TOKEN

5. تشغيل ngrok:
   ngrok http 5003

🎯 الحل الرابع: خدمة سحابية
{'='*40}
💡 يمكن استخدام خدمات مثل:
- Heroku
- Railway
- Render
- Vercel

📱 روابط سريعة:
{'='*40}
- الوصول العام: http://{public_ip}:5003/admin
- الوصول المحلي: http://{local_ip}:5003/admin

⏰ تم إنشاؤه في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return solutions

def create_friend_message():
    """إنشاء رسالة للصديقة"""
    local_ip, public_ip = get_network_info()
    public_works, _ = test_public_access()
    
    message = f"""
مرحبا! 👋

هنا روابط لوحة التحكم:

🔧 لوحة التحكم (عام): http://{public_ip}:5003/admin
⚠️ قد لا يعمل بسبب إعدادات الراوتر

🔧 لوحة التحكم (محلي): http://{local_ip}:5003/admin
✅ يعمل فقط في نفس المكان

الخطوات:
1. جرب الرابط العام أولاً
2. إذا لم يعمل، أخبريني
3. سأحاول حل المشكلة

إذا لم يعمل، أخبريني! 😊
"""
    
    return message

def setup_port_forwarding_guide():
    """دليل إعداد Port Forwarding"""
    local_ip, _ = get_network_info()
    
    guide = f"""
🔧 دليل إعداد Port Forwarding
{'='*50}

📋 الخطوات:

1. افتح إعدادات الراوتر:
   - اكتب في المتصفح: 192.168.1.1 أو 192.168.0.1
   - أو راجع كتيب الراوتر

2. ابحث عن:
   - Port Forwarding
   - Port Mapping
   - Virtual Server

3. أضف قاعدة جديدة:
   - اسم الخدمة: Flask App
   - المنفذ الخارجي: 5003
   - المنفذ الداخلي: 5003
   - عنوان IP المحلي: {local_ip}
   - البروتوكول: TCP

4. احفظ الإعدادات

5. اختبر الوصول:
   - من هاتف آخر
   - أو من موقع: https://www.yougetsignal.com/tools/open-ports/

⚠️ ملاحظة: قد تحتاج لمساعدة من مزود الإنترنت
"""
    
    return guide

def main():
    """الدالة الرئيسية"""
    print("🌐 حلول الوصول عن بعد")
    print("=" * 50)
    print("📱 للأصدقاء في أماكن مختلفة")
    print()
    
    # التحقق من تشغيل التطبيق
    try:
        response = requests.get('http://127.0.0.1:5003', timeout=5)
        if response.status_code == 200:
            print("✅ التطبيق يعمل بنجاح")
        else:
            print("❌ التطبيق لا يعمل")
            return
    except:
        print("❌ التطبيق غير مشغل")
        print("💡 شغل: python3 app.py")
        return
    
    print()
    
    # اختبار الوصول العام
    public_works, public_ip = test_public_access()
    
    print()
    
    # إنشاء الحلول
    solutions = create_remote_solutions()
    print(solutions)
    
    # حفظ الحلول
    with open('remote_solutions.txt', 'w', encoding='utf-8') as f:
        f.write(solutions)
    print("📁 تم حفظ الحلول في: remote_solutions.txt")
    
    print()
    
    # رسالة للصديقة
    friend_message = create_friend_message()
    print("📱 رسالة للصديقة:")
    print("=" * 30)
    print(friend_message)
    
    print()
    
    # دليل Port Forwarding
    if not public_works:
        print("🔧 دليل إعداد Port Forwarding:")
        print("=" * 40)
        port_guide = setup_port_forwarding_guide()
        print(port_guide)
        
        with open('port_forwarding_guide.txt', 'w', encoding='utf-8') as f:
            f.write(port_guide)
        print("📁 تم حفظ الدليل في: port_forwarding_guide.txt")
    
    print()
    print("🎯 الروابط للصديقة:")
    print(f"🌐 الوصول العام: http://{public_ip}:5003/admin")
    print(f"📱 الوصول المحلي: http://192.168.0.72:5003/admin")

if __name__ == "__main__":
    main() 