#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import time
import requests
from datetime import datetime

def print_header():
    """طباعة العنوان"""
    print("🌐 إعداد الوصول عن بعد المضمون")
    print("=" * 50)
    print("⚠️ ملاحظة: الوصول من خارج الشبكة قد لا يعمل")
    print("💡 للحصول على وصول مضمون، استخدم ngrok أو خدمة سحابية")
    print()

def check_ngrok_installation():
    """التحقق من تثبيت ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok مثبت")
            return True
        else:
            print("❌ ngrok غير مثبت")
            return False
    except FileNotFoundError:
        print("❌ ngrok غير مثبت")
        return False

def install_ngrok():
    """تثبيت ngrok"""
    print("📥 تثبيت ngrok...")
    
    # التحقق من نظام التشغيل
    if sys.platform == "darwin":  # macOS
        try:
            subprocess.run(['brew', 'install', 'ngrok/ngrok/ngrok'], 
                         check=True)
            print("✅ تم تثبيت ngrok بنجاح")
            return True
        except subprocess.CalledProcessError:
            print("❌ فشل في تثبيت ngrok عبر Homebrew")
            print("💡 قم بتحميل ngrok يدوياً من: https://ngrok.com/download")
            return False
    else:
        print("💡 قم بتحميل ngrok من: https://ngrok.com/download")
        return False

def check_ngrok_auth():
    """التحقق من إعداد authtoken لـ ngrok"""
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok مُعد بشكل صحيح")
            return True
        else:
            print("⚠️ ngrok يحتاج إلى authtoken")
            return False
    except:
        print("❌ خطأ في التحقق من إعداد ngrok")
        return False

def setup_ngrok_auth():
    """إعداد authtoken لـ ngrok"""
    print("🔧 إعداد ngrok...")
    print()
    print("📋 خطوات إعداد ngrok:")
    print("1. اذهب إلى: https://dashboard.ngrok.com/signup")
    print("2. أنشئ حساب مجاني")
    print("3. اذهب إلى: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("4. انسخ الـ authtoken")
    print()
    
    authtoken = input("🔑 أدخل authtoken الخاص بك: ").strip()
    
    if authtoken:
        try:
            subprocess.run(['ngrok', 'config', 'add-authtoken', authtoken], 
                         check=True)
            print("✅ تم إعداد ngrok بنجاح!")
            return True
        except subprocess.CalledProcessError:
            print("❌ فشل في إعداد ngrok")
            return False
    else:
        print("❌ لم يتم إدخال authtoken")
        return False

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

def run_ngrok():
    """تشغيل ngrok"""
    print("🌐 بدء تشغيل ngrok...")
    try:
        process = subprocess.Popen(['ngrok', 'http', '5003'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print("✅ ngrok يعمل الآن!")
        print("📱 انتظر قليلاً للحصول على الرابط...")
        
        # انتظار للحصول على الرابط
        time.sleep(3)
        
        # محاولة الحصول على الرابط من ngrok API
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    print(f"🎉 الرابط العام: {public_url}")
                    print(f"🔧 لوحة التحكم: {public_url}/admin")
                    
                    # حفظ الرابط في ملف
                    with open('remote_dashboard_url.txt', 'w', encoding='utf-8') as f:
                        f.write(f"🌐 رابط الوصول عن بعد\n")
                        f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"🔗 {public_url}\n")
                        f.write(f"🔧 لوحة التحكم: {public_url}/admin\n")
                    
                    print("📁 تم حفظ الرابط في: remote_dashboard_url.txt")
                    return True
        except:
            print("⚠️ لا يمكن الحصول على الرابط تلقائياً")
            print("💡 راجع: http://localhost:4040")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في تشغيل ngrok: {e}")
        return False

def create_alternative_solution():
    """إنشاء حل بديل بدون ngrok"""
    print("🔧 إنشاء حل بديل...")
    
    try:
        subprocess.run(['python3', 'quick_remote_access.py'], check=True)
        print("✅ تم إنشاء معلومات الوصول البديل")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في إنشاء الحل البديل")
        return False

def main():
    """الدالة الرئيسية"""
    print_header()
    
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
    
    # التحقق من ngrok
    if not check_ngrok_installation():
        print("📥 تثبيت ngrok...")
        choice = input("هل تريد تثبيت ngrok؟ (y/n): ").lower()
        if choice == 'y':
            if not install_ngrok():
                print("❌ فشل في تثبيت ngrok")
                print("🔧 إنشاء حل بديل...")
                create_alternative_solution()
                return
        else:
            print("🔧 إنشاء حل بديل...")
            create_alternative_solution()
            return
    
    # التحقق من إعداد ngrok
    if not check_ngrok_auth():
        print("🔧 إعداد ngrok...")
        if not setup_ngrok_auth():
            print("❌ فشل في إعداد ngrok")
            print("🔧 إنشاء حل بديل...")
            create_alternative_solution()
            return
    
    # تشغيل ngrok
    print()
    choice = input("هل تريد تشغيل ngrok الآن؟ (y/n): ").lower()
    if choice == 'y':
        if run_ngrok():
            print("\n🎉 تم إعداد الوصول عن بعد بنجاح!")
            print("📱 شارك الرابط مع أصدقائك!")
        else:
            print("❌ فشل في تشغيل ngrok")
            print("🔧 إنشاء حل بديل...")
            create_alternative_solution()
    else:
        print("🔧 إنشاء حل بديل...")
        create_alternative_solution()

if __name__ == "__main__":
    main() 