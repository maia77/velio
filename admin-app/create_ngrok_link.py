#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت سريع لتشغيل ngrok وإنشاء رابط للوصول عن بعد
"""

import subprocess
import time
import requests
import json
import webbrowser

def start_ngrok():
    """تشغيل ngrok"""
    print("🚀 بدء تشغيل ngrok...")
    
    try:
        # تشغيل ngrok في الخلفية
        process = subprocess.Popen(
            ['ngrok', 'http', '5003'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # انتظار قليلاً لبدء ngrok
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"❌ خطأ في تشغيل ngrok: {e}")
        return None

def get_ngrok_url():
    """الحصول على رابط ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    return tunnel['public_url']
        
        return None
    except:
        return None

def main():
    """الدالة الرئيسية"""
    print("🌐 إنشاء رابط ngrok للوصول عن بعد")
    print("=" * 50)
    
    # التحقق من تشغيل التطبيق
    try:
        response = requests.get('http://127.0.0.1:5003/admin', timeout=5)
        if response.status_code == 200:
            print("✅ التطبيق يعمل بنجاح")
        else:
            print("❌ التطبيق لا يعمل")
            return
    except:
        print("❌ التطبيق غير مشغل")
        print("🚀 يرجى تشغيل التطبيق أولاً: python3 app.py")
        return
    
    # تشغيل ngrok
    process = start_ngrok()
    if not process:
        return
    
    print("⏳ انتظار إنشاء النفق...")
    
    # محاولة الحصول على الرابط
    for i in range(10):
        url = get_ngrok_url()
        if url:
            print(f"\n🎉 تم إنشاء الرابط بنجاح!")
            print("=" * 50)
            print(f"🌐 الرابط العام: {url}")
            print(f"🔧 لوحة التحكم: {url}/admin")
            print(f"📱 المنتجات: {url}/view-products")
            print("=" * 50)
            print("📱 شارك هذا الرابط مع أصدقائك!")
            
            # حفظ الرابط في ملف
            with open('ngrok_url.txt', 'w', encoding='utf-8') as f:
                f.write(f"رابط ngrok للوصول عن بعد:\n")
                f.write(f"🌐 الرابط العام: {url}\n")
                f.write(f"🔧 لوحة التحكم: {url}/admin\n")
                f.write(f"📱 المنتجات: {url}/view-products\n")
                f.write(f"⏰ تم إنشاؤه في: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"\n💾 تم حفظ الرابط في ملف: ngrok_url.txt")
            
            # فتح المتصفح
            browser_choice = input("\nهل تريد فتح لوحة التحكم في المتصفح؟ (y/n): ").lower()
            if browser_choice == 'y':
                webbrowser.open(f"{url}/admin")
                print("🌐 تم فتح لوحة التحكم في المتصفح")
            
            print(f"\n⏹️ لإيقاف ngrok، اضغط Ctrl+C")
            
            try:
                # انتظار حتى يتم إيقاف البرنامج
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 إيقاف ngrok...")
                process.terminate()
                process.wait()
                print("✅ تم إيقاف ngrok")
            
            return
        
        print(f"⏳ محاولة {i+1}/10...")
        time.sleep(2)
    
    print("❌ فشل في إنشاء الرابط")
    if process:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main() 