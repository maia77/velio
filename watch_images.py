#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مراقب الصور التلقائي - يتابع تغييرات الصور ويقوم بالمزامنة تلقائياً
Auto Image Watcher - Monitors image changes and syncs automatically
"""

import os
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ImageSyncHandler(FileSystemEventHandler):
    """معالج أحداث تغيير الملفات"""
    
    def __init__(self):
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        self.last_sync = 0
        self.sync_delay = 2  # تأخير 2 ثانية لتجنب المزامنة المتكررة
    
    def is_image_file(self, file_path):
        """التحقق من أن الملف صورة"""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def on_created(self, event):
        """عند إنشاء ملف جديد"""
        if not event.is_directory and self.is_image_file(event.src_path):
            self.schedule_sync("إنشاء ملف جديد")
    
    def on_modified(self, event):
        """عند تعديل ملف"""
        if not event.is_directory and self.is_image_file(event.src_path):
            self.schedule_sync("تعديل ملف")
    
    def on_moved(self, event):
        """عند نقل ملف"""
        if not event.is_directory and self.is_image_file(event.dest_path):
            self.schedule_sync("نقل ملف")
    
    def schedule_sync(self, reason):
        """جدولة المزامنة مع تأخير"""
        current_time = time.time()
        if current_time - self.last_sync > self.sync_delay:
            logging.info(f"📁 {reason}: {Path(reason).name if reason else 'ملف'}")
            self.sync_images()
            self.last_sync = current_time
    
    def sync_images(self):
        """تنفيذ المزامنة"""
        try:
            # تشغيل سكريبت المزامنة
            result = subprocess.run(
                ['python3', 'auto_sync_images.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logging.info("✅ تمت المزامنة التلقائية بنجاح")
            else:
                logging.error(f"❌ خطأ في المزامنة: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logging.error("⏰ انتهت مهلة المزامنة")
        except Exception as e:
            logging.error(f"❌ خطأ غير متوقع: {e}")

def main():
    """الدالة الرئيسية"""
    print("👁️  مراقب الصور التلقائي")
    print("=" * 40)
    print("📁 مراقبة مجلدات الصور...")
    print("⏹️  اضغط Ctrl+C للإيقاف")
    print()
    
    # إنشاء المعالج
    event_handler = ImageSyncHandler()
    observer = Observer()
    
    # إضافة مراقبين للمجلدين
    base_dir = Path(__file__).parent
    web_uploads = base_dir / "web" / "static" / "uploads"
    admin_uploads = base_dir / "admin-app" / "static" / "uploads"
    
    # إنشاء المجلدات إذا لم تكن موجودة
    web_uploads.mkdir(parents=True, exist_ok=True)
    admin_uploads.mkdir(parents=True, exist_ok=True)
    
    observer.schedule(event_handler, str(web_uploads), recursive=False)
    observer.schedule(event_handler, str(admin_uploads), recursive=False)
    
    # بدء المراقبة
    observer.start()
    logging.info(f"👁️  بدء مراقبة: {web_uploads}")
    logging.info(f"👁️  بدء مراقبة: {admin_uploads}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  إيقاف المراقب...")
        observer.stop()
    
    observer.join()
    print("✅ تم إيقاف المراقب")

if __name__ == "__main__":
    main()

