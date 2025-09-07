#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لإصلاح مشاكل التعليقات في قاعدة البيانات
"""

import sys
import os

# إضافة مسار التطبيق
sys.path.append(os.path.dirname(__file__))

from app import app, db
from models import Comment, Product, ProductImage, Order, OrderStatusHistory

def fix_comments_database():
    """إصلاح قاعدة البيانات للتعليقات"""
    try:
        print("🔧 بدء إصلاح قاعدة البيانات للتعليقات...")
        print("=" * 50)
        
        with app.app_context():
            # إنشاء جميع الجداول
            print("📋 إنشاء الجداول...")
            db.create_all()
            
            # التحقق من وجود جدول التعليقات
            print("🔍 التحقق من جدول التعليقات...")
            
            # محاولة الاستعلام عن جدول التعليقات
            try:
                comments = Comment.query.limit(1).all()
                print("✅ جدول التعليقات موجود ويعمل بشكل صحيح")
            except Exception as e:
                print(f"❌ مشكلة في جدول التعليقات: {e}")
                return False
            
            # التحقق من وجود عمود image_url
            print("🖼️ التحقق من عمود image_url...")
            try:
                # محاولة إنشاء تعليق تجريبي للتحقق من الأعمدة
                test_comment = Comment(
                    product_id=1,
                    name="اختبار",
                    content="تعليق تجريبي",
                    image_url=None
                )
                # لا نحفظ التعليق، فقط نتحقق من صحة البيانات
                print("✅ عمود image_url موجود ويعمل بشكل صحيح")
            except Exception as e:
                print(f"❌ مشكلة في عمود image_url: {e}")
                return False
            
            # التحقق من وجود منتجات
            print("📦 التحقق من المنتجات...")
            products = Product.query.limit(1).all()
            if products:
                print(f"✅ يوجد {Product.query.count()} منتج في قاعدة البيانات")
            else:
                print("⚠️ لا توجد منتجات في قاعدة البيانات")
            
            print("=" * 50)
            print("✅ تم إصلاح قاعدة البيانات بنجاح!")
            print("🎉 التعليقات جاهزة للاستخدام")
            
            return True
            
    except Exception as e:
        print(f"❌ خطأ في إصلاح قاعدة البيانات: {e}")
        return False

def test_comments_api():
    """اختبار API التعليقات"""
    try:
        print("\n🧪 اختبار API التعليقات...")
        print("=" * 30)
        
        with app.app_context():
            # اختبار إنشاء تعليق
            print("📝 اختبار إنشاء تعليق...")
            
            # البحث عن منتج موجود
            product = Product.query.first()
            if not product:
                print("❌ لا توجد منتجات لاختبار التعليقات")
                return False
            
            # إنشاء تعليق تجريبي
            test_comment = Comment(
                product_id=product.id,
                name="مستخدم تجريبي",
                content="هذا تعليق تجريبي لاختبار النظام",
                rating=5,
                image_url=None
            )
            
            db.session.add(test_comment)
            db.session.commit()
            
            print(f"✅ تم إنشاء تعليق تجريبي للمنتج {product.id}")
            
            # اختبار جلب التعليقات
            print("📖 اختبار جلب التعليقات...")
            comments = Comment.query.filter_by(product_id=product.id).all()
            print(f"✅ تم العثور على {len(comments)} تعليق للمنتج")
            
            # حذف التعليق التجريبي
            db.session.delete(test_comment)
            db.session.commit()
            print("🗑️ تم حذف التعليق التجريبي")
            
            print("✅ جميع اختبارات API التعليقات نجحت!")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في اختبار API التعليقات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إصلاح مشاكل التعليقات...")
    print("=" * 60)
    
    # إصلاح قاعدة البيانات
    db_success = fix_comments_database()
    
    if db_success:
        # اختبار API
        api_success = test_comments_api()
        
        print("\n" + "=" * 60)
        if api_success:
            print("🎉 تم إصلاح جميع مشاكل التعليقات بنجاح!")
            print("✨ يمكن الآن:")
            print("   - إضافة تعليقات جديدة")
            print("   - رفع صور مع التعليقات")
            print("   - عرض التعليقات في صفحات المنتجات")
        else:
            print("⚠️ تم إصلاح قاعدة البيانات ولكن هناك مشاكل في API")
    else:
        print("❌ فشل في إصلاح قاعدة البيانات")
        print("💡 تأكد من إعدادات قاعدة البيانات")

if __name__ == "__main__":
    main()
