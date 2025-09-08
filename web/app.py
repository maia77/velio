from flask import Flask, request, redirect, url_for, session, render_template, jsonify, flash, send_from_directory
from flask_babel import Babel, gettext as _
from flask_cors import CORS
import locale
import ssl
import smtplib
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

from sqlalchemy import text
from config import Config
from amazon_translate import translate_service
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared_database_config_fallback import get_database_config

app = Flask(__name__, static_folder='static', template_folder='templates')

# إعدادات التطبيق
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')
app.config['BABEL_DEFAULT_LOCALE'] = 'ar'  # اللغة الافتراضية
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'  # مكان ملفات الترجمة
app.config['LANGUAGES'] = ['ar', 'en']  # العربية أولاً





# إعدادات قاعدة البيانات - مع نظام احتياطي
# استخدام قاعدة بيانات مشتركة (PostgreSQL أو SQLite)
basedir = os.path.abspath(os.path.dirname(__file__))
db_config, is_postgresql = get_database_config()
app.config.update(db_config)
use_remote = is_postgresql

# سيتم استيراد db من models.py

# إعدادات الجلسة
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(basedir, 'instance', 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # ساعة واحدة
app.config['SESSION_FILE_THRESHOLD'] = 500

# إعدادات المصادقة للمدير
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# إعدادات تحسين الصور
IMAGE_MAX_SIZE = (1000, 1000)  # أقصى عرض/ارتفاع بالبكسل
JPEG_QUALITY = 85  # جودة JPEG مناسبة للويب

# تهيئة الكاش والإعدادات العامة
app.config.from_object(Config)

# تهيئة الجلسة
from flask_session import Session
Session(app)

# إعادة ضبط إعدادات قاعدة البيانات بعد تحميل Config لضمان عدم استبدالها
# استخدام قاعدة البيانات المختارة
app.config.update(db_config)

# استيراد النماذج قبل تهيئة قاعدة البيانات
from models import db, Product, Comment, ProductImage, Order, OrderStatusHistory

# تهيئة الإضافات
babel = Babel(app)
CORS(app)
db.init_app(app)

# إنشاء الجداول إذا لم تكن موجودة
with app.app_context():
    try:
        db.create_all()
        print("✅ تم التأكد من إنشاء جداول قاعدة البيانات")
        # التأكد من وجود الأعمدة الجديدة (متوافق مع PostgreSQL و SQLite)
        try:
            with db.engine.connect() as conn:
                if use_remote:
                    # PostgreSQL syntax
                    conn.execute(text('ALTER TABLE products ADD COLUMN IF NOT EXISTS is_home_essentials BOOLEAN DEFAULT TRUE'))
                    conn.execute(text('ALTER TABLE products ADD COLUMN IF NOT EXISTS is_new_arrival BOOLEAN DEFAULT FALSE'))
                    conn.execute(text('ALTER TABLE products ADD COLUMN IF NOT EXISTS main_category VARCHAR(100) DEFAULT \'أصالة معاصرة\''))
                    conn.execute(text('ALTER TABLE products ADD COLUMN IF NOT EXISTS main_category_ar VARCHAR(100) DEFAULT \'أصالة معاصرة\''))
                    conn.commit()
                    print('✅ تم التأكد من وجود الأعمدة الجديدة (PostgreSQL)')
                else:
                    # SQLite syntax
                    cols = [row[1] for row in conn.execute(text('PRAGMA table_info(products)'))]
                    if 'is_home_essentials' not in cols:
                        conn.execute(text('ALTER TABLE products ADD COLUMN is_home_essentials BOOLEAN DEFAULT 1'))
                        print('🆕 تم إضافة العمود is_home_essentials')
                    if 'is_new_arrival' not in cols:
                        conn.execute(text('ALTER TABLE products ADD COLUMN is_new_arrival BOOLEAN DEFAULT 0'))
                        print('🆕 تم إضافة العمود is_new_arrival')
                    if 'main_category' not in cols:
                        conn.execute(text('ALTER TABLE products ADD COLUMN main_category VARCHAR(100) DEFAULT \'أصالة معاصرة\''))
                        print('تم إضافة العمود main_category')
                    if 'main_category_ar' not in cols:
                        conn.execute(text('ALTER TABLE products ADD COLUMN main_category_ar VARCHAR(100) DEFAULT \'أصالة معاصرة\''))
                        print('تم إضافة العمود main_category_ar')
                    conn.commit()
                    print('تم التأكد من وجود الأعمدة الجديدة (SQLite)')
        except Exception as e:
            print(f"تعذر التحقق/إضافة الأعمدة الجديدة: {e}")
    except Exception as e:
        print(f"فشل إنشاء الجداول: {e}")

# إعدادات Babel المحسنة
def get_locale():
    # أولاً، تحقق من الجلسة
    if 'lang' in session:
        return session['lang']
    
    # ثانياً، تحقق من تفضيل المستخدم المحفوظ
    if 'user_preference' in session:
        session['lang'] = session['user_preference']
        return session['user_preference']
    
    # ثالثاً، تجاهل locale النظام واستخدم العربية كافتراضية
    # (لأن locale النظام قد يكون en_US مما يسبب مشاكل)
    
    # أخيراً، استخدم اللغة الافتراضية (العربية) دائماً
    session['lang'] = 'ar'
    session['user_preference'] = 'ar'  # حفظ التفضيل أيضاً
    return 'ar'

# تعيين وظيفة تحديد اللغة
babel.init_app(app, locale_selector=get_locale)

# مسار إعادة توجيه للعربية
@app.route('/ar')
@app.route('/arabic')
@app.route('/arabic/')
def redirect_to_arabic():
    """إعادة توجيه تلقائي للعربية"""
    session['lang'] = 'ar'
    session['user_preference'] = 'ar'
    session['auto_translate'] = False
    print("إعادة توجيه للعربية")
    return redirect(url_for('index'))

# صفحة اختبار اللغة العربية الافتراضية
@app.route('/test-arabic')
def test_arabic_default():
    """صفحة اختبار اللغة العربية الافتراضية"""
    # ضبط اللغة للعربية إجبارياً
    session['lang'] = 'ar'
    session['user_preference'] = 'ar'
    session['auto_translate'] = False
    print("🧪 اختبار اللغة العربية الافتراضية")
    return render_template('test_arabic_default.html')

# صفحة اختبار الترجمة المحلية
@app.route('/test-translation')
def test_local_translation():
    """صفحة اختبار الترجمة المحلية"""
    print("🧪 اختبار الترجمة المحلية")
    return render_template('test_local_translation.html')

# مسار اختبار الترجمة
@app.route('/test-translation-fix')
def test_translation_fix():
    """صفحة اختبار ترجمة "الرئيسية" إلى "Home" """
    return render_template('test_translation_fix.html')

# وظائف رفع الملفات
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# دوال المصادقة
def is_admin_logged_in():
    """التحقق من تسجيل دخول المدير"""
    return session.get('admin_logged_in', False)

def require_admin_auth(f):
    """ديكوراتور لطلب مصادقة المدير"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def save_uploaded_file(file):
    """حفظ الملف المرفوع مع تصغير وضغط الصورة تلقائياً"""
    if not (file and allowed_file(file.filename)):
        return None

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    # صور GIF (قد تكون متحركة) نحفظها كما هي بدون معالجة
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext == 'gif':
        file.save(file_path)
        return f"/static/uploads/{unique_filename}"

    try:
        image = Image.open(file.stream)
        # تصحيح الاتجاه بناءً على EXIF
        image = ImageOps.exif_transpose(image)

        # تصغير مع الحفاظ على الأبعاد
        image.thumbnail(IMAGE_MAX_SIZE, Image.Resampling.LANCZOS)

        # تحديد الصيغة وخيارات الحفظ
        fmt_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG', 'webp': 'WEBP'}
        image_format = fmt_map.get(ext, (image.format or 'JPEG'))

        save_kwargs = {}
        if image_format == 'JPEG':
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            save_kwargs = {'quality': JPEG_QUALITY, 'optimize': True}
        elif image_format == 'PNG':
            save_kwargs = {'optimize': True}
        elif image_format == 'WEBP':
            # method: 0..6 (الأعلى = أفضل ضغط)
            save_kwargs = {'quality': JPEG_QUALITY, 'method': 6}

        image.save(file_path, format=image_format, **save_kwargs)
        return f"/static/uploads/{unique_filename}"
    except Exception:
        # في حال الفشل لأي سبب، احفظ الملف كما هو
        try:
            file.save(file_path)
            return f"/static/uploads/{unique_filename}"
        except Exception:
            return None



# تحسين وظيفة تغيير اللغة مع الترجمة التلقائية
@app.route('/change_language/<lang_code>')
def change_language(lang_code):
    if lang_code in app.config['LANGUAGES']:
        session['lang'] = lang_code
        # حفظ تفضيل المستخدم
        session['user_preference'] = lang_code
        
        # تفعيل الترجمة التلقائية إذا كانت الخدمة متاحة
        if translate_service.is_available():
            session['auto_translate'] = True
            print(f"تم تفعيل الترجمة التلقائية للغة: {lang_code}")
        else:
            session['auto_translate'] = False
            print("خدمة الترجمة غير متاحة")
        
        # إذا تم تغيير اللغة إلى العربية، توجيه إلى الصفحة الرئيسية
        if lang_code == 'ar':
            print("توجيه إلى الصفحة الرئيسية باللغة العربية")
            return redirect(url_for('index'))
    
    return redirect(request.referrer or url_for('index'))

# الحصول على معلومات اللغة الحالية
@app.route('/api/language/current')
def get_current_language():
    current_lang = get_locale()
    return jsonify({
        'language': current_lang,
        'available_languages': app.config['LANGUAGES'],
        'is_rtl': current_lang == 'ar',
        'user_preference': session.get('user_preference', current_lang),
        'auto_translate': session.get('auto_translate', False),
        'translate_service_available': translate_service.is_available()
    })

# وظيفة لإعادة ضبط اللغة إلى العربية
@app.route('/api/language/reset')
def reset_language():
    session['lang'] = 'ar'
    session['user_preference'] = 'ar'
    session['auto_translate'] = False
    print("تم إعادة ضبط اللغة إلى العربية")
    return jsonify({
        'success': True,
        'message': 'تم إعادة ضبط اللغة إلى العربية',
        'language': 'ar'
    })

# تحسين وظيفة اكتشاف لغة المتصفح والترجمة التلقائية
@app.route('/api/language/detect')
def detect_browser_language():
    browser_langs = []
    if request.accept_languages:
        for lang in request.accept_languages:
            browser_langs.append({
                'code': lang[0],
                'quality': lang[1]
            })
    
    detected_lang = request.accept_languages.best_match(app.config['LANGUAGES']) if request.accept_languages else None
    
    # تحسين اكتشاف اللغة بناءً على عدة عوامل
    auto_detected_lang = detected_lang
    detection_method = 'browser_header'
    
    # إذا لم يتم اكتشاف اللغة من المتصفح، جرب locale النظام
    if not auto_detected_lang:
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                if system_locale.startswith('ar'):
                    auto_detected_lang = 'ar'
                    detection_method = 'system_locale'
                elif system_locale.startswith('en'):
                    auto_detected_lang = 'en'
                    detection_method = 'system_locale'
        except Exception as e:
            pass
    
    # إذا لم يتم اكتشاف أي لغة، استخدم الافتراضية
    if not auto_detected_lang:
        auto_detected_lang = 'ar'
        detection_method = 'default'
    
    return jsonify({
        'browser_languages': browser_langs,
        'detected_language': auto_detected_lang,
        'detection_method': detection_method,
        'current_language': get_locale(),
        'auto_translation_enabled': True,
        'translation_types': {
            'automatic': 'بناءً على جهاز المستخدم',
            'manual': 'عند الضغط على الزر'
        },
        'user_preference': session.get('user_preference', auto_detected_lang),
        'translate_service_available': translate_service.is_available()
    })

# وظائف API للترجمة
@app.route('/api/translate/text', methods=['POST'])
def translate_text_api():
    """ترجمة نص واحد"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('target_language', 'ar')
        source_language = data.get('source_language', 'auto')
        
        if not text:
            return jsonify({'success': False, 'error': 'النص مطلوب'}), 400
        
        if not translate_service.is_available():
            return jsonify({'success': False, 'error': 'خدمة الترجمة غير متاحة'}), 503
        
        translated_text = translate_service.translate_text(text, target_language, source_language)
        
        if translated_text:
            return jsonify({
                'success': True,
                'original_text': text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language
            })
        else:
            return jsonify({'success': False, 'error': 'فشل في الترجمة'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/batch', methods=['POST'])
def translate_batch_api():
    """ترجمة مجموعة من النصوص مع تحسينات الأداء"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        target_language = data.get('target_language', 'ar')
        source_language = data.get('source_language', 'auto')
        
        if not texts:
            return jsonify({'success': False, 'error': 'النصوص مطلوبة'}), 400
        
        if not translate_service.is_available():
            return jsonify({'success': False, 'error': 'خدمة الترجمة غير متاحة'}), 503
        
        # تحسين: إزالة النصوص الفارغة والتكرار
        unique_texts = list(set([text.strip() for text in texts if text.strip()]))
        
        if not unique_texts:
            return jsonify({
                'success': True,
                'original_texts': texts,
                'translated_texts': [None] * len(texts),
                'source_language': source_language,
                'target_language': target_language
            })
        
        # استخدام الترجمة المجمعة المحسنة
        translated_texts = translate_service.translate_batch(unique_texts, target_language, source_language)
        
        # إنشاء خريطة للترجمات
        translation_map = {}
        for i, text in enumerate(unique_texts):
            if i < len(translated_texts) and translated_texts[i]:
                translation_map[text] = translated_texts[i]
        
        # إرجاع النتائج بالترتيب الأصلي
        final_translations = []
        for text in texts:
            clean_text = text.strip() if text else ''
            final_translations.append(translation_map.get(clean_text))
        
        return jsonify({
            'success': True,
            'original_texts': texts,
            'translated_texts': final_translations,
            'source_language': source_language,
            'target_language': target_language,
            'performance': {
                'unique_texts': len(unique_texts),
                'total_texts': len(texts),
                'cache_hits': len(unique_texts) - len([t for t in translated_texts if t is not None])
            }
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/product/<int:product_id>', methods=['POST'])
def translate_product_api(product_id):
    """ترجمة منتج كامل"""
    try:
        data = request.get_json()
        target_language = data.get('target_language', 'ar')
        
        # البحث عن المنتج
        product = Product.query.get_or_404(product_id)
        
        if not translate_service.is_available():
            return jsonify({'success': False, 'error': 'خدمة الترجمة غير متاحة'}), 503
        
        # ترجمة بيانات المنتج
        product_data = product.to_dict()
        translated_data = translate_service.translate_product(product_data, target_language)
        
        # حفظ الترجمات في قاعدة البيانات
        if f'name_{target_language}' in translated_data:
            setattr(product, f'name_{target_language}', translated_data[f'name_{target_language}'])
        if f'description_{target_language}' in translated_data:
            setattr(product, f'description_{target_language}', translated_data[f'description_{target_language}'])
        if f'category_{target_language}' in translated_data:
            setattr(product, f'category_{target_language}', translated_data[f'category_{target_language}'])
        if f'brand_{target_language}' in translated_data:
            setattr(product, f'brand_{target_language}', translated_data[f'brand_{target_language}'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product_id': product_id,
            'translated_data': translated_data,
            'target_language': target_language
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/detect', methods=['POST'])
def detect_language_api():
    """اكتشاف لغة النص"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'النص مطلوب'}), 400
        
        if not translate_service.is_available():
            return jsonify({'success': False, 'error': 'خدمة الترجمة غير متاحة'}), 503
        
        detected_language = translate_service.detect_language(text)
        
        if detected_language:
            return jsonify({
                'success': True,
                'text': text,
                'detected_language': detected_language
            })
        else:
            return jsonify({'success': False, 'error': 'فشل في اكتشاف اللغة'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/translate/languages')
def get_supported_languages_api():
    """الحصول على اللغات المدعومة"""
    try:
        languages = translate_service.get_supported_languages()
        return jsonify({
            'success': True,
            'languages': languages,
            'total_count': len(languages)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/ids')
def get_product_ids():
    """الحصول على معرفات جميع المنتجات النشطة"""
    try:
        # الحصول على جميع المنتجات النشطة
        products = Product.query.filter_by(is_active=True).all()
        product_ids = [product.id for product in products]
        
        return jsonify({
            'success': True,
            'product_ids': product_ids,
            'total_count': len(product_ids)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500









# الصفحة العربية
@app.route('/')
def index():
    # ضبط اللغة الافتراضية عند أول زيارة - إجبارياً العربية
    session['lang'] = 'ar'
    session['user_preference'] = 'ar'
    session['auto_translate'] = False  # تعطيل الترجمة التلقائية للعربية
    print("🌍 تم ضبط اللغة الافتراضية إلى العربية إجبارياً")
    
    return render_template('index.html')

@app.route('/track-order')
def track_order_page():
    """
    صفحة متابعة الطلبات للعملاء
    """
    return render_template('track_order.html')

@app.route('/product')
def product_detail():
    """صفحة تفاصيل المنتج"""
    return render_template('product.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """حفظ الصورة وإرجاع المسار مع تصغير وضغط تلقائي"""
    return save_uploaded_file(file)

@app.route('/test-admin')
def test_admin():
    return "لوحة الإدارة تعمل!"

@app.route('/test-database')
def test_database():
    """صفحة اختبار ربط قاعدة البيانات"""
    return render_template('test_database_connection.html')

@app.route('/test-db')
def test_db():
    """صفحة اختبار قاعدة البيانات"""
    return render_template('test_db.html')

@app.route('/api/test')
def test_api():
    """اختبار API بسيط"""
    return jsonify({'success': True, 'message': 'API يعمل!'})

@app.route('/test-products-debug')
def test_products_debug():
    """صفحة اختبار المنتجات للتشخيص"""
    return send_from_directory('.', 'test_products_debug.html')

@app.route('/debug-console')
def debug_console():
    """صفحة تشخيص Console"""
    return send_from_directory('.', 'debug_console.html')

@app.route('/test-simple')
def test_simple():
    """صفحة اختبار بسيطة"""
    return send_from_directory('.', 'test_simple.html')

@app.route('/test-cart')
def test_cart():
    """صفحة اختبار السلة"""
    return send_from_directory('.', 'test_cart.html')

@app.route('/test-simple-cart')
def test_simple_cart():
    """صفحة اختبار السلة البسيطة"""
    return send_from_directory('.', 'test_simple_cart.html')

@app.route('/test-cart-simple')
def test_cart_simple():
    """صفحة اختبار السلة البسيطة الجديدة"""
    return send_from_directory('.', 'test_cart_simple.html')

@app.route('/test-products-loading')
def test_products_loading():
    """صفحة اختبار تحميل المنتجات"""
    return send_from_directory('.', 'test_products_loading.html')



@app.route('/api/products-simple')
def get_products_simple():
    """API بسيط للمنتجات"""
    try:
        # عرض الأحدث أولاً لضمان ظهور المنتجات المضافة حديثاً في الواجهة
        try:
            products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
        except Exception:
            # احتياطي في حال فشل الترتيب مع بعض قواعد البيانات القديمة
            products = Product.query.filter_by(is_active=True).all()
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'name_ar': product.name_ar,
                'description': product.description,
                'description_ar': product.description_ar,
                'price': product.price,
                'category': product.category,
                'brand': product.brand,
                'image_url': product.image_url,
                'images': [img.to_dict() for img in product.images] if hasattr(product, 'images') else [],
                'main_category': getattr(product, 'main_category', 'أصالة معاصرة'),
                'main_category_ar': getattr(product, 'main_category_ar', 'أصالة معاصرة'),
                'is_home_essentials': getattr(product, 'is_home_essentials', True) if hasattr(product, 'is_home_essentials') and getattr(product, 'is_home_essentials') is not None else True,
                'is_new_arrival': getattr(product, 'is_new_arrival', False)
            })
        
        print(f"تم إرسال {len(products_data)} منتج عبر API البسيط")
        
        return jsonify({
            'success': True, 
            'products': products_data,
            'total_count': len(products_data)
        })
    except Exception as e:
        print(f"خطأ في API المنتجات البسيط: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'products': []
        }), 500

def text_contains_arabic_characters(text):
    """تحقق سريع إذا كان النص يحتوي على أحرف عربية"""
    if not text:
        return False
    return any('\u0600' <= ch <= '\u06FF' for ch in text)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product_simple():
    """إضافة منتج جديد مع رفع الصور"""
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category', '')
            brand = request.form.get('brand', '')
            is_home_essentials = request.form.get('is_home_essentials') == 'on'
            is_new_arrival = request.form.get('is_new_arrival') == 'on'
            
            # معالجة الصور المتعددة
            image_url = ''  # الصورة الرئيسية للتوافق مع النظام القديم
            uploaded_images = []
            
            # معالجة الصور المتعددة - دعم اسمين مختلفين للحقل
            files = []
            if 'product_images' in request.files:
                files.extend(request.files.getlist('product_images'))
            if 'product_image' in request.files:
                files.append(request.files['product_image'])
            
            for i, file in enumerate(files):
                if file and file.filename:
                    uploaded_url = save_uploaded_file(file)
                    if uploaded_url:
                        uploaded_images.append({
                            'url': uploaded_url,
                            'is_primary': i == 0,  # أول صورة هي الرئيسية
                            'sort_order': i
                        })
                        if i == 0:  # الصورة الأولى تصبح الصورة الرئيسية
                            image_url = uploaded_url
            
            # إنشاء المنتج
            product = Product(
                name=name,
                description=description,
                price=price,
                category=category,
                brand=brand,
                image_url=image_url
            )
            # ضبط الأعلام الجديدة مع التعامل مع قواعد بيانات قديمة بلا أعمدة
            try:
                product.is_home_essentials = is_home_essentials
                product.is_new_arrival = is_new_arrival
            except Exception:
                pass
            
            # الترجمة التلقائية للعربية إذا كانت الخدمة متاحة
            if translate_service.is_available():
                try:
                    # معالجة كل حقل على حدة: إذا كان عربي يُنسخ كما هو، وإلا تُستخدم الترجمة التلقائية
                    if name:
                        if text_contains_arabic_characters(name):
                            product.name_ar = name
                        else:
                            translated_name = translate_service.translate_text(name, 'ar', 'auto')
                            product.name_ar = translated_name if translated_name else name
                    if description:
                        if text_contains_arabic_characters(description):
                            product.description_ar = description
                        else:
                            translated_description = translate_service.translate_text(description, 'ar', 'auto')
                            product.description_ar = translated_description if translated_description else description
                    if category:
                        if text_contains_arabic_characters(category):
                            product.category_ar = category
                        else:
                            translated_category = translate_service.translate_text(category, 'ar', 'auto')
                            product.category_ar = translated_category if translated_category else category
                    if brand:
                        if text_contains_arabic_characters(brand):
                            product.brand_ar = brand
                        else:
                            translated_brand = translate_service.translate_text(brand, 'ar', 'auto')
                            product.brand_ar = translated_brand if translated_brand else brand
                    
                    print(f"✅ تم تجهيز الحقول العربية للمنتج '{name}'")
                except Exception as e:
                    print(f"خطأ في تجهيز الحقول العربية: {e}")
                    # استخدام النص الأصلي في حالة أي خطأ
                    product.name_ar = name
                    product.description_ar = description
                    product.category_ar = category
                    product.brand_ar = brand
            else:
                # استخدام النص الأصلي إذا كانت خدمة الترجمة غير متاحة
                product.name_ar = name
                product.description_ar = description
                product.category_ar = category
                product.brand_ar = brand
            
            # حفظ المنتج في قاعدة البيانات
            db.session.add(product)
            db.session.flush()  # للحصول على ID المنتج
            
            # إضافة الصور إلى قاعدة البيانات
            for img_data in uploaded_images:
                product_image = ProductImage(
                    product_id=product.id,
                    image_url=img_data['url'],
                    is_primary=img_data['is_primary'],
                    sort_order=img_data['sort_order'],
                    created_at=datetime.utcnow()
                )
                db.session.add(product_image)
            
            db.session.commit()
            # لا حاجة لتفريغ الكاش بعد إزالته
            
            image_status = "مع صورة" if image_url else "بدون صورة"
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>تم إضافة المنتج</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                    h1 {{ color: #28a745; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
                    .product-preview {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                    .product-image {{ max-width: 200px; max-height: 200px; border-radius: 8px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ تم إضافة المنتج بنجاح!</h1>
                    <div class="product-preview">
                        <h3>{name}</h3>
                        <p><strong>الاسم العربي:</strong> {product.name_ar}</p>
                        <p><strong>السعر:</strong> {price} $</p>
                        <p><strong>حالة الصورة:</strong> {image_status}</p>
                        {f'<img src="{image_url}" class="product-image" alt="{name}">' if image_url else '<p>📦 لا توجد صورة</p>'}
                    </div>
                    <p>تم إضافة المنتج بنجاح</p>
                    <a href="/admin" class="btn">العودة للوحة الإدارة</a>
                    <a href="/admin/products/add" class="btn">إضافة منتج آخر</a>
                    <a href="/products" class="btn">عرض المنتجات</a>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            return f"خطأ في إضافة المنتج: {str(e)}", 500
    
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>إضافة منتج جديد</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
            input, textarea, select { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
            input:focus, textarea:focus, select:focus { border-color: #007bff; outline: none; }
            .file-input { border: 2px dashed #007bff; background: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; }
            .file-input:hover { background: #e9ecef; }
            button { background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 18px; font-weight: bold; margin-top: 20px; }
            button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,123,255,0.3); }
            .btn-back { background: #6c757d; margin-top: 15px; }
            .btn-back:hover { background: #5a6268; }
            .preview-image { max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 10px; }
            .help-text { font-size: 14px; color: #6c757d; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>➕ إضافة منتج جديد</h1>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>📸 صورة المنتج:</label>
                    <div class="file-input">
                        <input type="file" name="product_image" accept="image/*" onchange="previewImage(this)">
                        <p>اضغط هنا لاختيار صورة من هاتفك</p>
                        <div id="image-preview"></div>
                    </div>
                    <div class="help-text">يدعم: JPG, PNG, GIF, WebP (حجم أقصى: 16MB)</div>
                </div>
                
                <div class="form-group">
                    <label>اسم المنتج (باللغة الإنجليزية):</label>
                    <input type="text" name="name" required placeholder="مثال: Modern Chair">
                    <div class="help-text">سيتم ترجمته تلقائياً للعربية</div>
                </div>
                
                <div class="form-group">
                    <label>📝 وصف المنتج:</label>
                    <textarea name="description" rows="4" required placeholder="وصف المنتج باللغة الإنجليزية"></textarea>
                    <div class="help-text">سيتم ترجمته تلقائياً للعربية</div>
                </div>
                
                <div class="form-group">
                    <label>السعر ($):</label>
                    <input type="number" name="price" step="0.01" required placeholder="مثال: 150.00">
                </div>
                
                <div class="form-group">
                    <label>الفئة (اختياري):</label>
                    <select name="category">
                        <option value="">اختر الفئة</option>
                        <option value="أثاث">أثاث</option>
                        <option value="إلكترونيات">إلكترونيات</option>
                        <option value="ملابس">ملابس</option>
                        <option value="أحذية">أحذية</option>
                        <option value="ساعات">ساعات</option>
                        <option value="حقائب">حقائب</option>
                        <option value="ألعاب">ألعاب</option>
                        <option value="كتب">كتب</option>
                        <option value="أخرى">أخرى</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>العلامة التجارية (اختياري):</label>
                    <input type="text" name="brand" placeholder="مثال: IKEA, Samsung, Nike">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_home_essentials" checked>
                        عرض في قسم "كل ما يحتاجه منزلك"
                    </label>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_new_arrival">
                        إضافة إلى قسم "وصل حديثاً"
                    </label>
                </div>
                
                <button type="submit">إضافة المنتج</button>
            </form>
            <a href="/admin" class="btn btn-back">العودة للوحة الإدارة</a>
        </div>
        
        <script>
            function previewImage(input) {
                const preview = document.getElementById('image-preview');
                if (input.files && input.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.innerHTML = '<img src="' + e.target.result + '" class="preview-image" alt="معاينة الصورة">';
                    }
                    reader.readAsDataURL(input.files[0]);
                } else {
                    preview.innerHTML = '';
                }
            }
        </script>
    </body>
    </html>
    """


@app.route('/admin')
@require_admin_auth
def admin_dashboard():
    """لوحة تحكم المدير"""
    try:
        products = Product.query.filter_by(is_active=True).all()
        return render_template('admin_products.html', products=products)
    except Exception as e:
        print(f"خطأ في لوحة تحكم المدير: {e}")
        return f"خطأ في عرض لوحة التحكم: {str(e)}", 500

# الصفحة الإنجليزية
@app.route('/index-en.html')
def index_en():
    return render_template('index-en.html')

# تشغيل التطبيق (تم الإبقاء على تشغيل واحد في نهاية الملف بعد تعريف جميع المسارات)

# --- إعدادات البريد الإلكتروني ---
# دعم متعدد لمقدمي الخدمة
EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER', 'yahoo').lower()  # yahoo, gmail, outlook

# إعدادات SMTP حسب المزود
if EMAIL_PROVIDER == 'gmail':
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
elif EMAIL_PROVIDER == 'yahoo':
    SMTP_SERVER = "smtp.mail.yahoo.com"
    SMTP_PORT = 587  # Yahoo يستخدم 587 مع TLS
elif EMAIL_PROVIDER == 'outlook':
    SMTP_SERVER = "smtp-mail.outlook.com"
    SMTP_PORT = 587
else:
    # افتراضي Yahoo
    SMTP_SERVER = "smtp.mail.yahoo.com"
    SMTP_PORT = 587

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', '')  # يجب إضافة البريد الإلكتروني من متغيرات البيئة
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '') # يجب إضافة كلمة مرور التطبيقات من متغيرات البيئة
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', SENDER_EMAIL)  # البريد المطلوب لاستقبال الإشعارات (نفس المرسل إذا لم يتم تحديد مستقبل)

def send_email(subject, body, from_name="Velio Store"):
    """
    دالة لإرسال إشعار عبر البريد الإلكتروني مع دعم متعدد المزودين.
    """
    print(f"📧 محاولة إرسال بريد إلكتروني: {subject}")
    print(f"إعدادات البريد: SENDER_EMAIL={SENDER_EMAIL}, RECEIVER_EMAIL={RECEIVER_EMAIL}")
    print(f"المزود: {EMAIL_PROVIDER}, الخادم: {SMTP_SERVER}:{SMTP_PORT}")
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("إعدادات البريد الإلكتروني غير مكتملة. يرجى إضافة SENDER_EMAIL و SENDER_PASSWORD")
        print("يمكنك تخطي إرسال البريد الإلكتروني والمتابعة مع إنشاء الطلب")
        return False
    
    if not RECEIVER_EMAIL:
        print("عنوان البريد المستقبل غير محدد")
        return False
    
    try:
        # إنشاء رسالة محسنة
        message = f"""From: {from_name} <{SENDER_EMAIL}>
To: {RECEIVER_EMAIL}
Subject: {subject}
Content-Type: text/plain; charset=UTF-8

{body}

---
تم إرسال هذه الرسالة تلقائياً من موقع Velio Store
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.encode('utf-8')
        
        print(f"📧 محاولة الإرسال عبر {EMAIL_PROVIDER.upper()}: {SMTP_SERVER}:{SMTP_PORT}")
        
        # إرسال حسب نوع المزود
        if EMAIL_PROVIDER == 'gmail':
            # Gmail يستخدم SSL
            print("🔐 استخدام SSL مع Gmail...")
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                print("🔑 محاولة تسجيل الدخول...")
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                print("📤 إرسال الرسالة...")
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
        else:
            # Yahoo و Outlook يستخدمان TLS
            print("🔐 استخدام TLS مع Yahoo/Outlook...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                print("🔒 تفعيل TLS...")
                server.starttls()  # تفعيل TLS
                print("🔑 محاولة تسجيل الدخول...")
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                print("📤 إرسال الرسالة...")
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
        
        print(f"✅ تم إرسال إشعار البريد الإلكتروني بنجاح إلى {RECEIVER_EMAIL}: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ خطأ في المصادقة: {e}")
        print("تأكد من صحة اسم المستخدم وكلمة المرور")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ رفض المستقبل: {e}")
        print("تأكد من صحة عنوان البريد المستقبل")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ انقطع الاتصال بالخادم: {e}")
        print("تحقق من إعدادات SMTP")
        return False
    except Exception as e:
        print(f"❌ فشل في إرسال إشعار البريد الإلكتروني: {e}")
        print(f"🔍 المزود: {EMAIL_PROVIDER}, الخادم: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"📧 المرسل: {SENDER_EMAIL}, المستقبل: {RECEIVER_EMAIL}")
        return False

# --- بيانات تجريبية (قاعدة بيانات مؤقتة في الذاكرة) ---
SAMPLE_PRODUCTS = [
    {
        "product_id": 1, 
        "name": "Modern Wooden Chair", 
        "description": "Comfortable and elegant chair for living room", 
        "price": 1500, 
        "image_url": "/static/images/product1.jpg",
        "category": "Furniture",
        "brand": "IKEA"
    },
    {
        "product_id": 2, 
        "name": "Leather Sofa", 
        "description": "Luxury black leather sofa for family room", 
        "price": 800, 
        "image_url": "/static/images/product2.jpg",
        "category": "Living Room",
        "brand": "Ashley"
    },
    {
        "product_id": 3, 
        "name": "Glass Coffee Table", 
        "description": "Modern glass coffee table with metal legs", 
        "price": 2200, 
        "image_url": "/static/images/product3.jpg",
        "category": "Living Room",
        "brand": "West Elm"
    },
    {
        "product_id": 4, 
        "name": "Bedroom Lamp", 
        "description": "Elegant bedside lamp with fabric shade", 
        "price": 450, 
        "image_url": "/static/images/product4.jpg",
        "category": "Lighting",
        "brand": "Target"
    }
]



contact_messages = []
orders = []
gps_locations = []  # قائمة لحفظ بيانات GPS

# --- نقاط النهاية (API Routes) ---

@app.route('/api/gps/location', methods=['POST'])
def receive_gps_location():
    """
    يستقبل بيانات الموقع الجغرافي (GPS) من الواجهة الأمامية ويحفظها.
    """
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'success': False, 'error': 'بيانات الموقع مفقودة. يرجى إرسال خط العرض وخط الطول.'}), 400

        # إنشاء سجل موقع جديد
        location_record = {
            'id': len(gps_locations) + 1,
            'latitude': float(data['latitude']),
            'longitude': float(data['longitude']),
            'source': data.get('source', 'unknown'),  # مصدر الطلب (order, contact, etc.)
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'received_at': datetime.now().isoformat()
        }

        # حفظ الموقع في القائمة
        gps_locations.append(location_record)

        # إرسال إشعار بالبريد الإلكتروني (اختياري)
        email_subject = f"موقع جديد تم استلامه - {location_record['source']}"
        email_body = f"""
تم استلام موقع جديد:

المعرف: {location_record['id']}
خط العرض: {location_record['latitude']}
خط الطول: {location_record['longitude']}
المصدر: {location_record['source']}
الوقت: {location_record['timestamp']}

رابط الخرائط: https://www.google.com/maps?q={location_record['latitude']},{location_record['longitude']}
        """
        send_email(email_subject, email_body)

        print(f"📍 تم حفظ موقع جديد: {location_record}")

        return jsonify({
            'success': True, 
            'message': 'تم حفظ الموقع بنجاح!',
            'location_id': location_record['id']
        }), 201
        
    except Exception as e:
        print(f"❌ خطأ في معالجة بيانات الموقع: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'}), 500

@app.route('/api/gps/locations', methods=['GET'])
def get_gps_locations():
    """
    يعيد قائمة بجميع المواقع المحفوظة.
    """
    try:
        return jsonify({
            'success': True, 
            'locations': gps_locations,
            'total_count': len(gps_locations)
        }), 200
    except Exception as e:
        print(f"❌ خطأ في استرجاع المواقع: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الخادم.'}), 500

@app.route('/api/contact/messages', methods=['POST'])
def receive_contact_message():
    """
    يستقبل رسائل نموذج "تواصل معنا" ويرسل إشعارًا بالبريد الإلكتروني.
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'email' not in data or 'message' not in data:
            return jsonify({'success': False, 'error': 'البيانات المطلوبة مفقودة. يرجى ملء جميع الحقول المطلوبة.'}), 400

        # حفظ الرسالة (اختياري)
        contact_messages.append(data)

        # إرسال إشعار محسن
        subject = data.get('subject', 'لا يوجد موضوع')
        phone = data.get('phone', 'غير محدد')
        email_subject = f"📧 رسالة تواصل جديدة من {data['name']}"
        email_body = f"""🔔 إشعار جديد من موقع Velio Store

👤 معلومات المرسل:
الاسم: {data['name']}
البريد الإلكتروني: {data['email']}
رقم الهاتف: {phone}
الموضوع: {subject}
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 محتوى الرسالة:
{data['message']}"""
        
        # إضافة الموقع إذا كان متوفراً
        if 'location' in data and data['location']:
            import urllib.parse
            encoded_location = urllib.parse.quote_plus(data['location'])
            map_link = f"https://www.google.com/maps/search/?api=1&query={encoded_location}"
            email_body += f"\n\nالموقع:\n{data['location']}\nرابط الخريطة: {map_link}"
        
        email_body += f"""

للرد على العميل:
- البريد الإلكتروني: {data['email']}
- الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
        
        send_email(email_subject, email_body)

        return jsonify({'success': True, 'message': 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.'}), 200
        
    except Exception as e:
        print(f"❌ خطأ في معالجة رسالة التواصل: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """
    ينشئ طلبًا جديدًا في قاعدة البيانات مع نظام حالة الطلبات
    """
    try:
        data = request.get_json()
        product_id = int(data['product_id'])
        quantity = int(data['quantity'])
        customer_info = data.get('customer_info', {})

        # البحث عن المنتج في قاعدة البيانات
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        # إنشاء رقم طلب فريد
        import uuid
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # إنشاء الطلب في قاعدة البيانات
        new_order = Order(
            order_number=order_number,
            product_id=product_id,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
            total_price=product.price * quantity,
            customer_name=customer_info.get('name', 'غير محدد'),
            customer_email=customer_info.get('email'),
            customer_phone=customer_info.get('phone'),
            customer_address=customer_info.get('address'),
            customer_country=customer_info.get('country'),
            payment_method=customer_info.get('payment_method'),
            status='pending',
            status_ar='قيد المراجعة'
        )

        db.session.add(new_order)
        db.session.commit()

        # إنشاء سجل في تاريخ الحالة
        status_history = OrderStatusHistory(
            order_id=new_order.id,
            old_status=None,
            new_status='pending',
            changed_by='system',
            notes='تم إنشاء الطلب'
        )
        db.session.add(status_history)
        db.session.commit()

        # إرسال إشعار بالبريد الإلكتروني محسن
        email_subject = f"طلب جديد #{new_order.order_number} - {product.name}"
        email_body = f"""إشعار طلب جديد من موقع Velio Store

تفاصيل الطلب:
رقم الطلب: #{new_order.order_number}
المنتج: {product.name}
الكمية: {quantity}
السعر الواحد: {product.price} $
السعر الإجمالي: {new_order.total_price} $
التاريخ: {new_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
الحالة: {new_order.get_status_display('ar')}

👤 معلومات العميل:"""
        
        # إضافة تفاصيل العميل إذا كانت متوفرة
        if customer_info:
            for key, value in customer_info.items():
                if value:
                    email_body += f"\n{key}: {value}"
                    # إضافة رابط الخريطة إذا كان المفتاح يحتوي على "عنوان" أو "address"
                    if any(keyword in key.lower() for keyword in ['عنوان', 'address', 'location', 'موقع']):
                        import urllib.parse
                        encoded_address = urllib.parse.quote_plus(str(value))
                        map_link = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                        email_body += f"\nرابط الخريطة: {map_link}"
        else:
            email_body += "\nلم يتم توفير معلومات العميل"
        
        email_body += f"""

للتواصل مع العميل:
- رقم الطلب: #{new_order.order_number}
- الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
        
        # إرسال إشعار للمدير
        send_email(email_subject, email_body)
        
        # إرسال إشعار تأكيد للعميل
        if new_order.customer_email:
            customer_subject = f"تأكيد استلام طلبك #{new_order.order_number}"
            customer_body = f"""مرحباً {new_order.customer_name},

شكراً لك على طلبك! تم استلام طلبك بنجاح وسنقوم بمراجعته قريباً.

📋 تفاصيل طلبك:
رقم الطلب: #{new_order.order_number}
المنتج: {new_order.product_name}
الكمية: {new_order.quantity}
السعر الإجمالي: {new_order.total_price} $
الحالة الحالية: {new_order.get_status_display('ar')}

للاستفسارات، يرجى التواصل معنا على:
- البريد الإلكتروني: velio.contact@yahoo.com
- رقم الطلب: #{new_order.order_number}

شكراً لاختيارك متجرنا!

---
Velio Store"""
            
            send_customer_email(new_order.customer_email, customer_subject, customer_body)

        return jsonify({
            'success': True,
            'message': 'تم إنشاء طلبك بنجاح! سنتواصل معك قريباً لتأكيد الطلب.',
            'order_number': new_order.order_number,
            'order_id': new_order.id
        }), 201

    except Exception as e:
        print(f"❌ خطأ في إنشاء الطلب: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى.'}), 500

@app.route('/api/orders/<order_number>', methods=['GET'])
def get_order_status(order_number):
    """
    الحصول على حالة طلب معين
    """
    try:
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            return jsonify({'success': False, 'error': 'الطلب غير موجود'}), 404
        
        # الحصول على تاريخ الحالة
        status_history = OrderStatusHistory.query.filter_by(order_id=order.id).order_by(OrderStatusHistory.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'order': order.to_dict(),
            'status_history': [history.to_dict() for history in status_history]
        })
    except Exception as e:
        print(f"❌ خطأ في الحصول على حالة الطلب: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الحصول على حالة الطلب'}), 500

@app.route('/api/orders/search', methods=['POST'])
def search_orders():
    """
    البحث عن الطلبات برقم الهاتف أو البريد الإلكتروني
    """
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').strip()
        
        if not search_term:
            return jsonify({'success': False, 'error': 'يرجى إدخال رقم الهاتف أو البريد الإلكتروني'}), 400
        
        # البحث في قاعدة البيانات
        orders = Order.query.filter(
            (Order.customer_phone.contains(search_term)) | 
            (Order.customer_email.contains(search_term))
        ).order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders]
        })
    except Exception as e:
        print(f"❌ خطأ في البحث عن الطلبات: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في البحث عن الطلبات'}), 500

@app.route('/api/admin/orders', methods=['GET'])
@require_admin_auth
def get_all_orders():
    """
    الحصول على جميع الطلبات (للمدير)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', '')
        
        query = Order.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        })
    except Exception as e:
        print(f"❌ خطأ في الحصول على الطلبات: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الحصول على الطلبات'}), 500

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@require_admin_auth
def update_order_status(order_id):
    """
    تحديث حالة الطلب (للمدير)
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        rejection_reason = data.get('rejection_reason', '')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'يرجى تحديد الحالة الجديدة'}), 400
        
        # التحقق من صحة الحالة
        valid_statuses = ['pending', 'processing', 'approved', 'shipped', 'rejected', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': 'حالة غير صحيحة'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'الطلب غير موجود'}), 404
        
        old_status = order.status
        
        # تحديث حالة الطلب
        order.status = new_status
        order.status_ar = order.get_status_display('ar')
        order.updated_at = datetime.utcnow()
        
        # تحديث التواريخ الخاصة
        if new_status == 'processing' and not order.processed_at:
            order.processed_at = datetime.utcnow()
        elif new_status == 'completed' and not order.completed_at:
            order.completed_at = datetime.utcnow()
        
        
        # إضافة سبب الرفض
        if new_status == 'rejected' and rejection_reason:
            order.rejection_reason = rejection_reason
        
        # إنشاء سجل في تاريخ الحالة
        status_history = OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=new_status,
            changed_by='admin',
            notes=f'تم تغيير الحالة من {old_status} إلى {new_status}'
        )
        
        db.session.add(status_history)
        db.session.commit()
        
        # إرسال إشعار للعميل (إذا كان لديه بريد إلكتروني)
        if order.customer_email:
            send_order_status_notification(order, new_status)
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة الطلب بنجاح',
            'order': order.to_dict()
        })
    except Exception as e:
        print(f"❌ خطأ في تحديث حالة الطلب: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'حدث خطأ في تحديث حالة الطلب'}), 500

@app.route('/api/admin/orders/delete-all', methods=['DELETE'])
@require_admin_auth
def delete_all_orders():
    """
    حذف جميع الطلبات (للمدير)
    """
    try:
        # حذف تاريخ حالة الطلبات أولاً
        OrderStatusHistory.query.delete()
        
        # حذف جميع الطلبات
        deleted_count = Order.query.count()
        Order.query.delete()
        
        # حفظ التغييرات
        db.session.commit()
        
        print(f"🗑️ تم حذف {deleted_count} طلب بواسطة المدير")
        
        return jsonify({
            'success': True,
            'message': f'تم حذف {deleted_count} طلب بنجاح',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ في حذف الطلبات: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في حذف الطلبات'}), 500


def send_customer_email(customer_email, subject, body):
    """
    دالة لإرسال إشعار للعميل عبر البريد الإلكتروني
    """
    print(f"📧 محاولة إرسال بريد إلكتروني للعميل: {subject}")
    print(f"👤 بريد العميل: {customer_email}")
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠️ إعدادات البريد الإلكتروني غير مكتملة. يرجى إضافة SENDER_EMAIL و SENDER_PASSWORD")
        return False
    
    if not customer_email:
        print("⚠️ عنوان البريد الإلكتروني للعميل غير محدد")
        return False
    
    try:
        # إنشاء رسالة محسنة
        message = f"""From: Velio Store <{SENDER_EMAIL}>
To: {customer_email}
Subject: {subject}
Content-Type: text/plain; charset=UTF-8

{body}"""

        # إعداد السياق الأمني
        context = ssl.create_default_context()
        
        if EMAIL_PROVIDER == 'gmail':
            # Gmail يستخدم SSL
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                print("🔑 محاولة تسجيل الدخول...")
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                print("📤 إرسال الرسالة...")
                server.sendmail(SENDER_EMAIL, customer_email, message)
        else:
            # Yahoo و Outlook يستخدمان TLS
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()  # تفعيل TLS
                print("🔑 محاولة تسجيل الدخول...")
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                print("📤 إرسال الرسالة...")
                server.sendmail(SENDER_EMAIL, customer_email, message)
        
        print(f"✅ تم إرسال إشعار البريد الإلكتروني بنجاح إلى العميل {customer_email}: {subject}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ خطأ في المصادقة: {e}")
        print("💡 تأكد من صحة كلمة مرور التطبيقات")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ تم رفض المستقبل: {e}")
        return False
    except Exception as e:
        print(f"❌ فشل في إرسال إشعار البريد الإلكتروني للعميل: {e}")
        print(f"🔍 المزود: {EMAIL_PROVIDER}, الخادم: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"📧 المرسل: {SENDER_EMAIL}, المستقبل: {customer_email}")
        return False


def send_order_status_notification(order, new_status):
    """
    إرسال إشعار للعميل عند تغيير حالة الطلب
    """
    try:
        # التحقق من وجود بريد العميل
        if not order.customer_email:
            print(f"⚠️ لا يوجد بريد إلكتروني للعميل في الطلب #{order.order_number}")
            return False
            
        status_messages = {
            'processing': 'تم بدء معالجة طلبك',
            'approved': 'تم الموافقة على طلبك',
            'shipped': 'تم إرسال طلبك',
            'rejected': 'تم رفض طلبك',
            'completed': 'تم إكمال طلبك بنجاح',
            'cancelled': 'تم إلغاء طلبك'
        }
        
        subject = f"تحديث حالة طلبك #{order.order_number}"
        message = status_messages.get(new_status, f'تم تحديث حالة طلبك إلى: {order.get_status_display("ar")}')
        
        email_body = f"""مرحباً {order.customer_name},

{message}

تفاصيل الطلب:
رقم الطلب: #{order.order_number}
المنتج: {order.product_name}
الكمية: {order.quantity}
السعر الإجمالي: {order.total_price} $
الحالة الحالية: {order.get_status_display('ar')}

"""
        
        if order.rejection_reason:
            email_body += f"سبب الرفض: {order.rejection_reason}\n\n"
        
        email_body += "شكراً لاختيارك متجرنا!\n\n---\nVelio Store"
        
        # إرسال الإشعار للعميل
        return send_customer_email(order.customer_email, subject, email_body)
        
    except Exception as e:
        print(f"❌ خطأ في إرسال إشعار العميل: {e}")
        return False

@app.route('/order-status')
def order_status_page():
    """
    صفحة استعلام حالة الطلب للعملاء
    """
    return render_template('order_status.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """صفحة تسجيل دخول المدير"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_orders_page'))
        else:
            return render_template('admin_login.html', error='اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """تسجيل خروج المدير"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/orders')
@require_admin_auth
def admin_orders_page():
    """
    صفحة إدارة الطلبات للمدير
    """
    return render_template('admin_orders.html')

@app.route('/admin/products/add')
@require_admin_auth
def admin_add_product():
    """
    صفحة إضافة منتج جديد للمدير
    """
    return redirect('/add')

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    يعيد قائمة بجميع المنتجات المتاحة من قاعدة البيانات.
    """
    try:
        # ترتيب بالمنتجات الأحدث أولاً لنتائج أكثر منطقية
        try:
            products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
        except Exception:
            products = Product.query.filter_by(is_active=True).all()
        products_data = []
        for product in products:
            # تحديد اللغة الأصلية لكل حقل
            name_language = 'en' if product.name and not any('\u0600' <= char <= '\u06FF' for char in product.name) else 'ar'
            description_language = 'en' if product.description and not any('\u0600' <= char <= '\u06FF' for char in product.description) else 'ar'
            category_language = 'en' if product.category and not any('\u0600' <= char <= '\u06FF' for char in product.category) else 'ar'
            brand_language = 'en' if product.brand and not any('\u0600' <= char <= '\u06FF' for char in product.brand) else 'ar'
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'name_ar': product.name_ar,
                'name_language': name_language,  # إضافة معلومات اللغة الأصلية
                'description': product.description,
                'description_ar': product.description_ar,
                'description_language': description_language,  # إضافة معلومات اللغة الأصلية
                'price': product.price,
                'category': product.category,
                'category_language': category_language,  # إضافة معلومات اللغة الأصلية
                'brand': product.brand,
                'brand_language': brand_language,  # إضافة معلومات اللغة الأصلية
                'image_url': product.image_url,
                'images': [img.to_dict() for img in product.images] if hasattr(product, 'images') else []
            })
        
        print(f"تم إرسال {len(products_data)} منتج عبر API مع معلومات اللغة")
        
        return jsonify({
            'success': True, 
            'products': products_data,
            'total_count': len(products_data)
        })
    except Exception as e:
        print(f"خطأ في API المنتجات: {e}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'products': []
        }), 500


# --- تعليقات المنتجات ---
@app.route('/api/products/<int:product_id>/comments', methods=['GET'])
def get_product_comments(product_id):
    """جلب التعليقات المعتمدة لمنتج معين"""
    try:
        # تحقق من أن المنتج موجود
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        comments = Comment.query.filter_by(product_id=product_id, is_approved=True).order_by(Comment.created_at.desc()).all()
        return jsonify({
            'success': True,
            'comments': [c.to_dict() for c in comments],
            'total_count': len(comments)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/comments', methods=['POST'])
def add_product_comment(product_id):
    """إضافة تعليق جديد لمنتج مع إمكانية رفع صورة"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        # التحقق من نوع الطلب
        if request.content_type and 'multipart/form-data' in request.content_type:
            # طلب مع ملف (صورة)
            name = (request.form.get('name') or '').strip()
            content = (request.form.get('content') or '').strip()
            rating = request.form.get('rating')
            image_file = request.files.get('image')
            
            # حفظ الصورة إذا تم رفعها
            image_url = None
            if image_file and image_file.filename:
                image_url = save_uploaded_file(image_file)
        else:
            # طلب JSON عادي
            data = request.get_json(silent=True) or {}
            name = (data.get('name') or '').strip()
            content = (data.get('content') or '').strip()
            rating = data.get('rating')
            image_url = None

        if not name or not content:
            return jsonify({'success': False, 'error': 'الاسم والمحتوى مطلوبان'}), 400

        try:
            # معالجة التقييم - تحويل السلسلة الفارغة إلى None
            if rating is None or rating == '' or rating == 'null':
                rating_value = None
            else:
                rating_value = int(rating)
                if rating_value < 1 or rating_value > 5:
                    return jsonify({'success': False, 'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400
        except (ValueError, TypeError):
            rating_value = None

        comment = Comment(
            product_id=product_id, 
            name=name,
            content=content, 
            rating=rating_value,
            image_url=image_url
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify({'success': True, 'comment': comment.to_dict()}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """
    نقطة نهاية وهمية لتسجيل المستخدمين.
    """
    return jsonify({'success': True, 'message': 'تم تسجيل المستخدم بنجاح'}), 201

# --- المسارات الرئيسية ---

# مسار الصفحة الرئيسية (محدث)
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/category/<category_name>')
def category_products(category_name):
    """عرض المنتجات حسب القسم المحدد"""
    try:
        # تحديد معلومات القسم
        category_info = {
            'اصالة-معاصرة': {
                'title': 'أصالة معاصرة',
                'description': 'جمع بين الأصالة والحداثة في تصميم منزلك',
                'filter': 'أصالة معاصرة'
            },
            'تفاصيل-مميزة': {
                'title': 'تفاصيل مميزة',
                'description': 'اهتم بالتفاصيل الصغيرة التي تحدث فرقاً كبيراً',
                'filter': 'تفاصيل مميزة'
            },
            'لمسات-فريدة': {
                'title': 'لمسات فريدة',
                'description': 'قطع مميزة تضيف لمسة خاصة لمنزلك',
                'filter': 'لمسات فريدة'
            },
            'زينة-الطبيعة': {
                'title': 'زينة الطبيعة',
                'description': 'أضف لمسة من الطبيعة إلى منزلك مع مجموعتنا المميزة',
                'filter': 'زينة الطبيعة'
            }
        }
        
        if category_name not in category_info:
            return "القسم غير موجود", 404
        
        info = category_info[category_name]
        
        # جلب المنتجات حسب القسم
        products = Product.query.filter(
            Product.is_active == True,
            (Product.main_category == info['filter']) | (Product.main_category_ar == info['filter'])
        ).all()
        
        return render_template('category_products.html', 
                             products=products,
                             category_title=info['title'],
                             category_description=info['description'])
                             
    except Exception as e:
        print(f"خطأ في عرض منتجات القسم {category_name}: {e}")
        return "خطأ في عرض المنتجات", 500


# مسار صفحة "من نحن"
@app.route('/about')
def about_page():
    return render_template('index.html')

# مسار صفحة "اتصل بنا"
@app.route('/contact')
def contact_page():
    return render_template('index.html')



# --- وظائف إدارة المنتجات ---

@app.route('/admin/products')
def admin_products():
    """صفحة إدارة المنتجات"""
    try:
        products = Product.query.filter_by(is_active=True).all()
        print(f"تم العثور على {len(products)} منتج في صفحة المدير")
        return render_template('admin_products.html', products=products)
    except Exception as e:
        print(f"خطأ في صفحة إدارة المنتجات: {e}")
        return f"خطأ في عرض المنتجات: {str(e)}", 500

@app.route('/admin/products/')
def admin_products_alt():
    """مسار بديل لإدارة المنتجات"""
    try:
        products = Product.query.filter_by(is_active=True).all()
        print(f"تم العثور على {len(products)} منتج في المسار البديل")
        return render_template('admin_products.html', products=products)
    except Exception as e:
        print(f"خطأ في المسار البديل: {e}")
        return f"خطأ في عرض المنتجات: {str(e)}", 500

@app.route('/admin/products/add', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج جديد"""
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category', '')
            brand = request.form.get('brand', '')
            main_category = request.form.get('main_category', 'أصالة معاصرة')
            # سنعتمد على رفع الصورة فقط، بدون رابط صورة
            image_url = ''
            is_home_essentials = request.form.get('is_home_essentials') == 'on'
            is_new_arrival = request.form.get('is_new_arrival') == 'on'
            
            # معالجة الصورة المرفوعة
            if 'product_image' in request.files:
                uploaded_file = request.files['product_image']
                if uploaded_file.filename != '':
                    uploaded_image_url = save_uploaded_file(uploaded_file)
                    if uploaded_image_url:
                        image_url = uploaded_image_url
            
            # إنشاء المنتج
            product = Product(
                name=name,
                description=description,
                price=price,
                category=category,
                brand=brand,
                main_category=main_category,
                image_url=image_url
            )
            
            # الترجمة/النسخ التلقائي إلى الحقول العربية
            if translate_service.is_available():
                try:
                    # معالجة كل حقل على حدة
                    if name:
                        if text_contains_arabic_characters(name):
                            product.name_ar = name
                        else:
                            translated_name = translate_service.translate_text(name, 'ar', 'auto')
                            product.name_ar = translated_name if translated_name else name
                    if description:
                        if text_contains_arabic_characters(description):
                            product.description_ar = description
                        else:
                            translated_description = translate_service.translate_text(description, 'ar', 'auto')
                            product.description_ar = translated_description if translated_description else description
                    if category:
                        if text_contains_arabic_characters(category):
                            product.category_ar = category
                        else:
                            translated_category = translate_service.translate_text(category, 'ar', 'auto')
                            product.category_ar = translated_category if translated_category else category
                    if brand:
                        if text_contains_arabic_characters(brand):
                            product.brand_ar = brand
                        else:
                            translated_brand = translate_service.translate_text(brand, 'ar', 'auto')
                            product.brand_ar = translated_brand if translated_brand else brand
                    
                    # ترجمة القسم الرئيسي
                    if main_category:
                        if text_contains_arabic_characters(main_category):
                            product.main_category_ar = main_category
                        else:
                            translated_main_category = translate_service.translate_text(main_category, 'ar', 'auto')
                            product.main_category_ar = translated_main_category if translated_main_category else main_category
                    
                    print(f"✅ تم تجهيز الحقول العربية للمنتج '{name}'")
                except Exception as e:
                    print(f"خطأ في تجهيز الحقول العربية: {e}")
                    product.name_ar = name
                    product.description_ar = description
                    product.category_ar = category
                    product.brand_ar = brand
                    product.main_category_ar = main_category
            else:
                product.name_ar = name
                product.description_ar = description
                product.category_ar = category
                product.brand_ar = brand
                product.main_category_ar = main_category
            
            # ضبط الأعلام الجديدة إن وُجدت حقول في قاعدة البيانات
            try:
                product.is_home_essentials = is_home_essentials
                product.is_new_arrival = is_new_arrival
            except Exception:
                pass

            db.session.add(product)
            db.session.commit()
            # لا حاجة لتفريغ الكاش بعد إزالته
            
            return "تم إضافة المنتج بنجاح!"
            
        except Exception as e:
            return f"خطأ في إضافة المنتج: {str(e)}", 500
    
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>إضافة منتج جديد</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .file-input { border: 2px dashed #007bff; padding: 20px; text-align: center; border-radius: 5px; margin: 10px 0; }
            .help-text { font-size: 12px; color: #666; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>➕ إضافة منتج جديد</h1>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>اسم المنتج:</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>الوصف:</label>
                    <textarea name="description" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label>السعر:</label>
                    <input type="number" name="price" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>الفئة:</label>
                    <input type="text" name="category">
                </div>
                <div class="form-group">
                    <label>العلامة التجارية:</label>
                    <input type="text" name="brand">
                </div>
                <div class="form-group">
                    <label>القسم الرئيسي:</label>
                    <input type="text" name="main_category">
                </div>
                <div class="form-group">
                    <label>صورة المنتج:</label>
                    <div class="file-input">
                        <input type="file" name="product_image" accept="image/*" required>
                        <div class="help-text">اختر صورة للمنتج (JPG, PNG, GIF, WebP)</div>
                    </div>
                </div>
                <button type="submit">إضافة المنتج</button>
            </form>
            <p><a href="/admin">العودة للوحة الإدارة</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """تعديل منتج موجود"""
    try:
        product = Product.query.get_or_404(product_id)
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطأ</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                h1 {{ color: #dc3545; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ المنتج غير موجود</h1>
                <p>المنتج برقم {product_id} غير موجود.</p>
                <a href="/view-products" class="btn">العودة لعرض المنتجات</a>
            </div>
        </body>
        </html>
        """
    
    if request.method == 'POST':
        try:
            # تحديث البيانات
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.price = float(request.form.get('price'))
            product.category = request.form.get('category', '')
            product.brand = request.form.get('brand', '')
            product.image_url = request.form.get('image_url', '')

            # معالجة صورة جديدة إذا تم رفعها
            if 'product_image' in request.files:
                new_file = request.files['product_image']
                if new_file and new_file.filename != '':
                    new_url = save_uploaded_file(new_file)
                    if new_url:
                        product.image_url = new_url
            
            # تجهيز الحقول العربية بعد التعديل
            if translate_service.is_available():
                try:
                    if any(text_contains_arabic_characters(t) for t in [product.name, product.description, product.category, product.brand]):
                        product.name_ar = product.name
                        product.description_ar = product.description
                        product.category_ar = product.category
                        product.brand_ar = product.brand
                    else:
                        if product.name:
                            translated_name = translate_service.translate_text(product.name, 'ar', 'auto')
                            product.name_ar = translated_name if translated_name else product.name
                        if product.description:
                            translated_description = translate_service.translate_text(product.description, 'ar', 'auto')
                            product.description_ar = translated_description if translated_description else product.description
                        if product.category:
                            translated_category = translate_service.translate_text(product.category, 'ar', 'auto')
                            product.category_ar = translated_category if translated_category else product.category
                        if product.brand:
                            translated_brand = translate_service.translate_text(product.brand, 'ar', 'auto')
                            product.brand_ar = translated_brand if translated_brand else product.brand
                    print(f"✅ تم تجهيز الحقول العربية بعد التعديل: '{product.name}'")
                except Exception as e:
                    print(f"⚠️ خطأ في تجهيز الحقول العربية بعد التعديل: {e}")
                    product.name_ar = product.name
                    product.description_ar = product.description
                    product.category_ar = product.category
                    product.brand_ar = product.brand
            else:
                product.name_ar = product.name
                product.description_ar = product.description
                product.category_ar = product.category
                product.brand_ar = product.brand
            
            db.session.commit()
            # لا حاجة لتفريغ الكاش بعد إزالته
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>تم التحديث</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                    h1 {{ color: #28a745; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ تم تحديث المنتج بنجاح!</h1>
                    <p>تم تحديث المنتج "{product.name}" بنجاح.</p>
                    <a href="/admin/products" class="btn">العودة للوحة الإدارة</a>
                    <a href="/view-products" class="btn">عرض المنتجات</a>
                </div>
            </body>
            </html>
            """
            
        except Exception as e:
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>خطأ</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                    h1 {{ color: #dc3545; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>❌ حدث خطأ</h1>
                    <p>حدث خطأ أثناء تحديث المنتج: {str(e)}</p>
                    <a href="/admin/products" class="btn">العودة للوحة الإدارة</a>
                </div>
            </body>
            </html>
            """
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تعديل المنتج</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input, textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
            .file-input {{ border: 2px dashed #007bff; padding: 20px; text-align: center; border-radius: 5px; margin: 10px 0; }}
            .help-text {{ font-size: 12px; color: #666; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>تعديل المنتج</h1>
            <form method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>اسم المنتج:</label>
                    <input type="text" name="name" value="{product.name}" required>
                </div>
                <div class="form-group">
                    <label>الوصف:</label>
                    <textarea name="description" rows="4" required>{product.description}</textarea>
                </div>
                <div class="form-group">
                    <label>السعر:</label>
                    <input type="number" name="price" step="0.01" value="{product.price}" required>
                </div>
                <div class="form-group">
                    <label>الفئة:</label>
                    <input type="text" name="category" value="{product.category or ''}">
                </div>
                <div class="form-group">
                    <label>العلامة التجارية:</label>
                    <input type="text" name="brand" value="{product.brand or ''}">
                </div>
                <div class="form-group">
                    <label>القسم الرئيسي:</label>
                    <input type="text" name="main_category" value="{product.main_category or ''}">
                </div>
                <div class="form-group">
                    <label>صورة المنتج:</label>
                    <div class="file-input">
                        <input type="file" name="product_image" accept="image/*">
                        <div class="help-text">اختر صورة للمنتج (JPG, PNG, GIF, WebP)</div>
                    </div>
                </div>
                <div class="form-group">
                    <label>أو رابط الصورة:</label>
                    <input type="url" name="image_url" value="{product.image_url or ''}" placeholder="https://example.com/image.jpg">
                    <div class="help-text">يمكنك إدخال رابط صورة بدلاً من رفع ملف</div>
                </div>
                <button type="submit">حفظ التغييرات</button>
            </form>
            <p><a href="/admin/products">العودة للوحة الإدارة</a> | <a href="/view-products">عرض المنتجات</a></p>
        </div>
    </body>
    </html>
    """

@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """حذف منتج"""
    try:
        product = Product.query.get_or_404(product_id)
        product.is_active = False  # حذف ناعم
        db.session.commit()
        # لا حاجة لتفريغ الكاش بعد إزالته
        
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تم الحذف</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                h1 {{ color: #28a745; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ تم حذف المنتج بنجاح!</h1>
                <p>تم حذف المنتج "{product.name}" بنجاح.</p>
                <a href="/admin/products" class="btn">العودة للوحة الإدارة</a>
                <a href="/view-products" class="btn">عرض المنتجات</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطأ</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                h1 {{ color: #dc3545; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ حدث خطأ</h1>
                <p>حدث خطأ أثناء حذف المنتج: {str(e)}</p>
                <a href="/admin/products" class="btn">العودة للوحة الإدارة</a>
            </div>
        </body>
        </html>
        """





@app.route('/api/products/create', methods=['POST'])
def create_product_api():
    """API لإنشاء منتج جديد"""
    try:
        data = request.get_json()
        
        # إنشاء المنتج
        product = Product(
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            image_url=data.get('image_url', '')
        )
        
        # تعيين البيانات العربية (بدون ترجمة تلقائية)
        product.name_ar = product.name
        product.description_ar = product.description
        product.category_ar = product.category
        product.brand_ar = product.brand
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إضافة المنتج بنجاح!',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



# --- سلة المشتريات (Cart) ---
def _get_session_cart():
    """إرجاع سلة الجلسة كقاموس {product_id(str): quantity(int)}"""
    cart = session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    return cart


def _save_session_cart(cart_dict):
    """حفظ السلة في الجلسة."""
    session['cart'] = cart_dict
    session.modified = True  # تأكيد تعديل الجلسة
    try:
        session.permanent = True
    except Exception:
        pass


def _cart_total_count(cart_dict):
    try:
        return int(sum(int(q) for q in cart_dict.values()))
    except Exception:
        return 0


@app.route('/api/cart/count', methods=['GET'])
def api_cart_count():
    cart = _get_session_cart()
    return jsonify({'success': True, 'count': _cart_total_count(cart)})


@app.route('/api/cart/items')
def api_cart_items():
    """الحصول على عناصر السلة كـ JSON."""
    try:
        cart = _get_session_cart()
        cart_items = []
        total = 0
        
        for product_id, quantity in cart.items():
            if quantity > 0:
                product = Product.query.get(int(product_id))
                if product and getattr(product, 'is_active', True):
                    item_total = float(product.price) * quantity
                    total += item_total
                    
                    cart_items.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'quantity': quantity,
                        'image': product.image_url or '/static/images/product1.jpg',
                        'total': item_total
                    })
        
        return jsonify({
            'success': True, 
            'items': cart_items, 
            'total': total,
            'count': len(cart_items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/cart/add', methods=['POST'])
def cart_add():
    """إضافة منتج إلى السلة من الواجهة (JSON: product_id, quantity)."""
    try:
        data = request.get_json(silent=True) or {}
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'الكمية غير صالحة'}), 400

        # التحقق من وجود المنتج
        product = Product.query.get(product_id)
        if not product or not getattr(product, 'is_active', True):
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        cart = _get_session_cart()
        key = str(product_id)
        cart[key] = int(cart.get(key, 0)) + quantity
        _save_session_cart(cart)

        return jsonify({'success': True, 'cart_count': _cart_total_count(cart)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/cart', methods=['GET'])
def cart_view():
    """عرض صفحة السلة مع تفاصيل المنتجات والأسعار."""
    cart = _get_session_cart()
    if not cart:
        return render_template('cart.html', cart_items=[], total=0.0, deposit=0.0)

    # بناء قائمة العناصر من قاعدة البيانات
    cart_items = []
    total = 0.0
    for key, qty in cart.items():
        try:
            pid = int(key)
            quantity = int(qty)
        except Exception:
            continue
        if quantity <= 0:
            continue
        product = Product.query.get(pid)
        if not product:
            continue
        price = float(getattr(product, 'price', 0.0) or 0.0)
        name = product.name_ar or product.name or f"منتج #{pid}"
        cart_items.append({
            'product_id': pid,
            'name': name,
            'price': price,
            'quantity': quantity,
        })
        total += price * quantity

    deposit = total * 0.5
    return render_template('cart.html', cart_items=cart_items, total=total, deposit=deposit)


@app.route('/cart/update', methods=['POST'])
def cart_update():
    """تحديث كمية عنصر في السلة (نموذج من صفحة السلة)."""
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity', 1))
        cart = _get_session_cart()
        key = str(product_id)
        if quantity <= 0:
            # إزالة إذا أصبحت الكمية 0 أو أقل
            if key in cart:
                cart.pop(key, None)
        else:
            cart[key] = quantity
        _save_session_cart(cart)
        return redirect(url_for('cart_view'))
    except Exception:
        return redirect(url_for('cart_view'))


@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    """إزالة عنصر من السلة (نموذج من صفحة السلة)."""
    try:
        product_id = int(request.form.get('product_id'))
        cart = _get_session_cart()
        cart.pop(str(product_id), None)
        _save_session_cart(cart)
        return redirect(url_for('cart_view'))
    except Exception:
        return redirect(url_for('cart_view'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout_page():
    """عرض صفحة إتمام الشراء واستلام بيانات العميل وإنشاء الطلب."""
    try:
        print("بدء عملية checkout...")
        
        # بناء ملخص السلة من الجلسة
        cart = _get_session_cart()
        print(f"📦 محتويات السلة: {cart}")
        print(f"📦 نوع السلة: {type(cart)}")
        print(f"📦 طول السلة: {len(cart) if cart else 0}")
        print(f"🔑 session ID: {session.get('_id', 'غير محدد')}")
        print(f"🔑 session keys: {list(session.keys())}")
        print(f"🔑 session cart key: {session.get('cart', 'غير موجود')}")
        print(f"🔑 request method: {request.method}")
        print(f"🔑 request form: {request.form}")
        print(f"🔑 request args: {request.args}")
        print(f"🔑 request data: {request.data}")
        print(f"🔑 request headers: {dict(request.headers)}")
        
        cart_items = []
        total = 0.0
        for key, qty in cart.items():
            try:
                pid = int(key)
                quantity = int(qty)
                print(f"🔍 معالجة منتج ID: {pid}, الكمية: {quantity}")
            except Exception as e:
                print(f"❌ خطأ في معالجة منتج {key}: {e}")
                continue
            if quantity <= 0:
                print(f"كمية غير صحيحة للمنتج {pid}: {quantity}")
                continue
            product = Product.query.get(pid)
            if not product:
                print(f"❌ المنتج {pid} غير موجود في قاعدة البيانات")
                continue
            price = float(getattr(product, 'price', 0.0) or 0.0)
            name = product.name_ar or product.name or f"منتج #{pid}"
            cart_items.append({
                'product_id': pid,
                'name': name,
                'price': price,
                'quantity': quantity,
            })
            total += price * quantity
            print(f"✅ تمت إضافة المنتج: {name} - السعر: {price} - الكمية: {quantity}")
        
        deposit = total * 0.5
        print(f"الإجمالي: {total}, المطلوب الآن: {deposit}")
        print(f"عدد العناصر في السلة: {len(cart_items)}")

        if request.method == 'POST':
            print("📝 معالجة طلب POST...")
            print(f"📦 السلة قبل POST: {cart}")
            print(f"عدد العناصر قبل POST: {len(cart_items)}")
            print(f"الإجمالي قبل POST: {total}")
            
            # استلام بيانات العميل
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            email = request.form.get('email', '').strip()
            payment_method = request.form.get('payment_method', 'bank_transfer')
            
            print(f"👤 بيانات العميل: الاسم={name}, الهاتف={phone}, البريد={email}")
            print(f"📍 العنوان: {address}")
            print(f"💳 طريقة الدفع: {payment_method}")

            if not (name and phone and address and email) or total <= 0:
                print("❌ بيانات ناقصة أو سلة فارغة")
                print(f"🔍 البيانات: name={name}, phone={phone}, address={address}, email={email}, total={total}")
                flash('يرجى تعبئة جميع الحقول والتأكد من أن السلة غير فارغة')
                return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)

            print("✅ البيانات صحيحة، بدء إنشاء الطلبات...")
            
            # إنشاء طلب داخلي لكل عنصر وإرسال إشعار شامل
            created_orders = []
            order_items = []
            
            for item in cart_items:
                print(f"إنشاء طلب للمنتج: {item['name']}")
                product = Product.query.get(item['product_id'])
                if not product:
                    print(f"❌ المنتج {item['product_id']} غير موجود")
                    continue
                
                # إنشاء رقم طلب فريد
                import uuid
                order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                print(f"🔢 رقم الطلب الجديد: {order_number}")
                
                try:
                    # إنشاء الطلب في قاعدة البيانات
                    new_order = Order(
                        order_number=order_number,
                        product_id=item['product_id'],
                        product_name=product.name,
                        quantity=item['quantity'],
                        unit_price=product.price,
                        total_price=product.price * item['quantity'],
                        customer_name=name,
                        customer_email=email,
                        customer_phone=phone,
                        customer_address=address,
                        customer_country='السعودية',  # يمكن تحديثه لاحقاً
                        payment_method=payment_method,
                        status='pending',
                        status_ar='قيد المراجعة'
                    )
                    
                    db.session.add(new_order)
                    db.session.flush()  # للحصول على ID
                    print(f"✅ تم إنشاء الطلب في قاعدة البيانات: {new_order.id}")
                    
                    # إنشاء سجل في تاريخ الحالة
                    status_history = OrderStatusHistory(
                        order_id=new_order.id,
                        old_status=None,
                        new_status='pending',
                        changed_by='system',
                        notes='تم إنشاء الطلب'
                    )
                    db.session.add(status_history)
                    print(f"✅ تم إنشاء سجل تاريخ الحالة")
                    
                    created_orders.append(new_order)
                    order_items.append(new_order.to_dict())
                    print(f"✅ تمت إضافة الطلب إلى القائمة")
                    
                except Exception as e:
                    print(f"❌ خطأ في إنشاء الطلب: {e}")
                    db.session.rollback()
                    continue
            
            try:
                print("💾 حفظ الطلبات في قاعدة البيانات...")
                db.session.commit()
                print(f"✅ تم حفظ {len(created_orders)} طلب بنجاح")
            except Exception as e:
                print(f"❌ خطأ في حفظ قاعدة البيانات: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                flash('حدث خطأ في حفظ الطلب. يرجى المحاولة مرة أخرى.')
                return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)

            # إرسال إشعار شامل للطلب الكامل
            if order_items:
                print("📧 محاولة إرسال إشعار البريد الإلكتروني...")
                try:
                    first_order = created_orders[0]
                    email_subject = f"طلب شامل جديد #{first_order.order_number} - {len(order_items)} منتج"
                    email_body = f"""إشعار طلب شامل جديد من موقع Velio Store

📋 ملخص الطلب:
رقم الطلب: #{first_order.order_number}
عدد المنتجات: {len(order_items)}
المبلغ الإجمالي: {total} $
المبلغ المطلوب الآن (50%): {deposit} $
المبلغ المتبقي عند التسليم: {total - deposit} $
التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
الحالة: {first_order.get_status_display('ar')}

تفاصيل المنتجات:"""
                    
                    for i, order in enumerate(order_items, 1):
                        email_body += f"""
{i}. {order['product_name']}
   - الكمية: {order['quantity']}
   - السعر الإجمالي: {order['total_price']} $"""
                    
                    # إنشاء رابط الخريطة للعنوان
                    import urllib.parse
                    encoded_address = urllib.parse.quote_plus(address)
                    map_link = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
                    
                    email_body += f"""

👤 معلومات العميل:
الاسم: {name}
الهاتف: {phone}
البريد الإلكتروني: {email}
العنوان: {address}
📍 موقع العميل على الخريطة: {map_link}
طريقة الدفع: {payment_method}

للتواصل مع العميل:
- رقم الطلب: #{first_order.order_number}
- البريد الإلكتروني: {email}
- الهاتف: {phone}

---
هذه رسالة تلقائية من نظام إشعارات Velio Store"""
                    
                    # إرسال إشعار للمدير
                    email_sent = send_email(email_subject, email_body)
                    if email_sent:
                        print("✅ تم إرسال البريد الإلكتروني للمدير بنجاح")
                    else:
                        print("⚠️ فشل في إرسال البريد الإلكتروني للمدير - سيتم المتابعة مع الطلب")
                    
                    # إرسال إشعار تأكيد للعميل
                    if email:
                        customer_subject = f"تأكيد استلام طلبك #{first_order.order_number}"
                        customer_body = f"""مرحباً {name},

شكراً لك على طلبك! تم استلام طلبك بنجاح وسنقوم بمراجعته قريباً.

📋 ملخص طلبك:
رقم الطلب: #{first_order.order_number}
عدد المنتجات: {len(order_items)}
المبلغ الإجمالي: {total} $
المبلغ المطلوب الآن (50%): {deposit} $
المبلغ المتبقي عند التسليم: {total - deposit} $
الحالة الحالية: {first_order.get_status_display('ar')}

تفاصيل المنتجات:"""
                        
                        for i, order in enumerate(order_items, 1):
                            customer_body += f"""
{i}. {order['product_name']}
   - الكمية: {order['quantity']}
   - السعر الإجمالي: {order['total_price']} $"""
                        
                        customer_body += f"""

للاستفسارات، يرجى التواصل معنا على:
- البريد الإلكتروني: velio.contact@yahoo.com
- رقم الطلب: #{first_order.order_number}

شكراً لاختيارك متجرنا!

---
Velio Store"""
                        
                        customer_email_sent = send_customer_email(email, customer_subject, customer_body)
                        if customer_email_sent:
                            print("✅ تم إرسال إشعار التأكيد للعميل بنجاح")
                        else:
                            print("⚠️ فشل في إرسال إشعار التأكيد للعميل")
                        
                except Exception as e:
                    print(f"❌ خطأ في إرسال البريد الإلكتروني: {e}")
                    print("⚠️ سيتم المتابعة مع إنشاء الطلب رغم فشل الإرسال")

            # التحقق من وجود طلبات تم إنشاؤها
            if not created_orders:
                print("❌ لم يتم إنشاء أي طلبات")
                flash('حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى.')
                return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)

            # تفريغ السلة بعد الإرسال
            _save_session_cart({})
            print("تم تفريغ السلة")

            # حساب تفاصيل الشكر
            first_order = created_orders[0]
            thank_you_order = {
                'order_id': first_order.order_number,
                'total_price': total,
                'deposit_paid_now': deposit,
                'remaining_on_delivery': total - deposit
            }
            print(f"تم إنشاء الطلب بنجاح: {thank_you_order['order_id']}")

            # إضافة رسالة نجاح
            flash(f'تم إنشاء طلبك بنجاح! رقم الطلب: {thank_you_order["order_id"]}')
            
            print(f"التوجه إلى صفحة الشكر مع البيانات: {thank_you_order}")
            return render_template('thank_you.html', order=thank_you_order)

        # GET: عرض صفحة الدفع مع الملخص
        print(f"📄 عرض صفحة checkout مع {len(cart_items)} منتج")
        return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)
        
    except Exception as e:
        print(f"❌ خطأ عام في checkout: {e}")
        print(f"🔍 نوع الخطأ: {type(e).__name__}")
        print(f"🔍 تفاصيل الخطأ: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'حدث خطأ غير متوقع: {str(e)}. يرجى المحاولة مرة أخرى.')
        return redirect(url_for('cart_view'))


@app.route('/thank-you')
def thank_you_page():
    """عرض صفحة الشكر مباشرة"""
    return render_template('thank_you.html', order=None)


# --- تشغيل السيرفر ---
if __name__ == '__main__':
    import os
    import sys
    
    # تحديد المنفذ من المعاملات أو متغير البيئة
    port = 5001  # المنفذ الافتراضي الجديد
    if len(sys.argv) > 1 and '--port' in sys.argv:
        port_index = sys.argv.index('--port')
        if port_index + 1 < len(sys.argv):
            port = int(sys.argv[port_index + 1])
    else:
        port = int(os.environ.get('PORT', 5001))
    
    print("تم إنشاء قاعدة البيانات بنجاح")
    print("بدء تشغيل سيرفر Flask مع دعم تعدد اللغات...")
    print("تم تفعيل خدمة GPS لتتبع المواقع")
    print("الموقع يدعم اللغتين العربية والإنجليزية")
    print(f"السيرفر سيكون متاحًا على: http://127.0.0.1:{port}")
    print(f"للوصول من الهاتف: http://192.168.0.240:{port}")
    print(f"لوحة إدارة المنتجات: http://127.0.0.1:{port}/admin/products")
    print(f"لوحة إدارة المنتجات (الهاتف): http://192.168.0.240:{port}/admin/products")
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
