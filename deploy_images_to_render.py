#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت رفع الصور إلى Render
Deploy Images to Render Script
"""

import os
import subprocess
import shutil
from pathlib import Path
import logging

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_git_status():
    """التحقق من حالة Git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        logging.error(f"خطأ في التحقق من Git: {e}")
        return None

def add_images_to_git():
    """إضافة الصور إلى Git"""
    logging.info("🔄 إضافة الصور إلى Git...")
    
    # إضافة صور web
    web_uploads = Path("web/static/uploads")
    if web_uploads.exists():
        try:
            subprocess.run(['git', 'add', 'web/static/uploads/'], check=True)
            logging.info("✅ تمت إضافة صور web إلى Git")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ خطأ في إضافة صور web: {e}")
    
    # إضافة صور admin-app
    admin_uploads = Path("admin-app/static/uploads")
    if admin_uploads.exists():
        try:
            subprocess.run(['git', 'add', 'admin-app/static/uploads/'], check=True)
            logging.info("✅ تمت إضافة صور admin-app إلى Git")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ خطأ في إضافة صور admin-app: {e}")

def commit_images():
    """عمل commit للصور"""
    try:
        subprocess.run(['git', 'commit', '-m', '🖼️ إضافة الصور المحدثة للـ deployment'], check=True)
        logging.info("✅ تم عمل commit للصور")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ خطأ في عمل commit: {e}")
        return False

def push_to_render():
    """رفع التغييرات إلى Render"""
    try:
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        logging.info("✅ تم رفع الصور إلى Render")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ خطأ في الرفع إلى Render: {e}")
        return False

def get_image_stats():
    """إحصائيات الصور"""
    web_count = 0
    admin_count = 0
    
    web_uploads = Path("web/static/uploads")
    if web_uploads.exists():
        web_count = len([f for f in web_uploads.iterdir() 
                        if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}])
    
    admin_uploads = Path("admin-app/static/uploads")
    if admin_uploads.exists():
        admin_count = len([f for f in admin_uploads.iterdir() 
                          if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}])
    
    return web_count, admin_count

def main():
    """الدالة الرئيسية"""
    print("🚀 سكريبت رفع الصور إلى Render")
    print("=" * 50)
    
    # التحقق من وجود Git
    if not Path(".git").exists():
        logging.error("❌ هذا المجلد ليس Git repository")
        return
    
    # إحصائيات الصور
    web_count, admin_count = get_image_stats()
    print(f"📊 عدد الصور في web: {web_count}")
    print(f"📊 عدد الصور في admin-app: {admin_count}")
    print()
    
    if web_count == 0 and admin_count == 0:
        print("⚠️  لا توجد صور للمزامنة")
        return
    
    # التحقق من حالة Git
    git_status = check_git_status()
    if git_status:
        print("📋 الملفات المتغيرة:")
        print(git_status)
        print()
    
    # إضافة الصور إلى Git
    add_images_to_git()
    
    # عمل commit
    if commit_images():
        print("🔄 رفع الصور إلى Render...")
        if push_to_render():
            print()
            print("🎉 تم رفع الصور بنجاح إلى Render!")
            print("⏳ انتظر بضع دقائق حتى يتم تحديث الموقع")
            print("🌐 تحقق من موقعك على Render")
        else:
            print("❌ فشل في رفع الصور إلى Render")
    else:
        print("❌ فشل في عمل commit للصور")

if __name__ == "__main__":
    main()
