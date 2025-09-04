#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import requests
import socket
import time
import os
from datetime import datetime

def get_local_ip():
    """الحصول على عنوان IP المحلي"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_app_running():
    """التحقق من تشغيل التطبيق"""
    try:
        response = requests.get('http://127.0.0.1:5003', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_app():
    """تشغيل التطبيق"""
    print("🚀 بدء تشغيل التطبيق...")
    try:
        subprocess.Popen(['python3', 'app.py'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
        time.sleep(5)
        
        if check_app_running():
            print("✅ التطبيق يعمل بنجاح")
            return True
        else:
            print("❌ فشل في تشغيل التطبيق")
            return False
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")
        return False

def test_network_access():
    """اختبار الوصول الشبكي"""
    local_ip = get_local_ip()
    
    print(f"🌐 اختبار الوصول الشبكي...")
    print(f"📱 عنوان IP المحلي: {local_ip}")
    
    # اختبار الوصول المحلي
    try:
        response = requests.get(f'http://{local_ip}:5003', timeout=5)
        if response.status_code == 200:
            print("✅ الوصول المحلي يعمل")
            return True
        else:
            print("❌ الوصول المحلي لا يعمل")
            return False
    except Exception as e:
        print(f"❌ خطأ في الوصول المحلي: {e}")
        return False

def create_phone_access_guide():
    """إنشاء دليل الوصول من الهاتف"""
    local_ip = get_local_ip()
    
    guide = f"""
📱 دليل الوصول من الهاتف
{'='*50}

🔧 الخطوات:

1. تأكد من أن الهاتف متصل بنفس الشبكة WiFi
2. افتح المتصفح في الهاتف
3. اكتب الرابط التالي:

   الرئيسية: http://{local_ip}:5003
   لوحة التحكم: http://{local_ip}:5003/admin

🔍 إذا لم يعمل:

1. تحقق من إعدادات جدار الحماية:
   - افتح System Preferences > Security & Privacy > Firewall
   - تأكد من أن Python مسموح له

2. جرب إعادة تشغيل التطبيق:
   python3 app.py

3. تحقق من عنوان IP:
   ifconfig | grep "inet " | grep -v 127.0.0.1

4. جرب ngrok للحصول على وصول مضمون:
   ngrok http 5003

📱 روابط سريعة:
- الرئيسية: http://{local_ip}:5003
- لوحة التحكم: http://{local_ip}:5003/admin
- المنتجات: http://{local_ip}:5003/view-products

⏰ تم إنشاؤه في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open('phone_access_guide.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide

def run_ngrok_for_phone():
    """تشغيل ngrok للوصول من الهاتف"""
    print("🌐 تشغيل ngrok للوصول من الهاتف...")
    
    try:
        # التحقق من ngrok
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ ngrok غير مثبت")
            print("💡 قم بتثبيت ngrok: brew install ngrok/ngrok/ngrok")
            return False
        
        # تشغيل ngrok
        print("🚀 بدء تشغيل ngrok...")
        process = subprocess.Popen(['ngrok', 'http', '5003'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        time.sleep(3)
        
        # محاولة الحصول على الرابط
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"🎉 الرابط العام للهاتف: {public_url}")
                    print(f"🔧 لوحة التحكم: {public_url}/admin")
                    
                    # حفظ الرابط
                    with open('phone_ngrok_url.txt', 'w', encoding='utf-8') as f:
                        f.write(f"📱 رابط الهاتف عبر ngrok\n")
                        f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"🔗 {public_url}\n")
                        f.write(f"🔧 لوحة التحكم: {public_url}/admin\n")
                    
                    return True
        except:
            print("⚠️ لا يمكن الحصول على الرابط تلقائياً")
            print("💡 راجع: http://localhost:4040")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في تشغيل ngrok: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("📱 حل مشكلة الوصول من الهاتف")
    print("=" * 50)
    
    # التحقق من تشغيل التطبيق
    if not check_app_running():
        print("⚠️ التطبيق غير مشغل")
        choice = input("هل تريد تشغيل التطبيق؟ (y/n): ").lower()
        if choice == 'y':
            if not start_app():
                print("❌ لا يمكن المتابعة بدون تشغيل التطبيق")
                return
        else:
            print("❌ لا يمكن المتابعة بدون تشغيل التطبيق")
            return
    else:
        print("✅ التطبيق يعمل بنجاح")
    
    print()
    
    # اختبار الوصول الشبكي
    if test_network_access():
        print("✅ الوصول الشبكي يعمل")
    else:
        print("❌ مشكلة في الوصول الشبكي")
    
    print()
    
    # إنشاء دليل الوصول
    guide = create_phone_access_guide()
    print(guide)
    
    print()
    
    # خيار ngrok
    choice = input("هل تريد تشغيل ngrok للوصول المضمون؟ (y/n): ").lower()
    if choice == 'y':
        if run_ngrok_for_phone():
            print("✅ تم إنشاء رابط ngrok للهاتف!")
        else:
            print("❌ فشل في تشغيل ngrok")
    
    print()
    print("📱 تم إنشاء دليل الوصول من الهاتف!")
    print("📁 راجع ملف: phone_access_guide.txt")

if __name__ == "__main__":
    main() 