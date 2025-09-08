#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لإصلاح مشاكل تهيئة قاعدة البيانات
"""

import sys
import os

# إضافة مسارات التطبيق
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin-app'))

def fix_web_database():
    """إصلاح قاعدة البيانات لتطبيق الويب"""
    try:
        print("🔧 إصلاح قاعدة البيانات لتطبيق الويب...")
        
        # استيراد التطبيق وإعداداته
        from web.app import app, db
        from web.models import Product, Comment, ProductImage, Order, OrderStatusHistory
        
        with app.app_context():
            # إنشاء جميع الجداول
            print("📋 إنشاء الجداول...")
            db.create_all()
            
            # اختبار قاعدة البيانات
            print("🧪 اختبار قاعدة البيانات...")
            
            # اختبار استعلام بسيط
            product_count = Product.query.count()
            print(f"✅ عدد المنتجات: {product_count}")
            
            # اختبار إنشاء منتج تجريبي
            test_product = Product(
                name='Test Product',
                description='Test Description',
                price=10.0
            )
            db.session.add(test_product)
            db.session.commit()
            print("✅ تم إنشاء منتج تجريبي بنجاح")
            
            # حذف المنتج التجريبي
            db.session.delete(test_product)
            db.session.commit()
            print("✅ تم حذف المنتج التجريبي بنجاح")
            
            print("✅ تم إصلاح قاعدة البيانات لتطبيق الويب بنجاح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة بيانات تطبيق الويب: {e}")
        return False

def fix_admin_database():
    """إصلاح قاعدة البيانات لتطبيق الإدارة"""
    try:
        print("🔧 إصلاح قاعدة البيانات لتطبيق الإدارة...")
        
        # استيراد التطبيق وإعداداته
        from admin_app_fixed import app, db, Product, ProductImage
        
        with app.app_context():
            # إنشاء جميع الجداول
            print("📋 إنشاء الجداول...")
            db.create_all()
            
            # اختبار قاعدة البيانات
            print("🧪 اختبار قاعدة البيانات...")
            
            # اختبار استعلام بسيط
            product_count = Product.query.count()
            print(f"✅ عدد المنتجات: {product_count}")
            
            print("✅ تم إصلاح قاعدة البيانات لتطبيق الإدارة بنجاح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة بيانات تطبيق الإدارة: {e}")
        return False

def test_database_operations():
    """اختبار عمليات قاعدة البيانات"""
    try:
        print("🧪 اختبار عمليات قاعدة البيانات...")
        
        from web.app import app, db
        from web.models import Product
        
        with app.app_context():
            # اختبار CRUD operations
            print("📝 اختبار عمليات CRUD...")
            
            # Create
            test_product = Product(
                name='Test Product CRUD',
                description='Test Description CRUD',
                price=15.0,
                category='Test Category'
            )
            db.session.add(test_product)
            db.session.commit()
            print("✅ Create: تم إنشاء منتج بنجاح")
            
            # Read
            found_product = Product.query.filter_by(name='Test Product CRUD').first()
            if found_product:
                print(f"✅ Read: تم العثور على المنتج - ID: {found_product.id}")
            else:
                print("❌ Read: فشل في العثور على المنتج")
                return False
            
            # Update
            found_product.price = 20.0
            db.session.commit()
            print("✅ Update: تم تحديث سعر المنتج")
            
            # Delete
            db.session.delete(found_product)
            db.session.commit()
            print("✅ Delete: تم حذف المنتج")
            
            print("✅ جميع عمليات CRUD تعمل بشكل صحيح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار عمليات قاعدة البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 إصلاح مشاكل قاعدة البيانات")
    print("=" * 50)
    
    # إصلاح قاعدة البيانات لتطبيق الويب
    web_success = fix_web_database()
    
    # إصلاح قاعدة البيانات لتطبيق الإدارة
    admin_success = fix_admin_database()
    
    # اختبار عمليات قاعدة البيانات
    test_success = test_database_operations()
    
    print("\n" + "=" * 50)
    if web_success and admin_success and test_success:
        print("🎉 تم إصلاح جميع مشاكل قاعدة البيانات بنجاح!")
        print("🚀 يمكنك الآن تشغيل التطبيقين بأمان")
    else:
        print("❌ فشل في إصلاح بعض مشاكل قاعدة البيانات")
        if not web_success:
            print("   - مشكلة في تطبيق الويب")
        if not admin_success:
            print("   - مشكلة في تطبيق الإدارة")
        if not test_success:
            print("   - مشكلة في اختبار العمليات")

if __name__ == "__main__":
    main()
