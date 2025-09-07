/**
 * نظام الترجمة التلقائية المحسن باستخدام Amazon Translate مع تحسينات الأداء المتقدمة
 * يدعم الترجمة الديناميكية للمحتوى بسرعة فائقة مع ضمان ترجمة جميع العناصر
 */

class TranslationManager {
    constructor() {
        this.currentLanguage = 'ar';  // اللغة الافتراضية العربية
        this.autoTranslate = false;   // الترجمة التلقائية معطلة افتراضياً
        this.translateServiceAvailable = false;
        this.supportedLanguages = [];
        // إزالة التخزين المؤقت المحلي لضمان استخدام Amazon Translate API فقط
        this.translationCache = new Map(); // فارغ
        this.pendingTranslations = new Map(); // فارغ
        this.batchSize = 100; // زيادة كبيرة في حجم المجموعة
        this.translationQueue = [];
        this.isProcessingQueue = false;
        
        // تحسينات الأداء المتقدمة
        this.workerPool = [];
        this.maxWorkers = 10; // زيادة عدد العمال
        this.requestTimeout = 10000; // تقليل الوقت إلى 10 ثانية
        this.retryAttempts = 1; // تقليل المحاولات
        this.debounceDelay = 50; // تقليل التأخير بشكل كبير
        
        // إعدادات الترجمة السريعة
        this.fastMode = true;
        this.preloadMode = true;
        this.backgroundTranslation = true;
        
        // تحسينات جديدة
        this.maxConcurrentBatches = 5; // عدد المجموعات المتزامنة
        this.batchDelay = 10; // تأخير أقل بين المجموعات
        this.cacheSize = 10000; // زيادة حجم التخزين المؤقت
        
        // تحسينات جديدة لضمان ترجمة جميع العناصر
        this.comprehensiveScan = true; // فحص شامل للصفحة
        this.retryFailedElements = true; // إعادة محاولة العناصر الفاشلة
        this.maxRetries = 3; // عدد المحاولات للعناصر الفاشلة
        this.failedElements = new Set(); // تتبع العناصر الفاشلة
        this.scanInterval = null; // فحص دوري للعناصر الجديدة
        
        // إضافة نظام الترجمة المحلي
        this.localTranslations = new Map(); // ترجمات محلية
        this.useLocalTranslations = true; // استخدام الترجمة المحلية أولاً
        
        this.init();
    }
    
    // وظيفة تحميل الترجمات المحلية
    async loadLocalTranslations() {
        try {
            // ترجمات محلية للكلمات الشائعة - محدثة لضمان الترجمة الصحيحة
            const localTranslations = {
                'ar': {
                    'Home': 'الرئيسية',
                    'Products': 'المنتجات',
                    'About Us': 'من نحن',
                    'Contact Us': 'اتصل بنا',
                    'Search products...': 'ابحث عن المنتجات...',
                    'Cart': 'السلة',
                    'Login': 'تسجيل الدخول',
                    'Everything your home needs': 'كل ما يحتاجه منزلك',
                    'From classic to modern designs': 'من التصاميم الكلاسيكية إلى العصرية',
                    'Shop Now': 'تسوق الآن',
                    'Latest Arrivals': 'وصل حديثاً',
                    'Order Now': 'اطلب الآن',
                    'Why Choose Us?': 'لماذا تختارنا؟',
                    'Fast Shipping': 'شحن سريع',
                    'High Quality': 'جودة عالية',
                    '24/7 Support': 'دعم 24/7',
                    'Modern Design Chair': 'كرسي بتصميم مودرن',
                    'Comfortable and modern chair that adds an aesthetic touch to your home.': 'كرسي مريح وعصري يضيف لمسة جمالية لمنزلك.',
                    'SAR': '$',
                    'Wooden Coffee Table': 'طاولة قهوة خشبية',
                    'Elegant and practical coffee table that suits all decorations.': 'طاولة قهوة أنيقة وعملية تناسب جميع الديكورات.',
                    'We deliver your order as quickly as possible to your doorstep': 'نوصل طلبك في أسرع وقت ممكن إلى باب منزلك',
                    'Carefully selected products from the best international brands': 'منتجات مختارة بعناية من أفضل الماركات العالمية',
                    'Customer service team is available to help you anytime': 'فريق خدمة العملاء متاح لمساعدتك في أي وقت',
                    'Home Decor and Furniture': 'ديكور وأثاث المنزل',
                    'Loading products...': 'جاري تحميل المنتجات...',
                    'Back to Home': 'العودة للرئيسية'
                },
                'en': {
                    'الرئيسية': 'Home',
                    'المنتجات': 'Products',
                    'من نحن': 'About Us',
                    'اتصل بنا': 'Contact Us',
                    'ابحث عن المنتجات...': 'Search products...',
                    'السلة': 'Cart',
                    'تسجيل الدخول': 'Login',
                    'كل ما يحتاجه منزلك': 'Everything your home needs',
                    'من التصاميم الكلاسيكية إلى العصرية': 'From classic to modern designs',
                    'تسوق الآن': 'Shop Now',
                    'وصل حديثاً': 'Latest Arrivals',
                    'اطلب الآن': 'Order Now',
                    'لماذا تختارنا؟': 'Why Choose Us?',
                    'شحن سريع': 'Fast Shipping',
                    'جودة عالية': 'High Quality',
                    'دعم 24/7': '24/7 Support',
                    'كرسي بتصميم مودرن': 'Modern Design Chair',
                    'كرسي مريح وعصري يضيف لمسة جمالية لمنزلك.': 'Comfortable and modern chair that adds an aesthetic touch to your home.',
                    '$': 'USD',
                    'طاولة قهوة خشبية': 'Wooden Coffee Table',
                    'طاولة قهوة أنيقة وعملية تناسب جميع الديكورات.': 'Elegant and practical coffee table that suits all decorations.',
                    'نوصل طلبك في أسرع وقت ممكن إلى باب منزلك': 'We deliver your order as quickly as possible to your doorstep',
                    'منتجات مختارة بعناية من أفضل الماركات العالمية': 'Carefully selected products from the best international brands',
                    'فريق خدمة العملاء متاح لمساعدتك في أي وقت': 'Customer service team is available to help you anytime',
                    'ديكور وأثاث المنزل': 'Home Decor and Furniture',
                    'جاري تحميل المنتجات...': 'Loading products...',
                    'العودة للرئيسية': 'Back to Home'
                }
            };
            
            // تحميل الترجمات المحلية
            this.localTranslations = new Map();
            
            Object.keys(localTranslations).forEach(lang => {
                this.localTranslations.set(lang, new Map(Object.entries(localTranslations[lang])));
            });
            
            console.log('📚 تم تحميل الترجمات المحلية بنجاح');
            console.log(`   العربية: ${this.localTranslations.get('ar')?.size || 0} ترجمة`);
            console.log(`   الإنجليزية: ${this.localTranslations.get('en')?.size || 0} ترجمة`);
            
        } catch (error) {
            console.error('❌ خطأ في تحميل الترجمات المحلية:', error);
        }
    }
    
    async init() {
        try {
            // ضبط اللغة الافتراضية للعربية أولاً
            this.currentLanguage = 'ar';
            
            // تحميل الترجمات المحلية أولاً
            await this.loadLocalTranslations();
            
            // الحصول على معلومات اللغة الحالية
            await this.getCurrentLanguageInfo();
            
            // إجبارياً ضبط اللغة للعربية إذا لم تكن محفوظة
            if (!this.currentLanguage || this.currentLanguage !== 'ar') {
                await this.changeLanguage('ar');
            }
            
            // الحصول على اللغات المدعومة
            await this.getSupportedLanguages();
            
            // إعداد مستمعي الأحداث
            this.setupEventListeners();
            
            // تحميل الترجمات الشائعة مسبقاً
            if (this.preloadMode) {
                this.preloadCommonTranslations();
            }
            
            // تفعيل الترجمة التلقائية إذا كانت مفعلة
            if (this.autoTranslate) {
                this.translatePageContent();
            }
            
            // بدء الفحص الدوري للعناصر الجديدة
            this.startPeriodicScan();
            
            console.log('✅ تم تهيئة نظام الترجمة المحسن بنجاح - اللغة الافتراضية: العربية');
        } catch (error) {
            console.error('❌ خطأ في تهيئة نظام الترجمة:', error);
        }
    }
    
    // وظيفة جديدة: بدء الفحص الدوري
    startPeriodicScan() {
        if (this.scanInterval) {
            clearInterval(this.scanInterval);
        }
        
        this.scanInterval = setInterval(() => {
            if (this.autoTranslate && this.translateServiceAvailable) {
                this.scanForNewElements();
            }
        }, 5000); // فحص كل 5 ثوان
    }
    
    // وظيفة جديدة: فحص العناصر الجديدة
    scanForNewElements() {
        const allElements = document.querySelectorAll('*');
        const newElements = [];
        
        allElements.forEach(element => {
            // التحقق من العناصر التي لم يتم ترجمتها بعد
            if (!element.hasAttribute('data-translated') && 
                this.hasTranslatableContent(element)) {
                newElements.push(element);
            }
        });
        
        if (newElements.length > 0) {
            console.log(`🔍 تم العثور على ${newElements.length} عنصر جديد للترجمة`);
            this.translateElements(newElements);
        }
    }
    
    // وظيفة جديدة: التحقق من وجود محتوى قابل للترجمة
    hasTranslatableContent(element) {
        const text = element.textContent?.trim();
        const placeholder = element.placeholder?.trim();
        
        // التحقق من placeholder لعناصر input
        if (element.tagName === 'INPUT' && placeholder && placeholder.length >= 2) {
            const ignoreClasses = ['no-translate', 'code-block', 'technical', 'translation-ignore'];
            const className = element.className || '';
            
            if (!ignoreClasses.some(cls => className.includes(cls))) {
                return this.shouldTranslateText(placeholder);
            }
        }
        
        if (!text || text.length < 2) return false;
        
        // تجاهل العناصر التي لا نريد ترجمتها
        const tagName = element.tagName.toLowerCase();
        const className = element.className || '';
        
        const ignoreTags = ['script', 'style', 'code', 'pre', 'textarea'];
        const ignoreClasses = ['no-translate', 'code-block', 'technical', 'translation-ignore'];
        
        if (ignoreTags.includes(tagName) || 
            ignoreClasses.some(cls => className.includes(cls))) {
            return false;
        }
        
        // تحسين جديد: التحقق من النص الأصلي قبل الترجمة
        const originalText = element.getAttribute('data-original');
        if (originalText) {
            // إذا كان النص الأصلي إنجليزي، لا نحتاج للترجمة
            if (this.isEnglishText(originalText)) {
                return false;
            }
        }
        
        return this.shouldTranslateText(text);
    }
    
    // وظيفة جديدة: التحقق من أن النص إنجليزي
    isEnglishText(text) {
        if (!text) return false;
        
        // التحقق من وجود أحرف إنجليزية
        const englishPattern = /^[a-zA-Z\s\d\.,!?;:'"()\-_]+$/;
        const arabicPattern = /[\u0600-\u06FF]/;
        
        // إذا كان النص يحتوي على أحرف عربية، فهو ليس إنجليزي
        if (arabicPattern.test(text)) {
            return false;
        }
        
        // إذا كان النص يتطابق مع النمط الإنجليزي، فهو إنجليزي
        return englishPattern.test(text);
    }
    
    // وظيفة جديدة: ترجمة عنصر محدد
    async translateElement(element) {
        if (!element || !this.translateServiceAvailable) return;
        
        const textNodes = this.getTextNodes(element);
        const textsToTranslate = [];
        const textNodeMap = new Map();
        
        textNodes.forEach(node => {
            const text = node.textContent.trim();
            if (text && text.length > 0 && this.shouldTranslateText(text)) {
                textsToTranslate.push(text);
                if (!textNodeMap.has(text)) {
                    textNodeMap.set(text, []);
                }
                textNodeMap.get(text).push(node);
            }
        });
        
        // إضافة ترجمة placeholder لعناصر input
        if (element.tagName === 'INPUT' && element.placeholder) {
            const placeholderText = element.placeholder.trim();
            if (placeholderText && this.shouldTranslateText(placeholderText)) {
                textsToTranslate.push(placeholderText);
                if (!textNodeMap.has(placeholderText)) {
                    textNodeMap.set(placeholderText, []);
                }
                textNodeMap.get(placeholderText).push({ type: 'placeholder', element: element });
            }
        }
        
        if (textsToTranslate.length > 0) {
            try {
                const translatedTexts = await this.translateBatch(textsToTranslate, this.currentLanguage, 'auto');
                
                // تطبيق الترجمات
                textsToTranslate.forEach((originalText, index) => {
                    const translatedText = translatedTexts[index];
                    if (translatedText) {
                        const nodes = textNodeMap.get(originalText) || [];
                        nodes.forEach(node => {
                            if (node.type === 'placeholder') {
                                // ترجمة placeholder
                                node.element.placeholder = translatedText;
                            } else {
                                // ترجمة textContent
                                node.textContent = translatedText;
                            }
                        });
                    }
                });
                
                // علامة أن العنصر تم ترجمته
                element.setAttribute('data-translated', 'true');
                
                console.log(`✅ تم ترجمة عنصر: ${element.tagName}`);
                
            } catch (error) {
                console.error(`❌ خطأ في ترجمة العنصر: ${error}`);
                this.failedElements.add(element);
            }
        }
    }
    
    // وظيفة جديدة: إعادة محاولة العناصر الفاشلة
    async retryFailedElements() {
        if (this.failedElements.size === 0) return;
        
        console.log(`🔄 إعادة محاولة ${this.failedElements.size} عنصر فاشل`);
        
        const failedElementsArray = Array.from(this.failedElements);
        this.failedElements.clear();
        
        for (const element of failedElementsArray) {
            if (element && element.isConnected) {
                await this.translateElement(element);
            }
        }
    }
    
    async getCurrentLanguageInfo() {
        try {
            const response = await fetch('/api/language/current');
            const data = await response.json();
            
            // إجبارياً ضبط اللغة للعربية إذا لم تكن محفوظة أو كانت إنجليزية
            if (!data.language || data.language === 'en') {
                this.currentLanguage = 'ar';
                // إعادة ضبط اللغة في الخادم
                await fetch('/api/language/reset');
                console.log('🔄 تم إعادة ضبط اللغة للعربية');
            } else {
                this.currentLanguage = data.language;
            }
            
            this.autoTranslate = data.auto_translate || false;
            this.translateServiceAvailable = data.translate_service_available;
            
            console.log(`🌍 اللغة الحالية: ${this.currentLanguage}`);
            console.log(`🔄 الترجمة التلقائية: ${this.autoTranslate ? 'مفعلة' : 'معطلة'}`);
            console.log(`🔧 خدمة الترجمة: ${this.translateServiceAvailable ? 'متاحة' : 'غير متاحة'}`);
            
        } catch (error) {
            console.error('❌ خطأ في الحصول على معلومات اللغة:', error);
            // في حالة الخطأ، استخدم العربية كافتراضية
            this.currentLanguage = 'ar';
            this.autoTranslate = false;
        }
    }
    
    async getSupportedLanguages() {
        try {
            const response = await fetch('/api/translate/languages');
            const data = await response.json();
            
            if (data.success) {
                this.supportedLanguages = data.languages;
                console.log(`📚 اللغات المدعومة: ${this.supportedLanguages.length} لغة`);
            }
        } catch (error) {
            console.error('❌ خطأ في الحصول على اللغات المدعومة:', error);
        }
    }
    
    preloadCommonTranslations() {
        // تحميل الترجمات الشائعة في الخلفية
        const commonTexts = [
            'Hello', 'Welcome', 'Thank you', 'Please', 'Yes', 'No',
            'مرحبا', 'أهلا وسهلا', 'شكرا لك', 'من فضلك', 'نعم', 'لا'
        ];
        
        console.log('🔄 تحميل الترجمات الشائعة مسبقاً...');
        
        // تحميل في الخلفية
        setTimeout(() => {
            commonTexts.forEach(text => {
                this.translateText(text, this.currentLanguage, 'auto');
            });
        }, 1000);
    }
    
    setupEventListeners() {
        // مستمع لتغيير اللغة
        document.addEventListener('languageChanged', (event) => {
            this.currentLanguage = event.detail.language;
            this.autoTranslate = event.detail.autoTranslate;
            
            if (this.autoTranslate) {
                this.translatePageContent();
            }
        });
        
        // مستمع لإضافة محتوى جديد مع debouncing محسن
        let debounceTimer;
        const observer = new MutationObserver((mutations) => {
            if (this.autoTranslate) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const newElements = [];
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach((node) => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    newElements.push(node);
                                }
                            });
                        }
                    });
                    
                    if (newElements.length > 0) {
                        this.translateElements(newElements);
                    }
                }, this.debounceDelay);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    async translateText(text, targetLanguage = 'ar', sourceLanguage = 'auto') {
        // تنظيف النص
        const cleanText = text.trim();
        if (!cleanText) return text;
        
        // التحقق من التخزين المؤقت
        const cacheKey = `${cleanText}_${sourceLanguage}_${targetLanguage}`;
        if (this.translationCache.has(cacheKey)) {
            return this.translationCache.get(cacheKey);
        }
        
        // التحقق من الطلبات المعلقة
        if (this.pendingTranslations.has(cacheKey)) {
            return this.pendingTranslations.get(cacheKey);
        }
        
        // استخدام الترجمة المحلية أولاً
        if (this.useLocalTranslations && this.localTranslations.has(targetLanguage)) {
            const localTranslation = this.localTranslations.get(targetLanguage).get(cleanText);
            if (localTranslation) {
                console.log(`📚 ترجمة محلية: "${cleanText}" -> "${localTranslation}"`);
                this.translationCache.set(cacheKey, localTranslation);
                return localTranslation;
            }
        }
        
        // معالجة خاصة لكلمة "الرئيسية"
        if (cleanText === 'الرئيسية' && targetLanguage === 'en') {
            console.log(`🎯 ترجمة خاصة: "الرئيسية" -> "Home"`);
            this.translationCache.set(cacheKey, 'Home');
            return 'Home';
        }
        
        // معالجة خاصة لكلمة "Home"
        if (cleanText === 'Home' && targetLanguage === 'ar') {
            console.log(`🎯 ترجمة خاصة: "Home" -> "الرئيسية"`);
            this.translationCache.set(cacheKey, 'الرئيسية');
            return 'الرئيسية';
        }
        
        // إنشاء وعد جديد للترجمة عبر API
        const translationPromise = this._performTranslationWithRetry(cleanText, targetLanguage, sourceLanguage);
        this.pendingTranslations.set(cacheKey, translationPromise);
        
        try {
            const result = await translationPromise;
            this.pendingTranslations.delete(cacheKey);
            return result;
        } catch (error) {
            this.pendingTranslations.delete(cacheKey);
            throw error;
        }
    }
    
    async _performTranslationWithRetry(text, targetLanguage, sourceLanguage, attempt = 0) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);
            
            const response = await fetch('/api/translate/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    target_language: targetLanguage,
                    source_language: sourceLanguage
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (data.success) {
                // حفظ في التخزين المؤقت
                const cacheKey = `${text}_${sourceLanguage}_${targetLanguage}`;
                this.translationCache.set(cacheKey, data.translated_text);
                return data.translated_text;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            if (attempt < this.retryAttempts && error.name === 'AbortError') {
                console.warn(`⚠️ إعادة المحاولة ${attempt + 1}/${this.retryAttempts} للنص: ${text}`);
                await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
                return this._performTranslationWithRetry(text, targetLanguage, sourceLanguage, attempt + 1);
            }
            
            console.error('❌ فشل في طلب الترجمة:', error);
            return text; // إرجاع النص الأصلي في حالة الفشل
        }
    }
    
    async translateBatch(texts, targetLanguage = 'ar', sourceLanguage = 'auto') {
        // إزالة النصوص الفارغة والتكرار مع تحسين
        const uniqueTexts = [...new Set(texts.filter(text => text && text.trim()))];
        
        if (uniqueTexts.length === 0) {
            return texts.map(() => null);
        }
        
        // التحقق من التخزين المؤقت أولاً
        const cachedResults = [];
        const textsToTranslate = [];
        const textIndexMap = [];
        
        uniqueTexts.forEach((text, index) => {
            const cacheKey = `${text}_${sourceLanguage}_${targetLanguage}`;
            if (this.translationCache.has(cacheKey)) {
                cachedResults[index] = this.translationCache.get(cacheKey);
            } else {
                textsToTranslate.push(text);
                textIndexMap.push(index);
            }
        });
        
        // إذا كانت جميع النصوص مخزنة مؤقتاً
        if (textsToTranslate.length === 0) {
            console.log(`⚡ تم استرجاع ${uniqueTexts.length} ترجمة من التخزين المؤقت`);
            return this.mapResultsToOriginalOrder(texts, uniqueTexts, cachedResults);
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);
            
            const response = await fetch('/api/translate/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    texts: textsToTranslate,
                    target_language: targetLanguage,
                    source_language: sourceLanguage
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (data.success) {
                // حفظ الترجمات الجديدة في التخزين المؤقت
                textsToTranslate.forEach((text, index) => {
                    const translatedText = data.translated_texts[index];
                    if (translatedText) {
                        const cacheKey = `${text}_${sourceLanguage}_${targetLanguage}`;
                        this.translationCache.set(cacheKey, translatedText);
                        cachedResults[textIndexMap[index]] = translatedText;
                    }
                });
                
                console.log(`🚀 تم ترجمة ${textsToTranslate.length} نص جديد`);
                
                // إرجاع النتائج بالترتيب الأصلي
                return texts.map(text => {
                    const cleanText = text ? text.trim() : '';
                    const uniqueIndex = uniqueTexts.indexOf(cleanText);
                    return uniqueIndex >= 0 ? cachedResults[uniqueIndex] : null;
                });
            } else {
                console.error('❌ فشل في الترجمة المجمعة:', data.error);
                return texts.map(() => null);
            }
        } catch (error) {
            console.error('❌ خطأ في طلب الترجمة المجمعة:', error);
            return texts.map(() => null);
        }
    }
    
    async translateElements(elements) {
        // جمع جميع النصوص من العناصر
        const allTexts = [];
        const textElementMap = new Map();
        
        elements.forEach(element => {
            const textNodes = this.getTextNodes(element);
            textNodes.forEach(node => {
                const text = node.textContent.trim();
                if (text && text.length > 0 && this.shouldTranslateText(text)) {
                    allTexts.push(text);
                    if (!textElementMap.has(text)) {
                        textElementMap.set(text, []);
                    }
                    textElementMap.get(text).push(node);
                }
            });
        });
        
        if (allTexts.length > 0) {
            // إضافة إلى قائمة الانتظار
            this.translationQueue.push({
                texts: allTexts,
                textElementMap: textElementMap,
                targetLanguage: this.currentLanguage,
                sourceLanguage: 'auto'
            });
            
            // معالجة قائمة الانتظار
            this.processTranslationQueue();
        }
    }
    
    async processTranslationQueue() {
        if (this.isProcessingQueue || this.translationQueue.length === 0) {
            return;
        }
        
        this.isProcessingQueue = true;
        
        try {
            while (this.translationQueue.length > 0) {
                const batch = this.translationQueue.shift();
                
                // تقسيم النصوص إلى مجموعات أكبر
                const textBatches = [];
                for (let i = 0; i < batch.texts.length; i += this.batchSize) {
                    textBatches.push(batch.texts.slice(i, i + this.batchSize));
                }
                
                // معالجة المجموعات بشكل متوازي
                const batchPromises = textBatches.map(async (textBatch, batchIndex) => {
                    try {
                        const translatedTexts = await this.translateBatch(
                            textBatch, 
                            batch.targetLanguage, 
                            batch.sourceLanguage
                        );
                        
                        // تطبيق الترجمات فوراً
                        textBatch.forEach((originalText, index) => {
                            const translatedText = translatedTexts[index];
                            if (translatedText) {
                                const textNodes = batch.textElementMap.get(originalText) || [];
                                textNodes.forEach(node => {
                                    node.textContent = translatedText;
                                });
                            }
                        });
                        
                        console.log(`✅ تم ترجمة مجموعة ${batchIndex + 1}/${textBatches.length}`);
                        
                        // تأخير أقل بين المجموعات
                        await new Promise(resolve => setTimeout(resolve, this.batchDelay));
                        
                    } catch (error) {
                        console.error(`❌ خطأ في ترجمة المجموعة ${batchIndex + 1}:`, error);
                    }
                });
                
                // انتظار اكتمال جميع المجموعات
                await Promise.all(batchPromises);
            }
        } catch (error) {
            console.error('❌ خطأ في معالجة قائمة انتظار الترجمة:', error);
        } finally {
            this.isProcessingQueue = false;
        }
    }
    
    async translatePageContent() {
        if (!this.translateServiceAvailable) {
            console.warn('⚠️ خدمة الترجمة غير متاحة');
            return;
        }
        
        console.log('🚀 بدء ترجمة محتوى الصفحة الشامل...');
        
        // الطريقة الأولى: ترجمة عناصر القائمة مباشرة (تشمل شريط البحث)
        await this.translateNavigationElements();
        
        // الطريقة الثانية: ترجمة النصوص التقليدية
        await this.translateTextNodes();
        
        // الطريقة الثالثة: فحص شامل لجميع العناصر
        await this.translateAllElements();
        
        // الطريقة الرابعة: إعادة محاولة العناصر الفاشلة
        if (this.retryFailedElements) {
            setTimeout(() => {
                this.retryFailedElements();
            }, 2000);
        }
        
        console.log('✅ تم اكتمال ترجمة محتوى الصفحة الشامل');
    }
    
    // وظيفة جديدة: ترجمة النصوص التقليدية
    async translateTextNodes() {
        const textNodes = this.getTextNodes(document.body);
        const textsToTranslate = [];
        const textNodeMap = new Map();
        
        // جمع النصوص للترجمة مع تحسين
        textNodes.forEach((node) => {
            const text = node.textContent.trim();
            if (text && text.length > 0 && this.shouldTranslateText(text)) {
                textsToTranslate.push(text);
                if (!textNodeMap.has(text)) {
                    textNodeMap.set(text, []);
                }
                textNodeMap.get(text).push(node);
            }
        });
        
        // إضافة ترجمة placeholder لجميع عناصر input
        const inputElements = document.querySelectorAll('input[placeholder]');
        inputElements.forEach(input => {
            const placeholderText = input.placeholder.trim();
            if (placeholderText && this.shouldTranslateText(placeholderText)) {
                textsToTranslate.push(placeholderText);
                if (!textNodeMap.has(placeholderText)) {
                    textNodeMap.set(placeholderText, []);
                }
                textNodeMap.get(placeholderText).push({ type: 'placeholder', element: input });
            }
        });
        
        if (textsToTranslate.length > 0) {
            try {
                // تقسيم النصوص إلى مجموعات أكبر مع معالجة متوازية
                const batches = [];
                for (let i = 0; i < textsToTranslate.length; i += this.batchSize) {
                    batches.push(textsToTranslate.slice(i, i + this.batchSize));
                }
                
                let totalTranslated = 0;
                
                // معالجة المجموعات بشكل متوازي
                const batchPromises = batches.map(async (batch, batchIndex) => {
                    try {
                        const translatedTexts = await this.translateBatch(batch, this.currentLanguage, 'auto');
                        
                        // تطبيق الترجمات فوراً
                        batch.forEach((originalText, index) => {
                            const translatedText = translatedTexts[index];
                            if (translatedText) {
                                const textNodes = textNodeMap.get(originalText) || [];
                                textNodes.forEach(node => {
                                    if (node.type === 'placeholder') {
                                        // ترجمة placeholder
                                        node.element.placeholder = translatedText;
                                    } else {
                                        // ترجمة textContent
                                        node.textContent = translatedText;
                                    }
                                });
                                totalTranslated++;
                            }
                        });
                        
                        console.log(`✅ تم ترجمة مجموعة النصوص ${batchIndex + 1}/${batches.length}`);
                        
                        // تأخير أقل بين المجموعات
                        await new Promise(resolve => setTimeout(resolve, this.batchDelay));
                        
                    } catch (error) {
                        console.error(`❌ خطأ في ترجمة مجموعة النصوص ${batchIndex + 1}:`, error);
                    }
                });
                
                // انتظار اكتمال جميع المجموعات
                await Promise.all(batchPromises);
                
                console.log(`🚀 تم ترجمة ${totalTranslated} نص تقليدي في الصفحة`);
                
            } catch (error) {
                console.error('❌ خطأ في ترجمة النصوص التقليدية:', error);
            }
        }
    }
    
    // وظيفة جديدة: ترجمة جميع العناصر
    async translateAllElements() {
        const allElements = document.querySelectorAll('*');
        const elementsToTranslate = [];
        
        allElements.forEach(element => {
            if (this.hasTranslatableContent(element) && 
                !element.hasAttribute('data-translated')) {
                elementsToTranslate.push(element);
            }
        });
        
        if (elementsToTranslate.length > 0) {
            console.log(`🔍 تم العثور على ${elementsToTranslate.length} عنصر للترجمة الشاملة`);
            
            // تقسيم العناصر إلى مجموعات
            const elementBatches = [];
            for (let i = 0; i < elementsToTranslate.length; i += 20) {
                elementBatches.push(elementsToTranslate.slice(i, i + 20));
            }
            
            let totalTranslated = 0;
            
            // ترجمة كل مجموعة
            for (const batch of elementBatches) {
                const batchPromises = batch.map(async (element) => {
                    try {
                        await this.translateElement(element);
                        totalTranslated++;
                    } catch (error) {
                        console.error(`❌ خطأ في ترجمة العنصر: ${error}`);
                    }
                });
                
                await Promise.all(batchPromises);
                
                // تأخير قصير بين المجموعات
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            console.log(`🚀 تم ترجمة ${totalTranslated} عنصر في الفحص الشامل`);
        }
    }
    
    // وظيفة جديدة: ترجمة عناصر القائمة مباشرة
    async translateNavigationElements() {
        console.log('🎯 بدء ترجمة عناصر القائمة مباشرة...');
        
        // ترجمة عناصر القائمة الرئيسية
        const navElements = [
            { selector: 'a[onclick*="showSection(\'home\')"]', ar: 'الرئيسية', en: 'Home' },
            { selector: 'a[onclick*="showSection(\'products\')"]', ar: 'المنتجات', en: 'Products' },
            { selector: 'a[onclick*="showSection(\'about-page\')"]', ar: 'من نحن', en: 'About Us' },
            { selector: 'a[onclick*="showSection(\'contact\')"]', ar: 'اتصل بنا', en: 'Contact Us' }
        ];
        
        navElements.forEach(element => {
            const navLink = document.querySelector(element.selector);
            if (navLink) {
                if (this.currentLanguage === 'en') {
                    navLink.textContent = element.en;
                    console.log(`✅ تم ترجمة "${element.ar}" إلى "${element.en}"`);
                } else {
                    navLink.textContent = element.ar;
                    console.log(`✅ تم ترجمة "${element.en}" إلى "${element.ar}"`);
                }
            }
        });
        
        // ترجمة عناصر Footer (روابط سريعة)
        const footerElements = [
            { selector: 'footer a[onclick*="showSection(\'home\')"]', ar: 'الرئيسية', en: 'Home' },
            { selector: 'footer a[onclick*="showSection(\'products\')"]', ar: 'المنتجات', en: 'Products' },
            { selector: 'footer a[onclick*="showSection(\'about-page\')"]', ar: 'من نحن', en: 'About Us' },
            { selector: 'footer a[onclick*="openFooterSection(\'contact\'"]', ar: 'اتصل بنا', en: 'Contact Us' }
        ];
        
        footerElements.forEach(element => {
            const footerLink = document.querySelector(element.selector);
            if (footerLink) {
                if (this.currentLanguage === 'en') {
                    // تحديث النص مع الحفاظ على الأيقونة
                    const icon = footerLink.querySelector('i');
                    if (icon) {
                        footerLink.innerHTML = icon.outerHTML + ' ' + element.en;
                    } else {
                        footerLink.textContent = element.en;
                    }
                    console.log(`✅ تم ترجمة Footer "${element.ar}" إلى "${element.en}"`);
                } else {
                    // تحديث النص مع الحفاظ على الأيقونة
                    const icon = footerLink.querySelector('i');
                    if (icon) {
                        footerLink.innerHTML = icon.outerHTML + ' ' + element.ar;
                    } else {
                        footerLink.textContent = element.ar;
                    }
                    console.log(`✅ تم ترجمة Footer "${element.en}" إلى "${element.ar}"`);
                }
            }
        });
        
        // ترجمة عناصر أخرى مهمة
        const otherElements = [
            { selector: '.cart-btn', ar: 'السلة', en: 'Cart' },
            { selector: '.hero-title', ar: 'كل ما يحتاجه منزلك', en: 'Everything your home needs' },
            { selector: '.hero-subtitle', ar: 'من التصاميم الكلاسيكية إلى العصرية', en: 'From classic to modern designs' },
            { selector: '.cta-button', ar: 'تسوق الآن', en: 'Shop Now' },
            { selector: '.section-title', ar: 'وصل حديثاً', en: 'Latest Arrivals' },
            { selector: '.loading-products p', ar: 'جاري تحميل المنتجات...', en: 'Loading products...' }
        ];
        
        otherElements.forEach(element => {
            const el = document.querySelector(element.selector);
            if (el) {
                if (this.currentLanguage === 'en') {
                    el.textContent = element.en;
                    console.log(`✅ تم ترجمة "${element.ar}" إلى "${element.en}"`);
                } else {
                    el.textContent = element.ar;
                    console.log(`✅ تم ترجمة "${element.en}" إلى "${element.ar}"`);
                }
            }
        });
        
        // ترجمة عناصر input مع placeholder
        const inputElements = [
            { selector: '.search-input', ar: 'ابحث عن المنتجات...', en: 'Search products...' },
            { selector: 'input[name="name"]', ar: 'أدخل اسمك الكامل', en: 'Enter your full name' },
            { selector: 'input[name="email"]', ar: 'أدخل بريدك الإلكتروني', en: 'Enter your email' },
            { selector: 'input[name="phone"]', ar: 'أدخل رقم الهاتف', en: 'Enter phone number' },
            { selector: 'input[name="subject"]', ar: 'موضوع الرسالة', en: 'Message subject' },
            { selector: '#orderName', ar: 'أدخل اسمك الثلاثي', en: 'Enter your full name' },
            { selector: '#orderEmail', ar: 'أدخل بريدك الإلكتروني', en: 'Enter your email' },
            { selector: '#orderPhone', ar: 'أدخل رقم الهاتف', en: 'Enter phone number' }
        ];
        
        inputElements.forEach(element => {
            const input = document.querySelector(element.selector);
            if (input) {
                if (this.currentLanguage === 'en') {
                    input.placeholder = element.en;
                    console.log(`✅ تم ترجمة placeholder "${element.ar}" إلى "${element.en}"`);
                } else {
                    input.placeholder = element.ar;
                    console.log(`✅ تم ترجمة placeholder "${element.en}" إلى "${element.ar}"`);
                }
            }
        });
        
        console.log('✅ تم اكتمال ترجمة عناصر القائمة مباشرة');
    }
    
    getTextNodes(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: (node) => {
                    // تجاهل النصوص في العناصر التي لا نريد ترجمتها
                    const parent = node.parentElement;
                    if (parent) {
                        const tagName = parent.tagName.toLowerCase();
                        const className = parent.className || '';
                        const id = parent.id || '';
                        
                        // تجاهل النصوص في هذه العناصر
                        const ignoreTags = ['script', 'style', 'code', 'pre', 'noscript'];
                        const ignoreClasses = ['no-translate', 'code-block', 'technical', 'translation-ignore'];
                        const ignoreIds = ['translation-ignore'];
                        
                        if (ignoreTags.includes(tagName) || 
                            ignoreClasses.some(cls => className.includes(cls)) ||
                            ignoreIds.some(idName => id.includes(idName))) {
                            return NodeFilter.FILTER_REJECT;
                        }
                        
                        // تجاهل النصوص في العناصر المخفية
                        const computedStyle = window.getComputedStyle(parent);
                        if (computedStyle.display === 'none' || 
                            computedStyle.visibility === 'hidden' ||
                            parent.offsetParent === null) {
                            return NodeFilter.FILTER_REJECT;
                        }
                    }
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
        );
        
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        return textNodes;
    }
    
    shouldTranslateText(text) {
        // تجاهل النصوص القصيرة جداً
        if (!text || text.length < 1) return false;
        
        // تجاهل الأرقام فقط
        if (/^\d+$/.test(text)) return false;
        
        // تجاهل علامات الترقيم فقط
        if (/^[^\w\s\u0600-\u06FF]+$/.test(text)) return false;
        
        // تجاهل النصوص التي تبدو كأكواد أو روابط
        if (text.includes('http://') || text.includes('https://') || text.includes('www.')) return false;
        if (text.includes('@') && text.includes('.com')) return false; // عناوين البريد الإلكتروني
        
        // تجاهل النصوص التي تحتوي على أكواد برمجية
        if (text.includes('function(') || text.includes('=>') || text.includes('var ') || text.includes('const ')) return false;
        
        // تجاهل النصوص التي تحتوي على أحرف خاصة فقط
        if (/^[^\u0600-\u06FF\u0041-\u005A\u0061-\u007A\s]+$/.test(text)) return false;
        
        // تحسين جديد: تجاهل النصوص الإنجليزية الموجودة أصلاً
        if (this.isEnglishText(text)) {
            console.log(`🚫 تجاهل النص الإنجليزي: "${text}"`);
            return false;
        }
        
        // معالجة خاصة لعناصر Footer
        if (text.includes('الرئيسية') || text.includes('Home')) {
            console.log(`🎯 معالجة خاصة لعنصر Footer: "${text}"`);
            return true;
        }
        
        // ترجمة النصوص التي تحتوي على أحرف عربية أو إنجليزية
        if (/[\u0600-\u06FF\u0041-\u005A\u0061-\u007A]/.test(text)) return true;
        
        return false;
    }
    
    // وظيفة مساعدة لتنظيف التخزين المؤقت
    cleanCache() {
        if (this.translationCache.size > this.cacheSize) {
            const entries = Array.from(this.translationCache.entries());
            const toDelete = entries.slice(0, entries.length - this.cacheSize);
            toDelete.forEach(([key]) => this.translationCache.delete(key));
            console.log(`🧹 تم تنظيف ${toDelete.length} ترجمة من التخزين المؤقت`);
        }
    }
    
    // وظائف مساعدة للواجهة
    createLanguageSelector() {
        const selector = document.createElement('div');
        selector.className = 'language-selector';
        selector.innerHTML = `
            <select id="language-select" onchange="translationManager.changeLanguage(this.value)">
                <option value="ar" ${this.currentLanguage === 'ar' ? 'selected' : ''}>العربية</option>
                <option value="en" ${this.currentLanguage === 'en' ? 'selected' : ''}>English</option>
                <option value="fr" ${this.currentLanguage === 'fr' ? 'selected' : ''}>Français</option>
                <option value="es" ${this.currentLanguage === 'es' ? 'selected' : ''}>Español</option>
                <option value="de" ${this.currentLanguage === 'de' ? 'selected' : ''}>Deutsch</option>
            </select>
            <label for="auto-translate">
                <input type="checkbox" id="auto-translate" ${this.autoTranslate ? 'checked' : ''} 
                       onchange="translationManager.toggleAutoTranslate(this.checked)">
                الترجمة التلقائية
            </label>
        `;
        
        return selector;
    }
    
    async changeLanguage(languageCode) {
        try {
            const response = await fetch(`/change_language/${languageCode}`);
            
            if (response.ok) {
                this.currentLanguage = languageCode;
                
                // تفعيل الترجمة التلقائية عند تغيير اللغة
                this.autoTranslate = true;
                
                // تنظيف التخزين المؤقت قبل الترجمة الجديدة
                this.cleanCache();
                
                // إرسال حدث تغيير اللغة
                document.dispatchEvent(new CustomEvent('languageChanged', {
                    detail: {
                        language: languageCode,
                        autoTranslate: this.autoTranslate
                    }
                }));
                
                // ترجمة عناصر القائمة مباشرة أولاً
                await this.translateNavigationElements();
                
                // إزالة إشعار التوجيه عند التبديل إلى العربية حسب الطلب
                
                // ترجمة باقي الصفحة
                if (this.translateServiceAvailable) {
                    await this.translatePageContent();
                }
                
                console.log(`🌍 تم تغيير اللغة إلى: ${languageCode} وترجمة الصفحة`);
            }
        } catch (error) {
            console.error('❌ خطأ في تغيير اللغة:', error);
        }
    }
    
    toggleAutoTranslate(enabled) {
        this.autoTranslate = enabled;
        
        if (enabled) {
            // تنظيف علامات الترجمة السابقة
            this.clearTranslationMarks();
            
            // بدء الترجمة الشاملة
            this.translatePageContent();
            
            // إعادة تشغيل الفحص الدوري
            this.startPeriodicScan();
        } else {
            // إيقاف الفحص الدوري
            if (this.scanInterval) {
                clearInterval(this.scanInterval);
                this.scanInterval = null;
            }
        }
        
        console.log(`🔄 الترجمة التلقائية: ${enabled ? 'مفعلة' : 'معطلة'}`);
    }
    
    // وظيفة جديدة: تنظيف علامات الترجمة
    clearTranslationMarks() {
        const translatedElements = document.querySelectorAll('[data-translated]');
        translatedElements.forEach(element => {
            element.removeAttribute('data-translated');
        });
        
        this.failedElements.clear();
        console.log('🧹 تم تنظيف علامات الترجمة السابقة');
    }
    
    // وظيفة جديدة: ترجمة عنصر محدد يدوياً
    async translateSpecificElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            await this.translateElement(element);
            return true;
        }
        return false;
    }
    
    // وظيفة جديدة: ترجمة جميع العناصر من نوع معين
    async translateElementsByTag(tagName) {
        const elements = document.querySelectorAll(tagName);
        const elementsArray = Array.from(elements);
        
        console.log(`🔍 تم العثور على ${elementsArray.length} عنصر من نوع ${tagName}`);
        
        for (const element of elementsArray) {
            if (this.hasTranslatableContent(element)) {
                await this.translateElement(element);
            }
        }
    }
    
    // وظيفة جديدة: ترجمة جميع العناصر من فئة معينة
    async translateElementsByClass(className) {
        const elements = document.querySelectorAll(`.${className}`);
        const elementsArray = Array.from(elements);
        
        console.log(`🔍 تم العثور على ${elementsArray.length} عنصر من فئة ${className}`);
        
        for (const element of elementsArray) {
            if (this.hasTranslatableContent(element)) {
                await this.translateElement(element);
            }
        }
    }
    
    // وظيفة جديدة: الحصول على إحصائيات الترجمة
    getTranslationStats() {
        const totalElements = document.querySelectorAll('*').length;
        const translatedElements = document.querySelectorAll('[data-translated]').length;
        const failedElementsCount = this.failedElements.size;
        
        return {
            totalElements,
            translatedElements,
            failedElements: failedElementsCount,
            translationRate: totalElements > 0 ? (translatedElements / totalElements * 100).toFixed(2) : 0,
            cacheSize: this.translationCache.size,
            pendingTranslations: this.pendingTranslations.size
        };
    }
    
    // وظيفة لترجمة منتج محدد
    async translateProduct(productId, targetLanguage = 'ar') {
        try {
            const response = await fetch(`/api/translate/product/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    target_language: targetLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log(`✅ تم ترجمة المنتج ${productId}`);
                return data.translated_data;
            } else {
                console.error('❌ فشل في ترجمة المنتج:', data.error);
                return null;
            }
        } catch (error) {
            console.error('❌ خطأ في ترجمة المنتج:', error);
            return null;
        }
    }
    
    // وظيفة إظهار إشعارات الترجمة
    showTranslationNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `translation-notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-family: 'Cairo', sans-serif;
            font-size: 14px;
            max-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                <span>${message}</span>
            </div>
        `;
        
        // إضافة CSS للحركة
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // إزالة الإشعار بعد 3 ثوان
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}

// إنشاء نسخة عامة من مدير الترجمة
const translationManager = new TranslationManager();

// تصدير للاستخدام في ملفات أخرى
window.translationManager = translationManager; 