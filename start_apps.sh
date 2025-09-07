#!/bin/bash

# ملف تشغيل التطبيقين مع قاعدة البيانات المشتركة

echo "🚀 بدء تشغيل التطبيقين مع قاعدة البيانات المشتركة"
echo "============================================================"

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python3 أولاً"
    exit 1
fi

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت. يرجى تثبيت pip3 أولاً"
    exit 1
fi

echo "✅ تم التحقق من Python3 و pip3"

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt

# اختبار الاتصال بقاعدة البيانات
echo "🔍 اختبار الاتصال بقاعدة البيانات..."
python3 shared_database_config_fallback.py

# التحقق من نجاح الاتصال
if [ $? -ne 0 ]; then
    echo "❌ فشل الاتصال بقاعدة البيانات. يرجى التحقق من الاتصال بالإنترنت"
    exit 1
fi

echo ""
echo "📋 معلومات التشغيل:"
echo "   🌐 تطبيق الويب: http://127.0.0.1:5003"
echo "   🔧 تطبيق الإدارة: http://127.0.0.1:5007"
echo "   💾 قاعدة البيانات: مشتركة بين التطبيقين"
echo ""

# تشغيل التطبيقين
echo "🚀 بدء تشغيل التطبيقين..."
python3 run_apps.py