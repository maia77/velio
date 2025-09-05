#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار عملية checkout
"""

import requests
import json

def test_checkout():
    """اختبار عملية checkout"""
    base_url = "http://localhost:5003"
    
    print("🧪 بدء اختبار عملية checkout...")
    
    # 1. اختبار صفحة checkout
    print("1️⃣ اختبار صفحة checkout...")
    try:
        response = requests.get(f"{base_url}/checkout")
        if response.status_code == 200:
            print("✅ صفحة checkout تعمل بشكل صحيح")
        else:
            print(f"❌ خطأ في صفحة checkout: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    # 2. اختبار إرسال طلب checkout (مع بيانات وهمية)
    print("2️⃣ اختبار إرسال طلب checkout...")
    try:
        data = {
            'name': 'اختبار العميل',
            'phone': '1234567890',
            'address': 'عنوان اختبار',
            'email': 'test@example.com',
            'location': 'sanaa',
            'payment_method': 'yemen_local'
        }
        
        response = requests.post(f"{base_url}/checkout", data=data)
        print(f"📊 حالة الاستجابة: {response.status_code}")
        
        if response.status_code == 200:
            if "شكراً" in response.text or "thank" in response.text.lower():
                print("✅ تم التوجه إلى صفحة الشكر بنجاح!")
                return True
            else:
                print("⚠️ تم إرسال الطلب ولكن لم يتم التوجه إلى صفحة الشكر")
                print("📄 محتوى الاستجابة:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
                return False
        else:
            print(f"❌ خطأ في إرسال الطلب: {response.status_code}")
            print("📄 محتوى الاستجابة:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الطلب: {e}")
        return False

if __name__ == "__main__":
    success = test_checkout()
    if success:
        print("🎉 اختبار checkout نجح!")
    else:
        print("❌ اختبار checkout فشل!")
