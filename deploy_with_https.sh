#!/bin/bash

# نشر التطبيق مع دعم HTTPS
echo "🚀 نشر تطبيق Velio مع دعم HTTPS..."

# التحقق من وجود Git
if ! command -v git &> /dev/null; then
    echo "❌ Git غير مثبت"
    exit 1
fi

# التحقق من وجود Render CLI
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI غير مثبت"
    echo "💡 لتثبيته: npm install -g @render/cli"
    exit 1
fi

echo "✅ Git و Render CLI متوفران"

# إضافة التغييرات إلى Git
echo "📝 إضافة التغييرات إلى Git..."
git add .

# إنشاء commit
echo "💾 إنشاء commit..."
git commit -m "إضافة دعم HTTPS وتحسين خدمة تحديد الموقع للهواتف"

# دفع التغييرات
echo "⬆️ دفع التغييرات إلى GitHub..."
git push origin main

# نشر على Render
echo "🌐 نشر على Render..."
render deploy

echo "✅ تم النشر بنجاح!"
echo ""
echo "🔗 روابط التطبيق:"
echo "📱 التطبيق الرئيسي: https://web-app.onrender.com"
echo "⚙️ لوحة الإدارة: https://admin-app.onrender.com"
echo ""
echo "📱 خدمة تحديد الموقع ستعمل بشكل أفضل على الهواتف مع HTTPS!"
