#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لإصلاح مشكلة قاعدة البيانات في تطبيق الويب
"""

import sys
import os

# إضافة مسار التطبيق
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def fix_web_app():
    """إصلاح تطبيق الويب"""
    try:
        print("🔧 إصلاح تطبيق الويب...")
        
        # استيراد التطبيق
        from web.app import app
        
        with app.app_context():
            # اختبار استيراد النماذج
            from web.models import Product, Comment, ProductImage, Order, OrderStatusHistory
            
            # اختبار استعلام بسيط
            product_count = Product.query.count()
            print(f"✅ عدد المنتجات في تطبيق الويب: {product_count}")
            
            # اختبار إنشاء منتج تجريبي
            test_product = Product(
                name='Test Product Web',
                description='Test Description Web',
                price=15.0
            )
            from web.models import db
            db.session.add(test_product)
            db.session.commit()
            print("✅ تم إنشاء منتج تجريبي في تطبيق الويب")
            
            # حذف المنتج التجريبي
            db.session.delete(test_product)
            db.session.commit()
            print("✅ تم حذف المنتج التجريبي من تطبيق الويب")
            
            print("✅ تطبيق الويب يعمل بشكل صحيح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في تطبيق الويب: {e}")
        return False

def test_web_app_routes():
    """اختبار routes تطبيق الويب"""
    try:
        print("🌐 اختبار routes تطبيق الويب...")
        
        from web.app import app
        
        # اختبار routes أساسية
        with app.test_client() as client:
            # اختبار الصفحة الرئيسية
            response = client.get('/')
            if response.status_code == 200:
                print("✅ الصفحة الرئيسية تعمل")
            else:
                print(f"❌ خطأ في الصفحة الرئيسية: {response.status_code}")
                return False
            
            # اختبار API المنتجات
            response = client.get('/api/products')
            if response.status_code == 200:
                print("✅ API المنتجات يعمل")
            else:
                print(f"❌ خطأ في API المنتجات: {response.status_code}")
                return False
            
            print("✅ جميع routes تعمل بشكل صحيح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار routes: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح تطبيق الويب")
    print("=" * 50)
    
    # إصلاح تطبيق الويب
    web_success = fix_web_app()
    
    # اختبار routes
    routes_success = test_web_app_routes()
    
    print("\n" + "=" * 50)
    if web_success and routes_success:
        print("🎉 تم إصلاح تطبيق الويب بنجاح!")
        print("🚀 يمكنك الآن تشغيل التطبيق")
    else:
        print("❌ فشل في إصلاح تطبيق الويب")
        if not web_success:
            print("   - مشكلة في قاعدة البيانات")
        if not routes_success:
            print("   - مشكلة في routes")

if __name__ == "__main__":
    main()
