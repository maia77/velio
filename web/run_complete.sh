#!/bin/bash

echo "🚀 بدء تشغيل التطبيق الكامل مع جميع الميزات..."

# إيقاف أي تطبيقات أخرى
pkill -f "python3 app.py" 2>/dev/null
pkill -f "python3 admin_app_fixed.py" 2>/dev/null
sleep 2

# الحصول على عنوان IP
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

echo "📍 عنوان IP الكمبيوتر: $IP_ADDRESS"
echo ""
echo "🔗 الروابط المتاحة:"
echo "   📱 التطبيق الرئيسي (الهاتف): http://$IP_ADDRESS:5003"
echo "   📱 إدارة المنتجات (الهاتف): http://$IP_ADDRESS:5007"
echo "   💻 التطبيق الرئيسي (الكمبيوتر): http://127.0.0.1:5003"
echo "   💻 إدارة المنتجات (الكمبيوتر): http://127.0.0.1:5007"
echo ""

echo "✅ الميزات المتاحة:"
echo "   - عرض المنتجات"
echo "   - إضافة منتجات جديدة"
echo "   - تعديل المنتجات (محدث)"
echo "   - حذف المنتجات"
echo "   - وصول من الهاتف"
echo ""

# تشغيل التطبيق الرئيسي
echo "🚀 تشغيل التطبيق الرئيسي..."
python3 app.py &
APP_PID=$!

# انتظار قليل
sleep 3

# تشغيل تطبيق الإدارة
echo "🚀 تشغيل تطبيق الإدارة..."
python3 admin_app_fixed.py &
ADMIN_PID=$!

echo ""
echo "✅ تم تشغيل التطبيقات بنجاح!"
echo ""
echo "📱 للوصول من الهاتف:"
echo "   - الموقع الرئيسي: http://$IP_ADDRESS:5003"
echo "   - إدارة المنتجات: http://$IP_ADDRESS:5007"
echo ""
echo "💻 للوصول من الكمبيوتر:"
echo "   - الموقع الرئيسي: http://127.0.0.1:5003"
echo "   - إدارة المنتجات: http://127.0.0.1:5007"
echo ""
echo "✏️ ميزة التعديل متاحة الآن!"
echo "   - اضغط على زر 'تعديل' بجانب أي منتج"
echo "   - عدل البيانات المطلوبة"
echo "   - اضغط 'تحديث المنتج'"
echo ""
echo "⏹️  لإيقاف التطبيقات، اضغط Ctrl+C أو استخدم:"
echo "   pkill -f 'python3 app.py' && pkill -f 'python3 admin_app_fixed.py'"

# انتظار إشارة الإيقاف
wait 