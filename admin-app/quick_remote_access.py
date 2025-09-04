#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import requests
import subprocess
import os
import json
from datetime import datetime

def get_local_ip():
    """الحصول على عنوان IP المحلي"""
    try:
        # الاتصال بـ Google DNS للحصول على IP المحلي
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def get_public_ip():
    """الحصول على عنوان IP العام"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "غير متاح"

def check_ngrok():
    """التحقق من تثبيت ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def run_ngrok():
    """تشغيل ngrok"""
    try:
        # التحقق من وجود authtoken
        result = subprocess.run(['ngrok', 'config', 'check'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, "ngrok يحتاج إلى authtoken"
        
        # تشغيل ngrok
        process = subprocess.Popen(['ngrok', 'http', '5003'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        return True, "ngrok يعمل"
    except Exception as e:
        return False, str(e)

def create_access_info():
    """إنشاء معلومات الوصول"""
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    ngrok_available = check_ngrok()
    
    info = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "local_access": {
            "url": f"http://{local_ip}:5003",
            "admin_url": f"http://{local_ip}:5003/admin",
            "description": "الوصول المحلي (من نفس الشبكة)"
        },
        "public_access": {
            "ip": public_ip,
            "url": f"http://{public_ip}:5003" if public_ip != "غير متاح" else "غير متاح",
            "admin_url": f"http://{public_ip}:5003/admin" if public_ip != "غير متاح" else "غير متاح",
            "description": "الوصول العام (قد لا يعمل بسبب الراوتر)"
        },
        "ngrok_status": {
            "available": ngrok_available,
            "recommended": ngrok_available,
            "setup_instructions": "ngrok config add-authtoken YOUR_TOKEN"
        },
        "recommendations": [
            "✅ استخدم ngrok للحصول على وصول مضمون",
            "⚠️ الوصول العام قد لا يعمل بسبب إعدادات الراوتر",
            "🔧 تأكد من تشغيل التطبيق على المنفذ 5003"
        ]
    }
    
    return info

def save_to_file(info):
    """حفظ المعلومات في ملف"""
    with open('remote_access_info.txt', 'w', encoding='utf-8') as f:
        f.write("🌐 معلومات الوصول عن بعد\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"📅 التاريخ: {info['timestamp']}\n\n")
        
        f.write("🏠 الوصول المحلي (من نفس الشبكة):\n")
        f.write(f"   الرئيسية: {info['local_access']['url']}\n")
        f.write(f"   لوحة التحكم: {info['local_access']['admin_url']}\n")
        f.write(f"   الوصف: {info['local_access']['description']}\n\n")
        
        f.write("🌍 الوصول العام:\n")
        f.write(f"   IP العام: {info['public_access']['ip']}\n")
        f.write(f"   الرئيسية: {info['public_access']['url']}\n")
        f.write(f"   لوحة التحكم: {info['public_access']['admin_url']}\n")
        f.write(f"   الوصف: {info['public_access']['description']}\n\n")
        
        f.write("🔧 حالة ngrok:\n")
        f.write(f"   متاح: {'نعم' if info['ngrok_status']['available'] else 'لا'}\n")
        f.write(f"   موصى به: {'نعم' if info['ngrok_status']['recommended'] else 'لا'}\n")
        f.write(f"   إعداد: {info['ngrok_status']['setup_instructions']}\n\n")
        
        f.write("💡 التوصيات:\n")
        for rec in info['recommendations']:
            f.write(f"   {rec}\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("📱 شارك هذه المعلومات مع أصدقائك!\n")

def main():
    print("🚀 إنشاء معلومات الوصول عن بعد...")
    print("=" * 50)
    
    info = create_access_info()
    save_to_file(info)
    
    print("✅ تم إنشاء معلومات الوصول!")
    print(f"📁 تم حفظ المعلومات في: remote_access_info.txt")
    print()
    
    print("🏠 الوصول المحلي:")
    print(f"   {info['local_access']['url']}")
    print(f"   {info['local_access']['admin_url']}")
    print()
    
    print("🌍 الوصول العام:")
    print(f"   IP: {info['public_access']['ip']}")
    print(f"   {info['public_access']['url']}")
    print()
    
    if info['ngrok_status']['available']:
        print("🔧 ngrok متاح!")
        print("💡 لتشغيل ngrok:")
        print("   ngrok http 5003")
    else:
        print("⚠️ ngrok غير متاح")
        print("📥 قم بتثبيت ngrok للحصول على وصول مضمون")
    
    print()
    print("📱 راجع ملف remote_access_info.txt للمزيد من التفاصيل")

if __name__ == "__main__":
    main() 