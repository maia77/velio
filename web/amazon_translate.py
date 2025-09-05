import boto3
import json
import os
import time
from typing import Dict, List, Optional
from flask import current_app
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AmazonTranslateService:
    """خدمة الترجمة باستخدام Amazon Translate مع تحسينات الأداء المتقدمة"""
    
    def __init__(self):
        # إعدادات AWS - يجب إضافة المفاتيح من متغيرات البيئة
        self.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', '')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
        self.region_name = os.environ.get('AWS_REGION', 'us-east-1')
        
        # تهيئة عميل Amazon Translate
        try:
            self.translate_client = boto3.client(
                'translate',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name,
                config=boto3.session.Config(
                    connect_timeout=10,
                    read_timeout=30,
                    retries={'max_attempts': 2}
                )
            )
            print("✅ تم تهيئة Amazon Translate بنجاح")
        except Exception as e:
            print(f"❌ خطأ في تهيئة Amazon Translate: {e}")
            self.translate_client = None
        
        # إعدادات الأداء المتقدمة
        self.max_batch_size = 50  # زيادة حجم المجموعة
        self.max_concurrent_requests = 10  # زيادة الطلبات المتزامنة
        # تخزين مؤقت بسيط داخل الذاكرة لنتائج الترجمة
        self.translation_cache = {}
        self.cache_lock = threading.Lock()
        self.language_detection_cache = {}
        
        # إعدادات الترجمة السريعة
        self.fast_translate_enabled = True
        self.preload_common_translations = True
        self.connection_pool_size = 5
        
        # تهيئة الترجمات الشائعة مسبقاً - معطل مؤقتاً
        # if self.preload_common_translations:
        #     self._preload_common_translations()
    
    def _preload_common_translations(self):
        """تحميل الترجمات الشائعة مسبقاً"""
        common_texts = [
            "Hello", "Welcome", "Thank you", "Please", "Yes", "No",
            "مرحبا", "أهلا وسهلا", "شكرا لك", "من فضلك", "نعم", "لا"
        ]
        
        print("🔄 تحميل الترجمات الشائعة مسبقاً...")
        
        for text in common_texts:
            # ترجمة من الإنجليزية إلى العربية
            self.translate_text(text, 'ar', 'en')
            # ترجمة من العربية إلى الإنجليزية
            self.translate_text(text, 'en', 'ar')
        
        print(f"✅ تم تحميل {len(common_texts) * 2} ترجمة شائعة")
    
    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> Optional[str]:
        """ترجمة نص واحد مع تحسينات متقدمة"""
        if not self.translate_client or not text:
            return None
        
        # محاولة القراءة من الكاش أولاً
        cache_key = f"{text}|||{source_language}|||{target_language}"
        with self.cache_lock:
            cached = self.translation_cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            # تحويل رموز اللغات
            target_lang_code = self._convert_language_code(target_language)
            source_lang_code = self._convert_language_code(source_language) if source_language != 'auto' else 'auto'
            
            # اكتشاف اللغة المحسن
            if source_lang_code == 'auto':
                detected_lang = self._fast_detect_language(text)
                source_lang_code = detected_lang if detected_lang else 'en'
            
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_lang_code,
                TargetLanguageCode=target_lang_code
            )
            
            translated_text = response['TranslatedText']
            
            # حفظ النتيجة في الكاش
            with self.cache_lock:
                self.translation_cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            print(f"❌ خطأ في ترجمة النص: {e}")
            return None
    
    def translate_text_preserve_format(self, text: str, target_language: str, source_language: str = 'auto') -> Optional[str]:
        """ترجمة نص مع الحفاظ على تنسيق الحروف الكابتل"""
        if not self.translate_client or not text:
            return None
        
        # حفظ التنسيق الأصلي
        original_text = text.strip()
        text_lower = original_text.lower()
        
        # محاولة القراءة من الكاش مع الحفاظ على المفاتيح بالحروف الصغيرة
        cache_key = f"{text_lower}|||{source_language}|||{target_language}"
        with self.cache_lock:
            cached_translation = self.translation_cache.get(cache_key)
            if cached_translation is not None:
                return self._apply_original_format(cached_translation, original_text)
        
        try:
            # تحويل رموز اللغات
            target_lang_code = self._convert_language_code(target_language)
            source_lang_code = self._convert_language_code(source_language) if source_language != 'auto' else 'auto'
            
            # اكتشاف اللغة المحسن
            if source_lang_code == 'auto':
                detected_lang = self._fast_detect_language(text_lower)
                source_lang_code = detected_lang if detected_lang else 'en'
            
            response = self.translate_client.translate_text(
                Text=text_lower,  # إرسال النص بالأحرف الصغيرة للحصول على ترجمة أفضل
                SourceLanguageCode=source_lang_code,
                TargetLanguageCode=target_lang_code
            )
            
            translated_text = response['TranslatedText']
            
            # تطبيق التنسيق الأصلي
            formatted_translation = self._apply_original_format(translated_text, original_text)
            
            # حفظ الترجمة الأساسية في الكاش بالحروف الصغيرة
            with self.cache_lock:
                self.translation_cache[cache_key] = translated_text
            
            return formatted_translation
            
        except Exception as e:
            print(f"❌ خطأ في ترجمة النص: {e}")
            return None
    
    def _apply_original_format(self, translated_text: str, original_text: str) -> str:
        """تطبيق تنسيق النص الأصلي على الترجمة"""
        if not translated_text or not original_text:
            return translated_text
        
        # تقسيم النصوص إلى كلمات
        original_words = original_text.split()
        translated_words = translated_text.split()
        
        # تطبيق التنسيق على كل كلمة مترجمة
        formatted_words = []
        for i, (orig_word, trans_word) in enumerate(zip(original_words, translated_words)):
            if orig_word.isupper():
                formatted_words.append(trans_word.upper())
            elif orig_word.istitle():
                # تطبيق الحرف الأول كابتل على النص العربي
                formatted_words.append(self._capitalize_arabic_word(trans_word))
            else:
                formatted_words.append(trans_word)
        
        # إضافة الكلمات المترجمة الإضافية إذا كانت الترجمة أطول
        if len(translated_words) > len(original_words):
            formatted_words.extend(translated_words[len(original_words):])
        
        return ' '.join(formatted_words)
    
    def _capitalize_arabic_word(self, word: str) -> str:
        """تحويل الحرف الأول إلى كابتل في الكلمة العربية"""
        if not word or len(word) == 0:
            return word
        
        # الحصول على الحرف الأول
        first_char = word[0]
        # الحصول على باقي الكلمة
        rest_of_word = word[1:] if len(word) > 1 else ""
        
        # تحويل الحرف الأول إلى كابتل
        if first_char.isalpha():
            capitalized_first = first_char.upper()
            return capitalized_first + rest_of_word
        else:
            return word
    
    def _fast_detect_language(self, text: str) -> Optional[str]:
        """اكتشاف سريع للغة"""
        # إزالة التحقق من التخزين المؤقت المحلي لضمان استخدام Amazon Translate API فقط
        # if text in self.language_detection_cache:
        #     return self.language_detection_cache[text]
        
        # اكتشاف سريع بناءً على الأحرف
        if any('\u0600' <= char <= '\u06FF' for char in text):
            detected_lang = 'ar'
        elif any('\u0041' <= char <= '\u005A' or '\u0061' <= char <= '\u007A' for char in text):
            detected_lang = 'en'
        else:
            detected_lang = 'en'  # افتراضي
        
        # إزالة حفظ التخزين المؤقت المحلي
        # self.language_detection_cache[text] = detected_lang
        
        return detected_lang
    
    def translate_batch(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[Optional[str]]:
        """ترجمة مجمعة محسنة جداً"""
        if not self.translate_client or not texts:
            return [None] * len(texts)
        
        # إزالة النصوص الفارغة والتكرار
        unique_texts = list(set([text.strip() for text in texts if text.strip()]))
        
        if not unique_texts:
            return [None] * len(texts)
        
        # استخدام الكاش لنتائج سابقة وتقليل عدد الاتصالات
        cached_results = {}
        texts_to_translate = []
        with self.cache_lock:
            for text in unique_texts:
                cache_key = f"{text}|||{source_language}|||{target_language}"
                if cache_key in self.translation_cache:
                    cached_results[text] = self.translation_cache[cache_key]
                else:
                    texts_to_translate.append(text)
        
        # with self.cache_lock:
        #     for text in unique_texts:
        #         cache_key = f"{text}_{source_language}_{target_language}"
        #         if cache_key in self.translation_cache:
        #             cached_results[text] = self.translation_cache[cache_key]
        #         else:
        #             texts_to_translate.append(text)
        
        # ترجمة النصوص الجديدة فقط
        if texts_to_translate:
            translated_results = self._ultra_fast_batch_translate(texts_to_translate, target_language, source_language)
            
            # دمج النتائج مع التخزين المؤقت
            for i, text in enumerate(texts_to_translate):
                if i < len(translated_results) and translated_results[i]:
                    cached_results[text] = translated_results[i]
                    with self.cache_lock:
                        self.translation_cache[f"{text}|||{source_language}|||{target_language}"] = translated_results[i]
        
        # إرجاع النتائج بالترتيب الأصلي
        results = []
        for text in texts:
            text_clean = text.strip()
            if text_clean in cached_results:
                results.append(cached_results[text_clean])
            else:
                results.append(None)
        
        return results
    
    def _ultra_fast_batch_translate(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[Optional[str]]:
        """ترجمة مجمعة فائقة السرعة"""
        if not texts:
            return []
        
        # تقسيم النصوص إلى مجموعات أكبر
        batches = [texts[i:i + self.max_batch_size] for i in range(0, len(texts), self.max_batch_size)]
        
        results = []
        
        # استخدام ThreadPoolExecutor مع عدد أكبر من العمال
        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            # إنشاء مهام الترجمة
            future_to_batch = {}
            for batch in batches:
                future = executor.submit(self._translate_single_batch_optimized, batch, target_language, source_language)
                future_to_batch[future] = batch
            
            # جمع النتائج
            for future in as_completed(future_to_batch):
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    print(f"❌ خطأ في ترجمة المجموعة: {e}")
                    batch = future_to_batch[future]
                    results.extend([None] * len(batch))
        
        return results
    
    def _translate_single_batch_optimized(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[Optional[str]]:
        """ترجمة مجموعة واحدة محسنة"""
        if not texts:
            return []
        
        try:
            # اكتشاف اللغة مرة واحدة للمجموعة
            source_lang_code = self._convert_language_code(source_language)
            if source_lang_code == 'auto':
                detected_lang = self._fast_detect_language(texts[0])
                source_lang_code = detected_lang if detected_lang else 'en'
            
            target_lang_code = self._convert_language_code(target_language)
            
            # ترجمة كل نص في المجموعة
            results = []
            for text in texts:
                try:
                    response = self.translate_client.translate_text(
                        Text=text,
                        SourceLanguageCode=source_lang_code,
                        TargetLanguageCode=target_lang_code
                    )
                    
                    translated_text = response['TranslatedText']
                    
                    # حفظ في التخزين المؤقت
                    cache_key = f"{text}_{source_language}_{target_language}"
                    with self.cache_lock:
                        self.translation_cache[cache_key] = translated_text
                    
                    results.append(translated_text)
                    
                except Exception as e:
                    print(f"❌ خطأ في ترجمة النص '{text[:30]}...': {e}")
                    results.append(None)
            
            print(f"✅ تم ترجمة مجموعة من {len(texts)} نص")
            return results
            
        except Exception as e:
            print(f"❌ خطأ في ترجمة المجموعة: {e}")
            return [None] * len(texts)
    
    def clear_cache(self):
        """مسح التخزين المؤقت"""
        with self.cache_lock:
            self.translation_cache.clear()
            self.language_detection_cache.clear()
        print("✅ تم مسح التخزين المؤقت")
    
    def get_cache_stats(self):
        """الحصول على إحصائيات التخزين المؤقت"""
        with self.cache_lock:
            return {
                'translation_cache_size': len(self.translation_cache),
                'language_detection_cache_size': len(self.language_detection_cache),
                'total_cache_size': len(self.translation_cache) + len(self.language_detection_cache)
            }
    
    def translate_product(self, product_data: Dict, target_language: str) -> Dict:
        """
        ترجمة بيانات منتج كاملة
        
        Args:
            product_data: بيانات المنتج
            target_language: اللغة المستهدفة
        
        Returns:
            بيانات المنتج المترجمة
        """
        if not self.translate_client:
            return product_data
        
        translated_data = product_data.copy()
        
        # ترجمة الحقول النصية
        fields_to_translate = ['name', 'description', 'category', 'brand']
        
        for field in fields_to_translate:
            if field in product_data and product_data[field]:
                translated_text = self.translate_text(
                    product_data[field], 
                    target_language, 
                    'en'  # نفترض أن النص الأصلي باللغة الإنجليزية
                )
                if translated_text:
                    translated_data[f'{field}_{target_language}'] = translated_text
        
        return translated_data
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        اكتشاف لغة النص
        
        Args:
            text: النص المراد اكتشاف لغته
        
        Returns:
            رمز اللغة المكتشفة
        """
        if not self.translate_client or not text:
            return None
        
        try:
            # استخدام Amazon Comprehend بدلاً من Translate للاكتشاف
            import boto3
            comprehend = boto3.client(
                'comprehend',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            response = comprehend.detect_dominant_language(Text=text)
            if response['Languages']:
                detected_language = response['Languages'][0]['LanguageCode']
                confidence = response['Languages'][0]['Score']
                print(f"✅ تم اكتشاف اللغة: {detected_language} (ثقة: {confidence:.2f}%)")
                return detected_language
            else:
                return None
            
        except Exception as e:
            print(f"❌ خطأ في اكتشاف اللغة: {e}")
            # محاولة اكتشاف بسيط بناءً على الأحرف
            if any('\u0600' <= char <= '\u06FF' for char in text):
                return 'ar'  # عربي
            elif any('\u0041' <= char <= '\u005A' or '\u0061' <= char <= '\u007A' for char in text):
                return 'en'  # إنجليزي
            else:
                return 'en'  # افتراضي
    
    def get_supported_languages(self) -> List[Dict]:
        """
        الحصول على قائمة اللغات المدعومة
        
        Returns:
            قائمة اللغات المدعومة
        """
        if not self.translate_client:
            return []
        
        try:
            response = self.translate_client.list_languages()
            languages = response['Languages']
            
            # تصفية اللغات المهمة فقط
            important_languages = ['ar', 'en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
            filtered_languages = [
                lang for lang in languages 
                if lang['LanguageCode'] in important_languages
            ]
            
            return filtered_languages
            
        except Exception as e:
            print(f"❌ خطأ في الحصول على اللغات المدعومة: {e}")
            return []
    
    def _convert_language_code(self, language_code: str) -> str:
        """
        تحويل رمز اللغة إلى التنسيق المطلوب لـ Amazon Translate
        
        Args:
            language_code: رمز اللغة
        
        Returns:
            رمز اللغة المحول
        """
        # تحويل رموز اللغات الشائعة
        language_mapping = {
            'ar': 'ar',      # العربية
            'en': 'en',      # الإنجليزية
            'fr': 'fr',      # الفرنسية
            'es': 'es',      # الإسبانية
            'de': 'de',      # الألمانية
            'it': 'it',      # الإيطالية
            'pt': 'pt',      # البرتغالية
            'ru': 'ru',      # الروسية
            'ja': 'ja',      # اليابانية
            'ko': 'ko',      # الكورية
            'zh': 'zh',      # الصينية
            'auto': 'auto'   # اكتشاف تلقائي
        }
        
        return language_mapping.get(language_code.lower(), language_code.lower())
    
    def is_available(self) -> bool:
        """
        التحقق من توفر خدمة الترجمة
        
        Returns:
            True إذا كانت الخدمة متاحة
        """
        return self.translate_client is not None

# إنشاء نسخة عامة من خدمة الترجمة
translate_service = AmazonTranslateService() 