#!/bin/bash

echo "🔧 إصلاح مشاكل ngrok تلقائياً..."
echo "=================================================="

# إيقاف جميع عمليات ngrok
echo "1. إيقاف عمليات ngrok..."
pkill ngrok 2>/dev/null
sleep 2

# فحص تثبيت ngrok
echo ""
echo "2. فحص تثبيت ngrok..."
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok غير مثبت"
    echo "📥 جاري التثبيت..."
    brew install ngrok/ngrok/ngrok
    if [ $? -eq 0 ]; then
        echo "✅ تم تثبيت ngrok بنجاح"
    else
        echo "❌ فشل في تثبيت ngrok"
        echo "💡 جرب التثبيت اليدوي:"
        echo "   curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null"
        exit 1
    fi
else
    echo "✅ ngrok مثبت"
fi

# فحص authtoken
echo ""
echo "3. فحص authtoken..."
if ! ngrok config check &> /dev/null; then
    echo "❌ مشكلة في authtoken"
    echo ""
    echo "🔧 لحل هذه المشكلة:"
    echo "1. اذهب إلى: https://dashboard.ngrok.com/signup"
    echo "2. أنشئ حساب مجاني"
    echo "3. اذهب إلى: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "4. انسخ الـ authtoken"
    echo "5. شغل الأمر التالي:"
    echo "   ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    echo "⏳ انتظار إدخال authtoken..."
    read -p "أدخل authtoken الخاص بك: " authtoken
    if [ ! -z "$authtoken" ]; then
        ngrok config add-authtoken "$authtoken"
        if [ $? -eq 0 ]; then
            echo "✅ تم إعداد authtoken بنجاح"
        else
            echo "❌ فشل في إعداد authtoken"
            exit 1
        fi
    else
        echo "❌ لم يتم إدخال authtoken"
        exit 1
    fi
else
    echo "✅ authtoken صحيح"
fi

# فحص التطبيق
echo ""
echo "4. فحص التطبيق..."
if ! curl -s http://localhost:5003 > /dev/null 2>&1; then
    echo "❌ التطبيق لا يعمل"
    echo "🚀 جاري تشغيل التطبيق..."
    
    # إيقاف أي عمليات python سابقة
    pkill -f "python3 app.py" 2>/dev/null
    sleep 2
    
    # تشغيل التطبيق في الخلفية
    python3 app.py &
    sleep 5
    
    # التحقق من تشغيل التطبيق
    if curl -s http://localhost:5003 > /dev/null 2>&1; then
        echo "✅ التطبيق يعمل الآن"
    else
        echo "❌ فشل في تشغيل التطبيق"
        echo "💡 تأكد من وجود ملف app.py"
        exit 1
    fi
else
    echo "✅ التطبيق يعمل"
fi

# فحص المنفذ
echo ""
echo "5. فحص المنفذ..."
if lsof -i :5003 > /dev/null 2>&1; then
    echo "✅ المنفذ 5003 مفتوح"
else
    echo "❌ المنفذ 5003 مغلق"
    echo "💡 جاري فتح المنفذ..."
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3 2>/dev/null
    echo "✅ تم إعداد جدار الحماية"
fi

# تشغيل ngrok
echo ""
echo "6. تشغيل ngrok..."
echo "🌐 جاري إنشاء النفق..."

# تشغيل ngrok في الخلفية
ngrok http 5003 > ngrok.log 2>&1 &
ngrok_pid=$!

# انتظار قليلاً
sleep 5

# التحقق من تشغيل ngrok
if ps -p $ngrok_pid > /dev/null; then
    echo "✅ ngrok يعمل"
    
    # محاولة الحصول على الرابط
    echo ""
    echo "🔍 جاري البحث عن الرابط..."
    for i in {1..10}; do
        if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
            response=$(curl -s http://localhost:4040/api/tunnels)
            if echo "$response" | grep -q "public_url"; then
                url=$(echo "$response" | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4)
                if [ ! -z "$url" ]; then
                    echo ""
                    echo "🎉 تم إنشاء الرابط بنجاح!"
                    echo "=================================================="
                    echo "🌐 الرابط العام: $url"
                    echo "🔧 لوحة التحكم: $url/admin"
                    echo "📱 المنتجات: $url/view-products"
                    echo "=================================================="
                    echo "📱 شارك هذا الرابط مع أصدقائك!"
                    
                    # حفظ الرابط في ملف
                    echo "رابط ngrok للوصول عن بعد:" > ngrok_url.txt
                    echo "🌐 الرابط العام: $url" >> ngrok_url.txt
                    echo "🔧 لوحة التحكم: $url/admin" >> ngrok_url.txt
                    echo "📱 المنتجات: $url/view-products" >> ngrok_url.txt
                    echo "⏰ تم إنشاؤه في: $(date)" >> ngrok_url.txt
                    
                    echo ""
                    echo "💾 تم حفظ الرابط في ملف: ngrok_url.txt"
                    echo ""
                    echo "⏹️ لإيقاف ngrok، اضغط Ctrl+C"
                    
                    # انتظار إيقاف ngrok
                    wait $ngrok_pid
                    break
                fi
            fi
        fi
        echo "⏳ محاولة $i/10..."
        sleep 2
    done
    
    if [ $i -eq 10 ]; then
        echo "❌ فشل في الحصول على الرابط"
        kill $ngrok_pid 2>/dev/null
    fi
else
    echo "❌ فشل في تشغيل ngrok"
    echo "📋 تحقق من السجل: cat ngrok.log"
fi

echo ""
echo "=================================================="
echo "🔧 انتهى الإصلاح" 