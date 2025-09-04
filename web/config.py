#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ملف الإعدادات لموقع Velio
"""

import os
from datetime import timedelta

class Config:
    """الإعدادات الأساسية"""
    
    # إعدادات التطبيق
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'
    DEBUG = True
    
    # إعدادات الترجمة
    BABEL_DEFAULT_LOCALE = 'ar'
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    LANGUAGES = ['en', 'ar']
    
    # إعدادات البريد الإلكتروني - يجب إضافة البيانات من متغيرات البيئة
    SMTP_SERVER = os.environ.get('SMTP_SERVER', "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')
    RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', '')
    
    # إعدادات قاعدة البيانات (للتطوير المستقبلي)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///velio.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات الأمان
    SESSION_COOKIE_SECURE = False  # True في الإنتاج
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # إعدادات الملفات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # إعدادات الترجمة التلقائية
    TRANSLATION_CACHE_SIZE = 1000
    AUTO_TRANSLATE_ENABLED = False
    AUTO_TRANSLATE_ON_LOAD = False
    MANUAL_TRANSLATE_ONLY = True
    
    # إعدادات GPS
    GPS_ENABLED = True
    GPS_CACHE_DURATION = 3600  # ثانية واحدة
    
    # إعدادات الإشعارات
    EMAIL_NOTIFICATIONS_ENABLED = True
    SMS_NOTIFICATIONS_ENABLED = False  # للتطوير المستقبلي
    
    # إعدادات الأداء والكاش
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    CACHE_DIR = os.environ.get('CACHE_DIR', './.cache')
    CACHE_THRESHOLD = int(os.environ.get('CACHE_THRESHOLD', '5000'))

class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # في الإنتاج، استخدم متغيرات البيئة
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
    SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
    RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

class TestingConfig(Config):
    """إعدادات الاختبار"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# قاموس الإعدادات
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 