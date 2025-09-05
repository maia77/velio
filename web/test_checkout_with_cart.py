#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار عملية checkout مع سلة مشتريات
"""

import requests
import json

def test_checkout_with_cart():
    """اختبار عملية checkout مع سلة مشتريات"""
    base_url = "http://localhost:5003"
    session = requests.Session()
    
    print("🧪 بدء اختبار عملية checkout مع سلة مشتريات...")
    
    # 1. إضافة منتج إلى السلة
    print("1️⃣ إضافة منتج إلى السلة...")
    try:
        # أولاً نحتاج إلى معرفة المنتجات المتاحة
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ خطأ في تحميل الصفحة الرئيسية: {response.status_code}")
            return False
        
        # إضافة منتج حقيقي إلى السلة (ID 16)
        cart_data = {'product_id': 16, 'quantity': 1}
        response = session.post(f"{base_url}/cart/add", json=cart_data, headers={'Content-Type': 'application/json'})
        print(f"📊 حالة إضافة المنتج: {response.status_code}")
        
        if response.status_code != 200:
            print("⚠️ لم يتم إضافة المنتج إلى السلة، لكن سنتابع الاختبار")
        
    except Exception as e:
        print(f"⚠️ خطأ في إضافة المنتج: {e}")
    
    # 2. اختبار صفحة checkout
    print("2️⃣ اختبار صفحة checkout...")
    try:
        response = session.get(f"{base_url}/checkout")
        if response.status_code == 200:
            print("✅ صفحة checkout تعمل بشكل صحيح")
        else:
            print(f"❌ خطأ في صفحة checkout: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    # 3. اختبار إرسال طلب checkout
    print("3️⃣ اختبار إرسال طلب checkout...")
    try:
        data = {
            'name': 'اختبار العميل',
            'phone': '1234567890',
            'address': 'عنوان اختبار',
            'email': 'test@example.com',
            'location': 'sanaa',
            'payment_method': 'yemen_local'
        }
        
        response = session.post(f"{base_url}/checkout", data=data)
        print(f"📊 حالة الاستجابة: {response.status_code}")
        
        if response.status_code == 200:
            if "شكراً" in response.text or "thank" in response.text.lower():
                print("✅ تم التوجه إلى صفحة الشكر بنجاح!")
                return True
            else:
                print("⚠️ تم إرسال الطلب ولكن لم يتم التوجه إلى صفحة الشكر")
                print("🔍 البحث عن رسائل الخطأ...")
                if "سلتك فارغة" in response.text:
                    print("❌ المشكلة: السلة فارغة!")
                elif "يرجى تعبئة" in response.text:
                    print("❌ المشكلة: بيانات ناقصة!")
                elif "إتمام الطلب" in response.text:
                    print("❌ المشكلة: عاد إلى صفحة checkout!")
                else:
                    print("❌ مشكلة غير معروفة")
                    print("📄 أول 500 حرف من الاستجابة:")
                    print(response.text[:500])
                return False
        else:
            print(f"❌ خطأ في إرسال الطلب: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في إرسال الطلب: {e}")
        return False

if __name__ == "__main__":
    success = test_checkout_with_cart()
    if success:
        print("🎉 اختبار checkout نجح!")
    else:
        print("❌ اختبار checkout فشل!")
