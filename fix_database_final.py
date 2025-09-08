#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت نهائي لإصلاح مشاكل قاعدة البيانات
"""

import sys
import os

# إضافة مسارات التطبيق
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'admin-app'))

def test_web_app():
    """اختبار تطبيق الويب"""
    try:
        print("🌐 اختبار تطبيق الويب...")
        
        # استيراد التطبيق
        from web.app import app
        
        with app.app_context():
            # اختبار استيراد النماذج
            from web.models import Product, Comment, ProductImage, Order, OrderStatusHistory
            
            # اختبار استعلام بسيط
            product_count = Product.query.count()
            print(f"✅ عدد المنتجات في تطبيق الويب: {product_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في تطبيق الويب: {e}")
        return False

def test_admin_app():
    """اختبار تطبيق الإدارة"""
    try:
        print("🔧 اختبار تطبيق الإدارة...")
        
        # استيراد التطبيق
        from admin_app_fixed import app
        
        with app.app_context():
            # اختبار استيراد النماذج
            from admin_app_fixed import Product, ProductImage
            
            # اختبار استعلام بسيط
            product_count = Product.query.count()
            print(f"✅ عدد المنتجات في تطبيق الإدارة: {product_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في تطبيق الإدارة: {e}")
        return False

def test_database_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        print("🔍 اختبار الاتصال بقاعدة البيانات...")
        
        from shared_database_config_fallback import test_connection
        success, message = test_connection()
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار الاتصال: {e}")
        return False

def test_crud_operations():
    """اختبار عمليات CRUD"""
    try:
        print("📝 اختبار عمليات CRUD...")
        
        from admin_app_fixed import app, db, Product
        
        with app.app_context():
            # Create
            test_product = Product(
                name='Test Product Final',
                description='Test Description Final',
                price=25.0,
                category='Test Category Final'
            )
            db.session.add(test_product)
            db.session.commit()
            print("✅ Create: تم إنشاء منتج بنجاح")
            
            # Read
            found_product = Product.query.filter_by(name='Test Product Final').first()
            if found_product:
                print(f"✅ Read: تم العثور على المنتج - ID: {found_product.id}")
            else:
                print("❌ Read: فشل في العثور على المنتج")
                return False
            
            # Update
            found_product.price = 30.0
            db.session.commit()
            print("✅ Update: تم تحديث سعر المنتج")
            
            # Delete
            db.session.delete(found_product)
            db.session.commit()
            print("✅ Delete: تم حذف المنتج")
            
            print("✅ جميع عمليات CRUD تعمل بشكل صحيح")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار عمليات CRUD: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔧 اختبار نهائي لقاعدة البيانات")
    print("=" * 50)
    
    # اختبار الاتصال بقاعدة البيانات
    connection_success = test_database_connection()
    
    # اختبار تطبيق الإدارة
    admin_success = test_admin_app()
    
    # اختبار تطبيق الويب
    web_success = test_web_app()
    
    # اختبار عمليات CRUD
    crud_success = test_crud_operations()
    
    print("\n" + "=" * 50)
    print("📊 تقرير النتائج:")
    print(f"🔍 الاتصال بقاعدة البيانات: {'✅' if connection_success else '❌'}")
    print(f"🔧 تطبيق الإدارة: {'✅' if admin_success else '❌'}")
    print(f"🌐 تطبيق الويب: {'✅' if web_success else '❌'}")
    print(f"📝 عمليات CRUD: {'✅' if crud_success else '❌'}")
    
    if connection_success and admin_success and crud_success:
        print("\n🎉 قاعدة البيانات تعمل بشكل صحيح!")
        if not web_success:
            print("⚠️ تطبيق الويب يحتاج إصلاح إضافي")
        print("🚀 يمكنك تشغيل التطبيقات")
    else:
        print("\n❌ هناك مشاكل تحتاج إصلاح")

if __name__ == "__main__":
    main()
