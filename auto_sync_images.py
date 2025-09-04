#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المزامنة التلقائية للصور بين التطبيقين
Auto Image Sync System between Applications
"""

import os
import shutil
import time
import hashlib
from pathlib import Path
import logging

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_sync.log'),
        logging.StreamHandler()
    ]
)

class ImageSyncManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.web_uploads = self.base_dir / "web" / "static" / "uploads"
        self.admin_uploads = self.base_dir / "admin-app" / "static" / "uploads"
        
        # إنشاء المجلدات إذا لم تكن موجودة
        self.web_uploads.mkdir(parents=True, exist_ok=True)
        self.admin_uploads.mkdir(parents=True, exist_ok=True)
        
        # أنواع الملفات المدعومة
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        
    def get_file_hash(self, file_path):
        """حساب hash للملف للتحقق من التغييرات"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def sync_images(self):
        """مزامنة الصور بين المجلدين"""
        logging.info("🔄 بدء مزامنة الصور...")
        
        synced_count = 0
        
        # مزامنة من admin-app إلى web
        for file_path in self.admin_uploads.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                target_path = self.web_uploads / file_path.name
                
                # نسخ الملف إذا لم يكن موجود أو إذا تغير
                if not target_path.exists() or self.get_file_hash(file_path) != self.get_file_hash(target_path):
                    try:
                        shutil.copy2(file_path, target_path)
                        logging.info(f"📁 نسخ: {file_path.name} → web")
                        synced_count += 1
                    except Exception as e:
                        logging.error(f"❌ خطأ في نسخ {file_path.name}: {e}")
        
        # مزامنة من web إلى admin-app
        for file_path in self.web_uploads.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                target_path = self.admin_uploads / file_path.name
                
                # نسخ الملف إذا لم يكن موجود أو إذا تغير
                if not target_path.exists() or self.get_file_hash(file_path) != self.get_file_hash(target_path):
                    try:
                        shutil.copy2(file_path, target_path)
                        logging.info(f"📁 نسخ: {file_path.name} → admin-app")
                        synced_count += 1
                    except Exception as e:
                        logging.error(f"❌ خطأ في نسخ {file_path.name}: {e}")
        
        logging.info(f"✅ تمت المزامنة بنجاح! تم مزامنة {synced_count} ملف")
        return synced_count
    
    def get_stats(self):
        """إحصائيات الملفات"""
        web_count = len([f for f in self.web_uploads.iterdir() 
                        if f.is_file() and f.suffix.lower() in self.supported_extensions])
        admin_count = len([f for f in self.admin_uploads.iterdir() 
                          if f.is_file() and f.suffix.lower() in self.supported_extensions])
        
        return {
            'web_count': web_count,
            'admin_count': admin_count,
            'web_path': str(self.web_uploads),
            'admin_path': str(self.admin_uploads)
        }

def main():
    """الدالة الرئيسية"""
    print("🖼️  نظام المزامنة التلقائية للصور")
    print("=" * 50)
    
    sync_manager = ImageSyncManager()
    
    # عرض الإحصائيات الحالية
    stats = sync_manager.get_stats()
    print(f"📊 الصور في web: {stats['web_count']}")
    print(f"📊 الصور في admin-app: {stats['admin_count']}")
    print()
    
    # تنفيذ المزامنة
    synced = sync_manager.sync_images()
    
    # عرض الإحصائيات النهائية
    stats = sync_manager.get_stats()
    print(f"📊 الصور في web: {stats['web_count']}")
    print(f"📊 الصور في admin-app: {stats['admin_count']}")
    
    if synced > 0:
        print(f"✅ تم مزامنة {synced} صورة جديدة")
    else:
        print("ℹ️  جميع الصور متزامنة بالفعل")

if __name__ == "__main__":
    main()
