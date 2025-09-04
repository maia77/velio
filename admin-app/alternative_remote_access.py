#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import webbrowser
import threading
import time
import requests

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        return None

def start_dashboard():
    print("🚀 بدء تشغيل لوحة التحكم...")
    os.system("python3 admin_dashboard.py &")
    time.sleep(3)

def main():
    print("🌐 إعداد الوصول عن بعد (بديل ngrok)...")
    
    # بدء لوحة التحكم
    start_dashboard()
    
    # الحصول على عنوان IP العام
    public_ip = get_public_ip()
    
    if public_ip:
        print(f"🌍 عنوان IP العام: {public_ip}")
        print(f"🔗 رابط لوحة التحكم: http://{public_ip}:5009")
        print("")
        print("⚠️  ملاحظات مهمة:")
        print("   1. تأكد من فتح المنفذ 5009 في جدار الحماية")
        print("   2. قد تحتاج لتكوين Router للسماح بالوصول")
        print("   3. هذا الحل يعمل فقط إذا كان لديك عنوان IP ثابت")
        print("")
        print("💡 للحصول على حل أفضل، استخدم ngrok")
    else:
        print("❌ لا يمكن الحصول على عنوان IP العام")
        print("💡 استخدم ngrok للحصول على رابط عام")

if __name__ == "__main__":
    main()
