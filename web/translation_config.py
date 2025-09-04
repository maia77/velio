"""
إعدادات تحسين أداء الترجمة المتقدمة
"""

# إعدادات الأداء العامة المحسنة
PERFORMANCE_CONFIG = {
    # حجم المجموعة للترجمة - زيادة كبيرة
    'BATCH_SIZE': 50,
    
    # الحد الأقصى للطلبات المتزامنة - زيادة كبيرة
    'MAX_CONCURRENT_REQUESTS': 10,
    
    # تأخير بين الطلبات (بالمللي ثانية) - تقليل كبير
    'REQUEST_DELAY': 25,
    
    # حجم التخزين المؤقت - زيادة كبيرة
    'CACHE_SIZE': 5000,
    
    # مدة صلاحية التخزين المؤقت (بالثواني)
    'CACHE_TTL': 7200,  # ساعتين
    
    # الحد الأقصى لطول النص للترجمة
    'MAX_TEXT_LENGTH': 10000,
    
    # الحد الأدنى لطول النص للترجمة
    'MIN_TEXT_LENGTH': 1,
    
    # اللغات المدعومة
    'SUPPORTED_LANGUAGES': [
        'ar', 'en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'
    ],
    
    # إعدادات AWS محسنة
    'AWS_REGION': 'us-east-1',
    'AWS_TIMEOUT': 15,  # تقليل الوقت
    'AWS_CONNECT_TIMEOUT': 5,
    'AWS_READ_TIMEOUT': 10,
    'AWS_MAX_RETRIES': 2,
    
    # إعدادات الترجمة التلقائية محسنة
    'AUTO_TRANSLATE_DELAY': 100,  # تقليل التأخير
    'DEBOUNCE_DELAY': 100,  # تقليل التأخير
    
    # إعدادات الأداء المتقدمة
    'FAST_MODE': True,
    'PRELOAD_MODE': True,
    'BACKGROUND_TRANSLATION': True,
    'WORKER_POOL_SIZE': 5,
    'REQUEST_TIMEOUT': 15000,  # 15 ثانية
    'RETRY_ATTEMPTS': 2,
}

# إعدادات التخزين المؤقت المحسنة - تم تعطيلها لضمان استخدام Amazon Translate API فقط
CACHE_CONFIG = {
    'ENABLED': False,  # تم تعطيل التخزين المؤقت المحلي
    'BACKEND': 'none',  # لا يوجد تخزين مؤقت
    'PERSISTENCE': False,  # لا حفظ على القرص
    'CLEANUP_INTERVAL': 0,  # لا تنظيف
    'MAX_ENTRIES': 0,
    'COMPRESSION': False,
    'THREAD_SAFE': False,
}

# إعدادات المراقبة المحسنة
MONITORING_CONFIG = {
    'ENABLED': True,
    'LOG_PERFORMANCE': True,
    'LOG_ERRORS': True,
    'METRICS_COLLECTION': True,
    'REAL_TIME_MONITORING': True,
    'PERFORMANCE_ALERTS': True,
}

# إعدادات الترجمة الذكية المحسنة
SMART_TRANSLATION_CONFIG = {
    'ENABLED': True,
    'DETECT_LANGUAGE_ONCE': True,
    'SKIP_SHORT_TEXTS': True,
    'SKIP_NUMBERS': True,
    'SKIP_URLS': True,
    'SKIP_EMAILS': True,
    'FAST_LANGUAGE_DETECTION': True,
    'PRELOAD_COMMON_TRANSLATIONS': True,
    'INTELLIGENT_BATCHING': True,
}

# إعدادات واجهة المستخدم المحسنة
UI_CONFIG = {
    'SHOW_LOADING_INDICATOR': True,
    'SHOW_PROGRESS_BAR': True,
    'ANIMATION_DURATION': 200,  # تقليل مدة الرسوم المتحركة
    'BATCH_UPDATE_DELAY': 50,  # تقليل التأخير
    'INSTANT_TRANSLATION': True,
    'LAZY_LOADING': True,
}

# إعدادات الأمان المحسنة
SECURITY_CONFIG = {
    'RATE_LIMITING': True,
    'MAX_REQUESTS_PER_MINUTE': 200,  # زيادة الحد
    'MAX_REQUESTS_PER_HOUR': 2000,  # زيادة الحد
    'BLOCK_SUSPICIOUS_REQUESTS': True,
    'REQUEST_VALIDATION': True,
}

# إعدادات الترجمة المتقدمة
ADVANCED_TRANSLATION_CONFIG = {
    'CONNECTION_POOLING': True,
    'KEEP_ALIVE': True,
    'HTTP2_SUPPORT': True,
    'COMPRESSION': True,
    'CACHE_WARMING': True,
    'PREDICTIVE_LOADING': True,
    'ADAPTIVE_BATCHING': True,
}

def get_config():
    """الحصول على جميع الإعدادات"""
    return {
        'performance': PERFORMANCE_CONFIG,
        'cache': CACHE_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'smart_translation': SMART_TRANSLATION_CONFIG,
        'ui': UI_CONFIG,
        'security': SECURITY_CONFIG,
        'advanced_translation': ADVANCED_TRANSLATION_CONFIG,
    }

def get_performance_config():
    """الحصول على إعدادات الأداء"""
    return PERFORMANCE_CONFIG

def get_cache_config():
    """الحصول على إعدادات التخزين المؤقت"""
    return CACHE_CONFIG

def get_advanced_config():
    """الحصول على إعدادات الترجمة المتقدمة"""
    return ADVANCED_TRANSLATION_CONFIG

def is_feature_enabled(feature_name):
    """التحقق من تفعيل ميزة معينة"""
    config = get_config()
    
    feature_map = {
        'cache': config['cache']['ENABLED'],
        'monitoring': config['monitoring']['ENABLED'],
        'smart_translation': config['smart_translation']['ENABLED'],
        'rate_limiting': config['security']['RATE_LIMITING'],
        'fast_mode': config['performance']['FAST_MODE'],
        'preload_mode': config['performance']['PRELOAD_MODE'],
        'connection_pooling': config['advanced_translation']['CONNECTION_POOLING'],
    }
    
    return feature_map.get(feature_name, False)

def get_optimized_settings():
    """الحصول على الإعدادات المحسنة للأداء العالي"""
    return {
        'batch_size': 50,
        'concurrent_requests': 10,
        'request_delay': 25,
        'cache_size': 5000,
        'timeout': 15,
        'retry_attempts': 2,
        'debounce_delay': 100,
    } 