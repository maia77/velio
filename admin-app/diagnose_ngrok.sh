#!/bin/bash

echo "🔍 تشخيص مشاكل ngrok..."
echo "=================================================="

# فحص ngrok
echo "1. فحص ngrok..."
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok مثبت"
    echo "📋 الإصدار: $(ngrok version)"
else
    echo "❌ ngrok غير مثبت"
    echo "💡 الحل: brew install ngrok/ngrok/ngrok"
    echo ""
fi

# فحص authtoken
echo ""
echo "2. فحص authtoken..."
if ngrok config check &> /dev/null; then
    echo "✅ authtoken صحيح"
else
    echo "❌ مشكلة في authtoken"
    echo "💡 الحل:"
    echo "   1. اذهب إلى: https://dashboard.ngrok.com/signup"
    echo "   2. أنشئ حساب مجاني"
    echo "   3. اذهب إلى: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "   4. شغل: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
fi

# فحص التطبيق
echo ""
echo "3. فحص التطبيق..."
if curl -s http://localhost:5003 > /dev/null 2>&1; then
    echo "✅ التطبيق يعمل على المنفذ 5003"
else
    echo "❌ التطبيق لا يعمل على المنفذ 5003"
    echo "💡 الحل: python3 app.py"
    echo ""
fi

# فحص المنفذ
echo ""
echo "4. فحص المنفذ 5003..."
if lsof -i :5003 > /dev/null 2>&1; then
    echo "✅ المنفذ 5003 مفتوح"
    echo "📋 العمليات:"
    lsof -i :5003
else
    echo "❌ المنفذ 5003 مغلق"
    echo ""
fi

# فحص الشبكة
echo ""
echo "5. فحص الشبكة..."
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✅ الاتصال بالإنترنت يعمل"
else
    echo "❌ مشكلة في الاتصال بالإنترنت"
    echo ""
fi

# فحص DNS
echo ""
echo "6. فحص DNS..."
if nslookup ngrok.com > /dev/null 2>&1; then
    echo "✅ DNS يعمل"
else
    echo "❌ مشكلة في DNS"
    echo ""
fi

# فحص جدار الحماية
echo ""
echo "7. فحص جدار الحماية..."
if sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep -i python > /dev/null 2>&1; then
    echo "✅ Python مُعد في جدار الحماية"
else
    echo "⚠️ Python قد يحتاج إعداد في جدار الحماية"
    echo "💡 الحل: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3"
    echo ""
fi

echo ""
echo "=================================================="
echo "🔧 انتهى التشخيص"
echo ""

# اقتراحات الحل
echo "🎯 الاقتراحات:"
echo ""

if ! command -v ngrok &> /dev/null; then
    echo "1. تثبيت ngrok:"
    echo "   brew install ngrok/ngrok/ngrok"
    echo ""
fi

if ! ngrok config check &> /dev/null; then
    echo "2. إعداد authtoken:"
    echo "   ngrok config add-authtoken YOUR_TOKEN"
    echo ""
fi

if ! curl -s http://localhost:5003 > /dev/null 2>&1; then
    echo "3. تشغيل التطبيق:"
    echo "   python3 app.py"
    echo ""
fi

echo "4. تشغيل ngrok:"
echo "   ngrok http 5003"
echo ""

echo "5. أو استخدم السكريبت المساعد:"
echo "   python3 create_ngrok_link.py"
echo ""

echo "📞 إذا استمرت المشكلة، أخبرني بالخطأ المحدد!" 