#!/bin/bash

# سكريبت سريع لرفع الصور إلى Render
echo "🚀 رفع الصور إلى Render..."
echo "=========================="

# التحقق من وجود Git
if [ ! -d ".git" ]; then
    echo "❌ هذا المجلد ليس Git repository"
    exit 1
fi

# إحصائيات الصور
web_count=$(find web/static/uploads -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" 2>/dev/null | wc -l)
admin_count=$(find admin-app/static/uploads -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.webp" 2>/dev/null | wc -l)

echo "📊 عدد الصور في web: $web_count"
echo "📊 عدد الصور في admin-app: $admin_count"
echo ""

if [ $web_count -eq 0 ] && [ $admin_count -eq 0 ]; then
    echo "⚠️  لا توجد صور للمزامنة"
    exit 0
fi

# إضافة الصور إلى Git
echo "📁 إضافة الصور إلى Git..."
git add web/static/uploads/ 2>/dev/null || true
git add admin-app/static/uploads/ 2>/dev/null || true

# عمل commit
echo "💾 عمل commit للصور..."
git commit -m "🖼️ إضافة الصور المحدثة للـ deployment" || {
    echo "⚠️  لا توجد تغييرات جديدة للصور"
    exit 0
}

# رفع إلى Render
echo "🚀 رفع الصور إلى Render..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 تم رفع الصور بنجاح إلى Render!"
    echo "⏳ انتظر بضع دقائق حتى يتم تحديث الموقع"
    echo "🌐 تحقق من موقعك على Render"
else
    echo "❌ فشل في رفع الصور إلى Render"
    exit 1
fi
