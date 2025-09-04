#!/bin/bash

# سكريبت لمزامنة الصور بين التطبيقين
echo "🔄 مزامنة الصور بين التطبيقين..."

# إنشاء مجلد uploads في web إذا لم يكن موجوداً
mkdir -p web/static/uploads

# نسخ جميع الصور من admin-app إلى web
echo "📁 نسخ الصور من admin-app إلى web..."
cp admin-app/static/uploads/*.jpg web/static/uploads/ 2>/dev/null || true
cp admin-app/static/uploads/*.png web/static/uploads/ 2>/dev/null || true
cp admin-app/static/uploads/*.gif web/static/uploads/ 2>/dev/null || true
cp admin-app/static/uploads/*.webp web/static/uploads/ 2>/dev/null || true

# نسخ جميع الصور من web إلى admin-app
echo "📁 نسخ الصور من web إلى admin-app..."
cp web/static/uploads/*.jpg admin-app/static/uploads/ 2>/dev/null || true
cp web/static/uploads/*.png admin-app/static/uploads/ 2>/dev/null || true
cp web/static/uploads/*.gif admin-app/static/uploads/ 2>/dev/null || true
cp web/static/uploads/*.webp admin-app/static/uploads/ 2>/dev/null || true

echo "✅ تمت مزامنة الصور بنجاح!"
echo "📊 عدد الصور في web/static/uploads: $(ls web/static/uploads/*.{jpg,png,gif,webp} 2>/dev/null | wc -l)"
echo "📊 عدد الصور في admin-app/static/uploads: $(ls admin-app/static/uploads/*.{jpg,png,gif,webp} 2>/dev/null | wc -l)"
