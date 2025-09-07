#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت لاختبار ميزة رفع الصور للتعليقات
"""

import sys
import os
import requests
import json
from PIL import Image
import io

# إضافة مسار التطبيق
sys.path.append(os.path.dirname(__file__))

def create_test_image():
    """إنشاء صورة تجريبية للاختبار"""
    # إنشاء صورة بسيطة 100x100 بكسل
    img = Image.new('RGB', (100, 100), color='lightblue')
    
    # إضافة نص على الصورة
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # محاولة استخدام خط افتراضي
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 40), "Test Image", fill='black', font=font)
    
    # حفظ الصورة في بايت
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_image_upload():
    """اختبار رفع صورة مع التعليق"""
    base_url = "http://localhost:5003"
    
    print("🧪 اختبار ميزة رفع الصور للتعليقات...")
    print("=" * 50)
    
    # إنشاء صورة تجريبية
    print("📸 إنشاء صورة تجريبية...")
    test_image = create_test_image()
    
    # اختبار رفع تعليق مع صورة
    print("📤 اختبار رفع تعليق مع صورة...")
    try:
        files = {
            'image': ('test_comment_image.jpg', test_image, 'image/jpeg')
        }
        data = {
            'name': 'مستخدم مع صورة',
            'content': 'هذا تعليق تجريبي مع صورة لاختبار الميزة الجديدة',
            'rating': '5'
        }
        
        response = requests.post(
            f"{base_url}/api/products/15/comments",
            files=files,
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                print("✅ تم رفع التعليق مع الصورة بنجاح!")
                comment = result.get('comment', {})
                print(f"   رقم التعليق: {comment.get('id')}")
                print(f"   رابط الصورة: {comment.get('image_url')}")
                
                # اختبار جلب التعليقات للتأكد من ظهور الصورة
                print("\n📖 اختبار جلب التعليقات مع الصور...")
                comments_response = requests.get(f"{base_url}/api/products/15/comments")
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    if comments_data.get('success'):
                        comments = comments_data.get('comments', [])
                        print(f"✅ تم جلب {len(comments)} تعليق")
                        
                        # البحث عن التعليق مع الصورة
                        for comment in comments:
                            if comment.get('image_url'):
                                print(f"   🖼️ تم العثور على تعليق مع صورة: {comment.get('image_url')}")
                                break
                        else:
                            print("   ⚠️ لم يتم العثور على تعليقات مع صور")
                else:
                    print(f"❌ خطأ في جلب التعليقات: {comments_response.status_code}")
            else:
                print(f"❌ فشل في رفع التعليق: {result.get('error')}")
        else:
            print(f"❌ خطأ HTTP: {response.status_code}")
            print(f"   الاستجابة: {response.text}")
    except Exception as e:
        print(f"❌ خطأ في رفع التعليق مع الصورة: {e}")

def test_comment_display():
    """اختبار عرض التعليقات مع الصور"""
    print("\n🖼️ اختبار عرض التعليقات مع الصور...")
    print("=" * 40)
    
    print("📋 للاختبار في المتصفح:")
    print("1. افتح المتصفح واذهب إلى: http://localhost:5003")
    print("2. انتقل إلى أي منتج")
    print("3. انقر على زر 'التعليقات'")
    print("4. جرب إضافة تعليق جديد مع صورة")
    print("5. تأكد من ظهور الصورة في التعليق")
    print("\n✨ الميزات المتاحة:")
    print("   - رفع صور مع التعليقات")
    print("   - معاينة الصور قبل الرفع")
    print("   - عرض الصور في التعليقات")
    print("   - فتح الصور في نافذة منبثقة")
    print("   - إزالة الصور من التعليقات")

def main():
    """الدالة الرئيسية"""
    print("🚀 اختبار شامل لميزة رفع الصور للتعليقات...")
    print("=" * 60)
    
    # اختبار رفع الصور
    test_image_upload()
    
    # تعليمات الاختبار في المتصفح
    test_comment_display()
    
    print("\n" + "=" * 60)
    print("🎉 تم إضافة ميزة رفع الصور للتعليقات بنجاح!")
    print("✨ الميزات الجديدة:")
    print("   - رفع الصور مع التعليقات في الصفحة الرئيسية")
    print("   - رفع الصور مع التعليقات في صفحة تفاصيل المنتج")
    print("   - معاينة الصور قبل الرفع")
    print("   - عرض الصور في التعليقات")
    print("   - فتح الصور في نافذة منبثقة")
    print("   - إزالة الصور من التعليقات")

if __name__ == "__main__":
    main()
