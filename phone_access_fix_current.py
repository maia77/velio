#!/usr/bin/env python3
"""
حل مشكلة الوصول من الهاتف - الإصدار الحالي
"""

import subprocess
import requests
from datetime import datetime

def get_current_ip():
    """الحصول على عنوان IP الحالي"""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                ip = line.split()[1]
                if ip.startswith('192.168.'):
                    return ip
        return None
    except:
        return None

def test_app_access(ip, port):
    """اختبار الوصول للتطبيق"""
    try:
        response = requests.get(f'http://{ip}:{port}', timeout=5)
        return response.status_code == 200
    except:
        return False

def create_phone_access_guide():
    """إنشاء دليل الوصول من الهاتف"""
    current_ip = get_current_ip()
    
    if not current_ip:
        return "❌ لا يمكن الحصول على عنوان IP"
    
    # اختبار التطبيقات
    main_app_works = test_app_access(current_ip, 5003)
    admin_app_works = test_app_access(current_ip, 5007)
    
    guide = f"""
📱 دليل الوصول من الهاتف - الإصدار الحالي
{'='*60}

🔍 التشخيص:
{'='*20}
📍 عنوان IP الحالي: {current_ip}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🌐 التطبيق الرئيسي (الموقع العام):
{'='*40}
✅ يعمل: {'نعم' if main_app_works else 'لا'}
📱 الرابط: http://{current_ip}:5003
🔧 لوحة إدارة المنتجات: http://{current_ip}:5003/admin/products

🔧 تطبيق الإدارة (إدارة الطلبات):
{'='*40}
✅ يعمل: {'نعم' if admin_app_works else 'لا'}
📱 الرابط: http://{current_ip}:5007
🔧 لوحة إدارة الطلبات: http://{current_ip}:5007/admin/orders

📋 خطوات الوصول من الهاتف:
{'='*30}
1. تأكد من أن الهاتف متصل بنفس شبكة WiFi
2. افتح المتصفح في الهاتف
3. استخدم أحد الروابط التالية:

🚀 روابط سريعة للهاتف:
{'='*30}
📱 الموقع العام: http://{current_ip}:5003
🔧 إدارة الطلبات: http://{current_ip}:5007
📦 إدارة المنتجات: http://{current_ip}:5003/admin/products

⚠️ ملاحظات مهمة:
{'='*20}
- إذا لم يعمل الرابط، تأكد من أن الهاتف على نفس الشبكة
- قد تحتاج لإعادة تشغيل التطبيقات إذا تغير عنوان IP
- استخدم ngrok للحصول على رابط عام دائم

🔧 حلول إضافية:
{'='*20}
1. إعادة تشغيل التطبيقات:
   python3 web/app.py
   python3 admin_app.py

2. استخدام ngrok للوصول العام:
   ngrok http 5007

3. فتح جدار الحماية:
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
"""
    
    # حفظ الدليل
    with open('phone_access_current.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide

def main():
    """الدالة الرئيسية"""
    print("📱 حل مشكلة الوصول من الهاتف")
    print("=" * 50)
    
    guide = create_phone_access_guide()
    print(guide)
    
    print("\n📁 تم حفظ الدليل في: phone_access_current.txt")
    
    # عرض الروابط السريعة
    current_ip = get_current_ip()
    if current_ip:
        print(f"\n🚀 الروابط الصحيحة للهاتف:")
        print(f"📱 الموقع العام: http://{current_ip}:5003")
        print(f"🔧 إدارة الطلبات: http://{current_ip}:5007")

if __name__ == "__main__":
    main()
