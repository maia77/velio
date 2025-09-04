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
        # الحصول على عنوان IP المحلي
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # الحصول على عنوان IP العام
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            public_ip = response.text
        except:
            public_ip = "غير متاح"
        
        return local_ip, public_ip
    except:
        return "127.0.0.1", "غير متاح"

def test_access_urls():
    """اختبار روابط الوصول"""
    local_ip, public_ip = get_network_info()
    
    print("🔍 اختبار روابط الوصول...")
    
    # اختبار الوصول المحلي
    try:
        response = requests.get(f'http://{local_ip}:5003', timeout=5)
        local_works = response.status_code == 200
        print(f"✅ الوصول المحلي: http://{local_ip}:5003")
    except:
        local_works = False
        print(f"❌ الوصول المحلي: http://{local_ip}:5003")
    
    # اختبار الوصول العام
    if public_ip != "غير متاح":
        try:
            response = requests.get(f'http://{public_ip}:5003', timeout=10)
            public_works = response.status_code == 200
            print(f"✅ الوصول العام: http://{public_ip}:5003")
        except:
            public_works = False
            print(f"❌ الوصول العام: http://{public_ip}:5003")
    else:
        public_works = False
        print("❌ الوصول العام: غير متاح")
    
    return local_ip, public_ip, local_works, public_works

def create_phone_solutions():
    """إنشاء حلول الوصول من الهاتف"""
    local_ip, public_ip, local_works, public_works = test_access_urls()
    
    solutions = f"""
📱 حلول الوصول من الهاتف
{'='*50}

🎯 الحل الأول: الوصول المحلي (الأكثر موثوقية)
{'='*30}
✅ يعمل: {'نعم' if local_works else 'لا'}
📱 الرابط: http://{local_ip}:5003
🔧 لوحة التحكم: http://{local_ip}:5003/admin

📋 الخطوات:
1. تأكد من أن الهاتف متصل بنفس الشبكة WiFi
2. افتح المتصفح في الهاتف
3. اكتب: http://{local_ip}:5003

🎯 الحل الثاني: الوصول العام
{'='*30}
✅ يعمل: {'نعم' if public_works else 'لا'}
📱 الرابط: http://{public_ip}:5003
🔧 لوحة التحكم: http://{public_ip}:5003/admin

📋 ملاحظة: قد لا يعمل بسبب إعدادات الراوتر

🎯 الحل الثالث: ngrok (الأكثر موثوقية)
{'='*30}
💡 للحصول على وصول مضمون:
1. شغل: ngrok http 5003
2. انسخ الرابط الذي يظهر
3. شاركه مع الهاتف

🔧 إعدادات إضافية:
{'='*30}
1. فتح جدار الحماية:
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3

2. إعادة تشغيل التطبيق:
   python3 app.py

3. التحقق من الشبكة:
   ifconfig | grep "inet " | grep -v 127.0.0.1

📱 روابط سريعة:
{'='*30}
- الرئيسية: http://{local_ip}:5003
- لوحة التحكم: http://{local_ip}:5003/admin
- المنتجات: http://{local_ip}:5003/view-products

⏰ تم إنشاؤه في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('phone_solutions.txt', 'w', encoding='utf-8') as f:
        f.write(solutions)
    
    return solutions

def main():
    """الدالة الرئيسية"""
    print("📱 حل مشكلة الوصول من الهاتف")
    print("=" * 50)
    
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
    
    # إنشاء الحلول
    solutions = create_phone_solutions()
    print(solutions)
    
    print()
    print("📱 تم إنشاء حلول الوصول من الهاتف!")
    print("📁 راجع ملف: phone_solutions.txt")
    
    # عرض الروابط السريعة
    local_ip, _, _, _ = test_access_urls()
    print()
    print("🚀 روابط سريعة للهاتف:")
    print(f"📱 الرئيسية: http://{local_ip}:5003")
    print(f"🔧 لوحة التحكم: http://{local_ip}:5003/admin")

if __name__ == "__main__":
    main() 