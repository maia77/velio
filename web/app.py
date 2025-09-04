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

from models import db, Product, Comment
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

# إعدادات الجلسة
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(basedir, 'instance', 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # ساعة واحدة
app.config['SESSION_FILE_THRESHOLD'] = 500

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
                        print('🆕 تم إضافة العمود main_category')
                    if 'main_category_ar' not in cols:
                        conn.execute(text('ALTER TABLE products ADD COLUMN main_category_ar VARCHAR(100) DEFAULT \'أصالة معاصرة\''))
                        print('🆕 تم إضافة العمود main_category_ar')
                    conn.commit()
                    print('✅ تم التأكد من وجود الأعمدة الجديدة (SQLite)')
        except Exception as e:
            print(f"⚠️ تعذر التحقق/إضافة الأعمدة الجديدة: {e}")
    except Exception as e:
        print(f"❌ فشل إنشاء الجداول: {e}")

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
    print("🔄 إعادة توجيه للعربية")
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
            print(f"✅ تم تفعيل الترجمة التلقائية للغة: {lang_code}")
        else:
            session['auto_translate'] = False
            print("⚠️ خدمة الترجمة غير متاحة")
        
        # إذا تم تغيير اللغة إلى العربية، توجيه إلى الصفحة الرئيسية
        if lang_code == 'ar':
            print("🏠 توجيه إلى الصفحة الرئيسية باللغة العربية")
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
    print("🔄 تم إعادة ضبط اللغة إلى العربية")
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """حفظ الصورة وإرجاع المسار مع تصغير وضغط تلقائي"""
    return save_uploaded_file(file)

@app.route('/test-admin')
def test_admin():
    return "لوحة الإدارة تعمل! 🎉"

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
                'main_category': getattr(product, 'main_category', 'أصالة معاصرة'),
                'main_category_ar': getattr(product, 'main_category_ar', 'أصالة معاصرة'),
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
            
            # معالجة الصورة المرفوعة
            image_url = ''
            if 'product_image' in request.files:
                uploaded_file = request.files['product_image']
                if uploaded_file.filename != '':
                    image_url = save_uploaded_file(uploaded_file)
            
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
                    print(f"⚠️ خطأ في تجهيز الحقول العربية: {e}")
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
                    <label>🏷️ اسم المنتج (باللغة الإنجليزية):</label>
                    <input type="text" name="name" required placeholder="مثال: Modern Chair">
                    <div class="help-text">سيتم ترجمته تلقائياً للعربية</div>
                </div>
                
                <div class="form-group">
                    <label>📝 وصف المنتج:</label>
                    <textarea name="description" rows="4" required placeholder="وصف المنتج باللغة الإنجليزية"></textarea>
                    <div class="help-text">سيتم ترجمته تلقائياً للعربية</div>
                </div>
                
                <div class="form-group">
                    <label>💰 السعر ($):</label>
                    <input type="number" name="price" step="0.01" required placeholder="مثال: 150.00">
                </div>
                
                <div class="form-group">
                    <label>📂 الفئة (اختياري):</label>
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
                    <label>🏢 العلامة التجارية (اختياري):</label>
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
                
                <button type="submit">💾 إضافة المنتج</button>
            </form>
            <a href="/admin" class="btn btn-back">↩️ العودة للوحة الإدارة</a>
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
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', '')  # يجب إضافة البريد الإلكتروني من متغيرات البيئة
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '') # يجب إضافة كلمة مرور التطبيقات من متغيرات البيئة
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL', '') # البريد الذي سيستقبل الإشعارات

def send_email(subject, body):
    """
    دالة لإرسال إشعار عبر البريد الإلكتروني.
    """
    message = f"Subject: {subject}\n\n{body}".encode('utf-8')
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
            print(f"✅ تم إرسال إشعار البريد الإلكتروني بنجاح: {subject}")
    except Exception as e:
        print(f"❌ فشل في إرسال إشعار البريد الإلكتروني: {e}")

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

        # إرسال إشعار
        email_subject = f"رسالة جديدة من {data['name']}"
        email_body = f"من: {data['name']} ({data['email']})\n\nالرسالة:\n{data['message']}"
        
        # إضافة الموقع إذا كان متوفراً
        if 'location' in data and data['location']:
            email_body += f"\n\nالموقع:\n{data['location']}"
        
        send_email(email_subject, email_body)

        return jsonify({'success': True, 'message': 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.'}), 200
        
    except Exception as e:
        print(f"❌ خطأ في معالجة رسالة التواصل: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في الخادم. يرجى المحاولة مرة أخرى.'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """
    ينشئ طلبًا جديدًا لمنتج من قاعدة البيانات، ويتحقق من المخزون، ويقوم بتحديثه.
    """
    try:
        data = request.get_json()
        product_id = int(data['product_id'])
        quantity = int(data['quantity'])

        # البحث عن المنتج في قاعدة البيانات
        with app.app_context():
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        # حفظ الطلب
        new_order = {
            'order_id': len(orders) + 1,
            'product_id': product_id,
            'product_name': product.name,
            'quantity': quantity,
            'total_price': product.price * quantity,
            'order_date': datetime.now().isoformat(),
            'customer_info': data.get('customer_info', {})
        }
        orders.append(new_order)

        # إرسال إشعار بالبريد الإلكتروني
        email_subject = f"طلب جديد - {product.name}"
        email_body = f"""
طلب جديد:

المنتج: {product.name}
الكمية: {quantity}
السعر الإجمالي: {new_order['total_price']} $
رقم الطلب: {new_order['order_id']}
التاريخ: {new_order['order_date']}

معلومات العميل:
{data.get('customer_info', {})}
        """
        send_email(email_subject, email_body)

        return jsonify({
            'success': True,
            'message': 'تم إنشاء طلبك بنجاح! سنتواصل معك قريباً لتأكيد الطلب.',
            'order_id': new_order['order_id']
        }), 201

    except Exception as e:
        print(f"❌ خطأ في إنشاء الطلب: {e}")
        return jsonify({'success': False, 'error': 'حدث خطأ في إنشاء الطلب. يرجى المحاولة مرة أخرى.'}), 500

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
                'image_url': product.image_url
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
    """إضافة تعليق جديد لمنتج"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404

        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        content = (data.get('content') or '').strip()
        rating = data.get('rating')

        if not name or not content:
            return jsonify({'success': False, 'error': 'الاسم والمحتوى مطلوبان'}), 400

        try:
            rating_value = int(rating) if rating is not None else None
            if rating_value is not None and (rating_value < 1 or rating_value > 5):
                return jsonify({'success': False, 'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400
        except Exception:
            rating_value = None

        comment = Comment(product_id=product_id, name=name, content=content, rating=rating_value)
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
                'title': '🏛️ أصالة معاصرة',
                'description': 'جمع بين الأصالة والحداثة في تصميم منزلك',
                'filter': 'أصالة معاصرة'
            },
            'تفاصيل-مميزة': {
                'title': '🎨 تفاصيل مميزة',
                'description': 'اهتم بالتفاصيل الصغيرة التي تحدث فرقاً كبيراً',
                'filter': 'تفاصيل مميزة'
            },
            'لمسات-فريدة': {
                'title': '✨ لمسات فريدة',
                'description': 'قطع مميزة تضيف لمسة خاصة لمنزلك',
                'filter': 'لمسات فريدة'
            },
            'زينة-الطبيعة': {
                'title': '🌿 زينة الطبيعة',
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
                    print(f"⚠️ خطأ في تجهيز الحقول العربية: {e}")
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
            
            return "تم إضافة المنتج بنجاح! 🎉"
            
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
            <h1>✏️ تعديل المنتج</h1>
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
        # بناء ملخص السلة من الجلسة
        cart = _get_session_cart()
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

        if request.method == 'POST':
            # استلام بيانات العميل
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            email = request.form.get('email', '').strip()
            payment_method = request.form.get('payment_method', 'bank_transfer')

            if not (name and phone and address and email) or total <= 0:
                # إعادة العرض مع رسالة بسيطة (يمكن تحسينها لاحقاً)
                flash('يرجى تعبئة جميع الحقول والتأكد من أن السلة غير فارغة')
                return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)

            # إنشاء طلب داخلي لكل عنصر (أبسطياً)، وإرسال بريد إشعار كما هو متاح سابقاً
            created_order = None
            for item in cart_items:
                order_data = {
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'customer_info': {
                        'name': name,
                        'phone': phone,
                        'address': address,
                        'email': email,
                        'payment_method': payment_method,
                    }
                }
                # استدعاء المنطق الداخلي كما في /api/orders
                product = Product.query.get(order_data['product_id'])
                new_order = {
                    'order_id': len(orders) + 1,
                    'product_id': order_data['product_id'],
                    'product_name': product.name if product else f"منتج #{order_data['product_id']}",
                    'quantity': order_data['quantity'],
                    'total_price': (product.price if product else 0.0) * order_data['quantity'],
                    'order_date': datetime.now().isoformat(),
                    'customer_info': order_data['customer_info']
                }
                orders.append(new_order)
                created_order = new_order  # آخر واحد كمرجع

            # تفريغ السلة بعد الإرسال
            _save_session_cart({})

            # حساب تفاصيل الشكر
            thank_you_order = {
                'order_id': created_order['order_id'] if created_order else 0,
                'total_price': total,
                'deposit_paid_now': deposit,
                'remaining_on_delivery': total - deposit
            }

            return render_template('thank_you.html', order=thank_you_order)

        # GET: عرض صفحة الدفع مع الملخص
        return render_template('checkout.html', cart_items=cart_items, total=total, deposit=deposit)
    except Exception:
        return redirect(url_for('cart_view'))


@app.route('/thank-you')
def thank_you_page():
    """عرض صفحة الشكر مباشرة"""
    return render_template('thank_you.html', order=None)


# --- تشغيل السيرفر ---
if __name__ == '__main__':
    print("✅ تم إنشاء قاعدة البيانات بنجاح")
    print("🚀 بدء تشغيل سيرفر Flask مع دعم تعدد اللغات...")
    print("📍 تم تفعيل خدمة GPS لتتبع المواقع")
    print("🌍 الموقع يدعم اللغتين العربية والإنجليزية")
    print("📡 السيرفر سيكون متاحًا على: http://127.0.0.1:5003")
    print("📱 للوصول من الهاتف: http://192.168.0.72:5003")
    print("لوحة إدارة المنتجات: http://127.0.0.1:5003/admin/products")
    print("لوحة إدارة المنتجات (الهاتف): http://192.168.0.72:5003/admin/products")
    app.run(debug=True, host='0.0.0.0', port=5003, use_reloader=False)
