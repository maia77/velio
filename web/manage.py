#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف إدارة مشروع Velio
"""

import os
import sys
import subprocess
from flask.cli import FlaskGroup
from app import app

cli = FlaskGroup(app)

@cli.command()
def run():
    """تشغيل التطبيق"""
    print("🚀 بدء تشغيل موقع Velio...")
    app.run(host='0.0.0.0', port=5003, debug=True)

@cli.command()
def test():
    """تشغيل الاختبارات"""
    print("🧪 تشغيل اختبارات Velio...")
    subprocess.run([sys.executable, 'tests.py'])

@cli.command()
def install():
    """تثبيت المكتبات المطلوبة"""
    print("📦 تثبيت المكتبات المطلوبة...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

@cli.command()
def translate():
    """تحديث ملفات الترجمة"""
    print("🌍 تحديث ملفات الترجمة...")
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'extract', '-F', 'babel.cfg', '-k', '_l', '-o', 'messages.pot', '.'])
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'init', '-i', 'messages.pot', 'translations'])
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'compile', '-d', 'translations'])

@cli.command()
def clean():
    """تنظيف الملفات المؤقتة"""
    print("🧹 تنظيف الملفات المؤقتة...")
    files_to_remove = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '*.log'
    ]
    
    for pattern in files_to_remove:
        if os.path.exists(pattern):
            if os.path.isdir(pattern):
                import shutil
                shutil.rmtree(pattern)
            else:
                os.remove(pattern)
    
    print("✅ تم تنظيف الملفات المؤقتة")

@cli.command()
def setup():
    """إعداد المشروع بالكامل"""
    print("🔧 إعداد مشروع Velio...")
    
    # تثبيت المكتبات
    print("📦 تثبيت المكتبات...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # إنشاء المجلدات المطلوبة
    print("📁 إنشاء المجلدات...")
    folders = ['static/uploads', 'static/images', 'logs']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # تحديث الترجمات
    print("🌍 تحديث الترجمات...")
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'extract', '-F', 'babel.cfg', '-k', '_l', '-o', 'messages.pot', '.'])
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'init', '-i', 'messages.pot', 'translations'])
    subprocess.run([sys.executable, '-m', 'flask', 'babel', 'compile', '-d', 'translations'])
    
    print("✅ تم إعداد المشروع بنجاح!")

@cli.command()
def deploy():
    """إعداد المشروع للإنتاج"""
    print("🚀 إعداد المشروع للإنتاج...")
    
    # تنظيف الملفات المؤقتة
    subprocess.run([sys.executable, 'manage.py', 'clean'])
    
    # تشغيل الاختبارات
    print("🧪 تشغيل الاختبارات...")
    subprocess.run([sys.executable, 'tests.py'])
    
    # تحديث الترجمات
    subprocess.run([sys.executable, 'manage.py', 'translate'])
    
    print("✅ تم إعداد المشروع للإنتاج!")

if __name__ == '__main__':
    cli() 