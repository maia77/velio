#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إعداد شهادة SSL للتطبيق المحلي
هذا الملف ينشئ شهادة SSL ذاتية التوقيع للتطوير المحلي
"""

import os
import ssl
import subprocess
from pathlib import Path

def create_ssl_certificate():
    """إنشاء شهادة SSL ذاتية التوقيع للتطوير المحلي"""
    
    # إنشاء مجلد الشهادات
    cert_dir = Path("ssl_certs")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # فحص وجود الشهادات
    if cert_file.exists() and key_file.exists():
        print("✅ شهادات SSL موجودة بالفعل")
        return str(cert_file), str(key_file)
    
    print("🔐 إنشاء شهادة SSL جديدة...")
    
    try:
        # إنشاء شهادة SSL ذاتية التوقيع
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", str(key_file),
            "-out", str(cert_file),
            "-days", "365",
            "-nodes",
            "-subj", "/C=SA/ST=Riyadh/L=Riyadh/O=Velio/OU=IT/CN=localhost"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ تم إنشاء شهادة SSL بنجاح")
            print(f"📁 الشهادة: {cert_file}")
            print(f"🔑 المفتاح: {key_file}")
            return str(cert_file), str(key_file)
        else:
            print(f"❌ خطأ في إنشاء الشهادة: {result.stderr}")
            return None, None
            
    except FileNotFoundError:
        print("❌ OpenSSL غير مثبت. يرجى تثبيت OpenSSL أولاً")
        print("💡 على macOS: brew install openssl")
        print("💡 على Ubuntu: sudo apt-get install openssl")
        return None, None
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return None, None

def create_ssl_context():
    """إنشاء سياق SSL للتطبيق"""
    cert_file, key_file = create_ssl_certificate()
    
    if not cert_file or not key_file:
        return None
    
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        return context
    except Exception as e:
        print(f"❌ خطأ في إنشاء سياق SSL: {e}")
        return None

if __name__ == "__main__":
    print("🔐 إعداد شهادة SSL للتطبيق المحلي")
    print("=" * 50)
    
    cert_file, key_file = create_ssl_certificate()
    
    if cert_file and key_file:
        print("\n✅ تم إعداد SSL بنجاح!")
        print(f"🌐 يمكنك الآن الوصول للتطبيق عبر: https://localhost:5001")
        print("⚠️  قد يظهر تحذير أمان في المتصفح - اضغط 'متابعة' أو 'Advanced' ثم 'Proceed'")
    else:
        print("\n❌ فشل في إعداد SSL")
        print("💡 يمكنك تشغيل التطبيق بدون SSL على: http://localhost:5001")
