#!/bin/bash

# سكريبت تشغيل التطبيقات مع المزامنة التلقائية
echo "🚀 بدء تشغيل التطبيقات مع المزامنة التلقائية للصور"
echo "=================================================="

# إيقاف أي عمليات سابقة
echo "⏹️  إيقاف العمليات السابقة..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "watch_images.py" 2>/dev/null || true
lsof -ti:5003 | xargs kill -9 2>/dev/null || true
lsof -ti:5007 | xargs kill -9 2>/dev/null || true

# مزامنة الصور قبل البدء
echo "🔄 مزامنة الصور قبل البدء..."
python3 auto_sync_images.py

# بدء مراقب الصور في الخلفية
echo "👁️  بدء مراقب الصور التلقائي..."
python3 watch_images.py &
WATCH_PID=$!

# انتظار قليل
sleep 2

# بدء التطبيق الرئيسي (web)
echo "🌐 بدء التطبيق الرئيسي على المنفذ 5003..."
cd web
python3 app.py &
WEB_PID=$!

# العودة للمجلد الرئيسي
cd ..

# انتظار قليل
sleep 3

# بدء تطبيق الإدارة
echo "⚙️  بدء تطبيق الإدارة على المنفذ 5007..."
cd admin-app
python3 admin_app_fixed.py &
ADMIN_PID=$!

# العودة للمجلد الرئيسي
cd ..

# انتظار قليل للتأكد من بدء التطبيقات
sleep 5

echo ""
echo "✅ تم تشغيل جميع التطبيقات بنجاح!"
echo "=================================="
echo "🌐 التطبيق الرئيسي: http://127.0.0.1:5003"
echo "⚙️  تطبيق الإدارة: http://127.0.0.1:5007"
echo "👁️  مراقب الصور: يعمل في الخلفية"
echo ""
echo "📱 للوصول من الهاتف:"
echo "🌐 التطبيق الرئيسي: http://192.168.0.72:5003"
echo "⚙️  تطبيق الإدارة: http://192.168.0.72:5007"
echo ""
echo "⏹️  للإيقاف: اضغط Ctrl+C"

# دالة التنظيف عند الإيقاف
cleanup() {
    echo ""
    echo "⏹️  إيقاف جميع التطبيقات..."
    kill $WEB_PID 2>/dev/null || true
    kill $ADMIN_PID 2>/dev/null || true
    kill $WATCH_PID 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "watch_images.py" 2>/dev/null || true
    echo "✅ تم إيقاف جميع التطبيقات"
    exit 0
}

# ربط دالة التنظيف بإشارة الإيقاف
trap cleanup SIGINT SIGTERM

# انتظار إلى ما لا نهاية
while true; do
    sleep 1
done
