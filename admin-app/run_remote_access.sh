#!/bin/bash

echo "🚀 بدء تشغيل الوصول عن بعد للوحة التحكم..."

# التحقق من تشغيل التطبيق
if ! pgrep -f "python3 app.py" > /dev/null; then
    echo "⚠️ التطبيق غير مشغل. بدء تشغيل التطبيق..."
    python3 app.py &
    sleep 5
fi

# تشغيل ngrok
echo "🌐 بدء تشغيل نفق ngrok..."
ngrok http 5003

echo "✅ تم إنشاء الرابط العام!"
echo "📱 شارك الرابط مع صديقتك للوصول للوحة التحكم"
