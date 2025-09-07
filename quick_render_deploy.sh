#!/bin/bash

# سكريبت نشر سريع على Render
echo "⚡ نشر سريع على Render..."
echo "========================"

# التحقق من وجود Git
if [ ! -d ".git" ]; then
    echo "❌ هذا المجلد ليس Git repository"
    exit 1
fi

# تحسين البناء
echo "🔧 تحسين البناء..."

# إنشاء .dockerignore للتحسين
cat > .dockerignore << 'EOF'
*.log
*.pyc
__pycache__/
.git/
*.md
admin-app/
.DS_Store
*.tmp
EOF

# تحسين requirements.txt (إزالة التعليقات والمسافات)
echo "📦 تحسين requirements.txt..."
grep -v '^#' requirements.txt | grep -v '^$' > requirements_clean.txt
mv requirements_clean.txt requirements.txt

# إضافة جميع التغييرات
echo "📁 إضافة التغييرات إلى Git..."
git add .

# عمل commit
echo "💾 عمل commit..."
git commit -m "⚡ نشر سريع - تحسينات الأداء" || {
    echo "⚠️  لا توجد تغييرات جديدة"
    exit 0
}

# رفع إلى Render
echo "🚀 رفع إلى Render..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 تم الرفع بنجاح!"
    echo "⏳ Render سيبدأ البناء الآن..."
    echo ""
    echo "📊 تتبع التقدم:"
    echo "1. اذهب إلى dashboard Render"
    echo "2. تحقق من حالة البناء"
    echo "3. انتظر حتى يكتمل البناء"
    echo ""
    echo "⚡ نصائح للسرعة:"
    echo "- استخدم Render CLI: npm install -g @render/cli"
    echo "- ترقية إلى خطة مدفوعة ($7/شهر)"
    echo "- استخدم Vercel للسرعة القصوى"
else
    echo "❌ فشل في الرفع"
    exit 1
fi
