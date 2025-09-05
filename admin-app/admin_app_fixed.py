#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, render_template_string, render_template, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from shared_database_config_fallback import get_database_config

app = Flask(__name__)

# إعداد مفتاح سري للجلسة (مطلوب لنظام السلة)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key-in-production')

# إعدادات الجلسة
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(basedir, 'instance', 'flask_session')
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # ساعة واحدة
app.config['SESSION_FILE_THRESHOLD'] = 500

# إعداد قاعدة البيانات - مع نظام احتياطي
# استخدام قاعدة بيانات مشتركة (PostgreSQL أو SQLite)
db_config, is_postgresql = get_database_config()
app.config.update(db_config)
use_remote = is_postgresql
db = SQLAlchemy(app)

# تهيئة الجلسة
Session(app)

# إنشاء مجلد الجلسة إذا لم يكن موجوداً
os.makedirs(os.path.join(basedir, 'instance', 'flask_session'), exist_ok=True)

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return f"/static/uploads/{unique_filename}"
    return None

# إنشاء الجداول عند التشغيل إذا لم تكن موجودة
with app.app_context():
    try:
        db.create_all()
        print("✅ تم التأكد من إنشاء جداول قاعدة البيانات لتطبيق الإدارة (الإصدار المحسن)")
        
            
    except Exception as e:
        print(f"⚠️ تعذر إنشاء الجداول في تطبيق الإدارة (الإصدار المحسن): {e}")

# نموذج المنتج
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    category_ar = db.Column(db.String(100), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    brand_ar = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # الصورة الرئيسية (للتوافق مع النظام القديم)
    # القسم الرئيسي للمنتج (أصالة معاصرة، تفاصيل مميزة، لمسات فريدة، زينة الطبيعة)
    main_category = db.Column(db.String(100), nullable=True, default='أصالة معاصرة')
    main_category_ar = db.Column(db.String(100), nullable=True, default='أصالة معاصرة')
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    # إظهار المنتج في قسم "كل ما يحتاجه منزلك" و"وصل حديثاً"
    is_home_essentials = db.Column(db.Boolean, default=True)
    is_new_arrival = db.Column(db.Boolean, default=False)
    
    # علاقة مع الصور المتعددة
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')


class ProductImage(db.Model):
    """نموذج صور المنتج"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200), nullable=True)  # نص بديل للصورة
    is_primary = db.Column(db.Boolean, default=False)  # الصورة الرئيسية
    sort_order = db.Column(db.Integer, default=0)  # ترتيب الصورة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """تحويل الصورة إلى قاموس"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'image_url': self.image_url,
            'alt_text': self.alt_text,
            'is_primary': self.is_primary,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ProductImage {self.id} for Product {self.product_id}>'

class Order(db.Model):
    """نموذج الطلبات"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # رقم الطلب
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # معلومات العميل
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_address = db.Column(db.Text, nullable=True)
    customer_country = db.Column(db.String(50), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    
    # حالة الطلب
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, approved, rejected, completed, cancelled
    status_ar = db.Column(db.String(50), nullable=True)  # الترجمة العربية للحالة
    
    # تواريخ مهمة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)  # تاريخ المعالجة
    completed_at = db.Column(db.DateTime, nullable=True)  # تاريخ الإكمال
    
    # ملاحظات إضافية
    rejection_reason = db.Column(db.Text, nullable=True)  # سبب الرفض
    
    # علاقة مع المنتج
    product = db.relationship('Product', backref='orders')
    
    # علاقة مع تاريخ حالة الطلب
    status_history = db.relationship('OrderStatusHistory', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """تحويل الطلب إلى قاموس"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'customer_address': self.customer_address,
            'customer_country': self.customer_country,
            'payment_method': self.payment_method,
            'status': self.status,
            'status_ar': self.status_ar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rejection_reason': self.rejection_reason
        }
    
    def get_status_display(self, language='ar'):
        """الحصول على نص الحالة باللغة المطلوبة"""
        status_map = {
            'ar': {
                'pending': 'قيد المراجعة',
                'processing': 'قيد المعالجة',
                'approved': 'تم الموافقة',
                'rejected': 'تم الرفض',
                'completed': 'مكتمل',
                'cancelled': 'ملغي'
            },
            'en': {
                'pending': 'Pending',
                'processing': 'Processing',
                'approved': 'Approved',
                'rejected': 'Rejected',
                'completed': 'Completed',
                'cancelled': 'Cancelled'
            }
        }
        return status_map.get(language, {}).get(self.status, self.status)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderStatusHistory(db.Model):
    """نموذج تاريخ حالة الطلب"""
    __tablename__ = 'order_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.String(50), nullable=False)  # admin, customer, system
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """تحويل تاريخ الحالة إلى قاموس"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderStatusHistory {self.id} for Order {self.order_id}>'

# التحقق من وجود الحقول الجديدة وإضافتها إذا لزم الأمر (متوافق مع PostgreSQL و SQLite)
def check_and_add_new_fields():
    """فحص وإضافة الحقول الجديدة للمنتجات"""
    try:
        # محاولة الوصول للحقول الجديدة (بعد تعريف النماذج)
        test_product = Product.query.first()
        if test_product:
            # التحقق من وجود الحقول الجديدة
            if not hasattr(test_product, 'main_category'):
                print("🔄 إضافة الحقول الجديدة للقسم الرئيسي...")
                # إضافة الحقول الجديدة (متوافق مع كلا النوعين)
                with db.engine.connect() as conn:
                    if use_remote:
                        # PostgreSQL syntax
                        conn.execute(db.text("ALTER TABLE products ADD COLUMN IF NOT EXISTS main_category VARCHAR(100) DEFAULT 'أصالة معاصرة'"))
                        conn.execute(db.text("ALTER TABLE products ADD COLUMN IF NOT EXISTS main_category_ar VARCHAR(100) DEFAULT 'أصالة معاصرة'"))
                        conn.execute(db.text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_home_essentials BOOLEAN DEFAULT TRUE"))
                        conn.execute(db.text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_new_arrival BOOLEAN DEFAULT FALSE"))
                    else:
                        # SQLite syntax
                        cols = [row[1] for row in conn.execute(db.text('PRAGMA table_info(products)'))]
                        if 'main_category' not in cols:
                            conn.execute(db.text("ALTER TABLE products ADD COLUMN main_category VARCHAR(100) DEFAULT 'أصالة معاصرة'"))
                        if 'main_category_ar' not in cols:
                            conn.execute(db.text("ALTER TABLE products ADD COLUMN main_category_ar VARCHAR(100) DEFAULT 'أصالة معاصرة'"))
                        if 'is_home_essentials' not in cols:
                            conn.execute(db.text("ALTER TABLE products ADD COLUMN is_home_essentials BOOLEAN DEFAULT 1"))
                        if 'is_new_arrival' not in cols:
                            conn.execute(db.text("ALTER TABLE products ADD COLUMN is_new_arrival BOOLEAN DEFAULT 0"))
                    
                    # تحديث المنتجات الموجودة
                    conn.execute(db.text("UPDATE products SET main_category = 'أصالة معاصرة', main_category_ar = 'أصالة معاصرة' WHERE main_category IS NULL"))
                    conn.commit()
                
                print("✅ تم إضافة الحقول الجديدة بنجاح!")
            else:
                print("✅ الحقول الجديدة موجودة بالفعل")
        else:
            print("ℹ️ لا توجد منتجات في قاعدة البيانات لإضافة الحقول الجديدة")
    except Exception as e:
        print(f"⚠️ خطأ في التحقق من الحقول الجديدة: {e}")
        print("ℹ️ سيتم إنشاء الحقول عند إضافة أول منتج")

# تشغيل فحص الحقول الجديدة داخل سياق التطبيق
with app.app_context():
    check_and_add_new_fields()

@app.route('/')
def index():
    """الصفحة الرئيسية لإدارة المنتجات"""
    try:
        products = Product.query.filter_by(is_active=True).all()
        
        products_html = ""
        for product in products:
            # دعم الصور المتعددة
            if hasattr(product, 'images') and product.images:
                # عرض الصور المتعددة
                images_html = ""
                for i, img in enumerate(product.images[:3]):  # أول 3 صور
                    primary_badge = " (رئيسية)" if img.is_primary else ""
                    images_html += f'<img src="{img.image_url}" style="max-width: 80px; max-height: 80px; border-radius: 8px; margin: 2px;" alt="{product.name}{primary_badge}">'
                if len(product.images) > 3:
                    images_html += f'<div style="display: inline-block; width: 80px; height: 80px; background: #f0f0f0; border-radius: 8px; text-align: center; line-height: 80px; font-size: 12px; color: #666;">+{len(product.images) - 3}</div>'
                image_html = f'<div style="display: flex; flex-wrap: wrap; gap: 5px;">{images_html}</div>'
            else:
                # الصورة الواحدة القديمة
                image_html = f'<img src="{product.image_url}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" alt="{product.name}">' if product.image_url else '<p>📦 لا توجد صورة</p>'
            
            products_html += f"""
            <div class="product-card">
                <div style="display: flex; gap: 20px; align-items: start;">
                    <div style="flex-shrink: 0;">
                        {image_html}
                    </div>
                    <div style="flex-grow: 1;">
                        <h3 style="margin: 0 0 10px 0; color: #333;">{product.name}</h3>
                        <p style="margin: 5px 0; color: #666;"><strong>الاسم العربي:</strong> {product.name_ar or 'غير مترجم'}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الوصف:</strong> {product.description[:100]}{'...' if len(product.description) > 100 else ''}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الوصف العربي:</strong> {product.description_ar[:100] if product.description_ar else 'غير مترجم'}{'...' if product.description_ar and len(product.description_ar) > 100 else ''}</p>
                        <p style="margin: 5px 0; color: #28a745; font-weight: bold;"><strong>السعر:</strong> {product.price} $</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الفئة:</strong> {product.category or 'غير محدد'}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>العلامة التجارية:</strong> {product.brand or 'غير محدد'}</p>
                        <p style="margin: 5px 0; color: #667eea; font-weight: bold;"><strong>القسم الرئيسي:</strong> {product.main_category or 'أصالة معاصرة'}</p>
                        
                        <div class="product-actions">
                            <a href="/edit/{product.id}" class="btn btn-edit">✏️ تعديل</a>
                            <form method="POST" action="/delete/{product.id}" style="display: inline;">
                                <button type="submit" class="btn btn-delete" onclick="return confirm('هل أنت متأكد من حذف هذا المنتج؟')">🗑️ حذف</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>إدارة المنتجات - الإصلاح النهائي</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                
                body {{ 
                    font-family: 'Cairo', Arial, sans-serif; 
                    margin: 0; 
                    background: #f5f5f5; 
                    direction: rtl;
                    line-height: 1.6;
                }}
                
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    margin: 20px auto;
                }}
                
                h1 {{ 
                    color: #333; 
                    text-align: center; 
                    margin-bottom: 30px; 
                    font-size: 2.5rem;
                    font-weight: 700;
                }}
                
                .btn {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    margin: 10px; 
                    border: none; 
                    cursor: pointer; 
                    font-weight: 500;
                    transition: all 0.3s ease;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .btn:hover {{ 
                    background: #0056b3; 
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,123,255,0.3);
                }}
                
                .btn-edit {{ 
                    background: #28a745; 
                }}
                
                .btn-edit:hover {{ 
                    background: #218838; 
                    box-shadow: 0 4px 12px rgba(40,167,69,0.3);
                }}
                
                .btn-delete {{ 
                    background: #dc3545; 
                }}
                
                .btn-delete:hover {{ 
                    background: #c82333; 
                    box-shadow: 0 4px 12px rgba(220,53,69,0.3);
                }}
                
                .stats {{ 
                    background: #e9ecef; 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin-bottom: 30px; 
                    text-align: center; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                .product-card {{ 
                    border: 1px solid #ddd; 
                    padding: 25px; 
                    margin: 20px 0; 
                    border-radius: 15px; 
                    background: white; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                }}
                
                .product-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }}
                
                .product-actions {{ 
                    margin-top: 20px; 
                    display: flex; 
                    gap: 15px; 
                    flex-wrap: wrap; 
                }}
                
                .success {{ 
                    color: #28a745; 
                    font-weight: bold; 
                    text-align: center; 
                    margin: 20px 0; 
                    padding: 15px;
                    background: #d4edda;
                    border-radius: 8px;
                    border: 1px solid #c3e6cb;
                }}
                
                /* التصميم المتجاوب */
                @media (max-width: 768px) {{
                    .container {{ 
                        padding: 20px; 
                        margin: 10px;
                        border-radius: 8px;
                    }}
                    
                    h1 {{
                        font-size: 2rem;
                        margin-bottom: 20px;
                    }}
                    
                    .product-card {{
                        padding: 20px;
                        margin: 15px 0;
                    }}
                    
                    .product-card > div {{
                        flex-direction: column !important;
                        gap: 15px;
                    }}
                    
                    .product-actions {{ 
                        flex-direction: column; 
                        gap: 10px;
                    }}
                    
                    .btn {{
                        width: 100%;
                        margin: 5px 0;
                        justify-content: center;
                    }}
                    
                    .stats {{
                        padding: 15px;
                        margin-bottom: 20px;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    .container {{ 
                        padding: 15px; 
                        margin: 5px;
                    }}
                    
                    h1 {{
                        font-size: 1.8rem;
                    }}
                    
                    .product-card {{
                        padding: 15px;
                    }}
                    
                    .btn {{
                        padding: 10px 20px;
                        font-size: 14px;
                    }}
                }}
                
                /* تحسينات إضافية */
                .product-card img {{
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                .product-card h3 {{
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }}
                
                .product-card p {{
                    margin: 8px 0;
                    line-height: 1.5;
                }}
                
                .product-card strong {{
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>إدارة المنتجات - الإصلاح النهائي</h1>
                <div class="success">✅ تم إصلاح مشكلة 404 بنجاح!</div>
                <div class="stats">
                    <p><strong>إجمالي المنتجات:</strong> {len(products)}</p>
                    <p><strong>إجمالي القيمة:</strong> {sum(p.price for p in products):.2f} $</p>
                </div>
                
                <div style="text-align: center; margin-bottom: 20px;">
                    <a href="/add" class="btn">➕ إضافة منتج جديد</a>
                    <a href="/admin/orders" class="btn" style="background: #17a2b8;">📋 إدارة الطلبات</a>
                    <a href="/cart" class="btn" style="background: #28a745;">🛒 عرض السلة (<span id="cart-count">0</span>)</a>
                    <a href="/" class="btn">🔄 تحديث الصفحة</a>
                </div>
                
                <!-- عرض جميع الأقسام -->
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 30px 0; text-align: center;">
                    <h3 style="color: #333; margin-bottom: 20px;">🏪 تصفح المنتجات حسب القسم</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                        <a href="/category/اصالة-معاصرة" class="btn" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 20px;">
                            <span style="font-size: 2rem; margin-bottom: 10px;">🏛️</span>
                            <strong>أصالة معاصرة</strong>
                            <small style="opacity: 0.8; margin-top: 5px;">جمع بين الأصالة والحداثة</small>
                        </a>
                        <a href="/category/تفاصيل-مميزة" class="btn" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 20px;">
                            <span style="font-size: 2rem; margin-bottom: 10px;">🎨</span>
                            <strong>تفاصيل مميزة</strong>
                            <small style="opacity: 0.8; margin-top: 5px;">اهتم بالتفاصيل الصغيرة</small>
                        </a>
                        <a href="/category/لمسات-فريدة" class="btn" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 20px;">
                            <span style="font-size: 2rem; margin-bottom: 10px;">✨</span>
                            <strong>لمسات فريدة</strong>
                            <small style="opacity: 0.8; margin-top: 5px;">قطع مميزة وخاصة</small>
                        </a>
                        <a href="/category/زينة-الطبيعة" class="btn" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 20px;">
                            <span style="font-size: 2rem; margin-bottom: 10px;">🌿</span>
                            <strong>زينة الطبيعة</strong>
                            <small style="opacity: 0.8; margin-top: 5px;">لمسة من الطبيعة</small>
                        </a>
                    </div>
                </div>
                
                {products_html}
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
                <p>خطأ في عرض المنتجات: {str(e)}</p>
                <a href="/" class="btn">العودة للصفحة الرئيسية</a>
            </div>
        </body>
        </html>
        """

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """تعديل منتج"""
    try:
        product = Product.query.get_or_404(product_id)
        
        if request.method == 'POST':
            # تحديث بيانات المنتج
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.price = float(request.form.get('price'))
            product.category = request.form.get('category', '')
            product.brand = request.form.get('brand', '')
            
            # تحديث خيارات العرض
            product.is_home_essentials = request.form.get('is_home_essentials') == 'on'
            product.is_new_arrival = request.form.get('is_new_arrival') == 'on'
            
            # معالجة صورة جديدة إن رُفعت
            if 'product_image' in request.files:
                file = request.files['product_image']
                if file and file.filename:
                    uploaded_url = save_uploaded_file(file)
                    if uploaded_url:
                        product.image_url = uploaded_url
            product.name_ar = product.name
            product.description_ar = product.description
            product.category_ar = product.category
            product.brand_ar = product.brand
            product.updated_at = datetime.now()
            
            db.session.commit()
            
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>تم التعديل</title>
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                
                body {{ 
                    font-family: 'Cairo', Arial, sans-serif; 
                    margin: 0; 
                    background: #f5f5f5; 
                    direction: rtl;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
                    text-align: center; 
                }}
                
                h1 {{ 
                    color: #28a745; 
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                }}
                
                p {{
                    font-size: 1.1rem;
                    color: #666;
                    margin-bottom: 30px;
                }}
                
                .btn {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    margin: 10px; 
                    font-weight: 500;
                    transition: all 0.3s ease;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .btn:hover {{
                    background: #0056b3;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,123,255,0.3);
                }}
                
                /* التصميم المتجاوب */
                @media (max-width: 768px) {{
                    body {{
                        padding: 10px;
                    }}
                    
                    .container {{
                        padding: 25px 20px;
                        margin: 10px;
                        border-radius: 12px;
                    }}
                    
                    h1 {{
                        font-size: 2rem;
                    }}
                    
                    p {{
                        font-size: 1rem;
                    }}
                    
                    .btn {{
                        width: 100%;
                        margin: 10px 0;
                        justify-content: center;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    body {{
                        padding: 5px;
                    }}
                    
                    .container {{
                        padding: 20px 15px;
                        margin: 5px;
                    }}
                    
                    h1 {{
                        font-size: 1.8rem;
                    }}
                    
                    .btn {{
                        padding: 12px 25px;
                        font-size: 14px;
                    }}
                }}
            </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ تم تعديل المنتج بنجاح!</h1>
                    <p>تم تعديل المنتج "{product.name}" بنجاح.</p>
                    <a href="/" class="btn">العودة لإدارة المنتجات</a>
                </div>
            </body>
            </html>
            """
        
        # عرض نموذج التعديل
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تعديل منتج</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                
                body {{ 
                    font-family: 'Cairo', Arial, sans-serif; 
                    margin: 0; 
                    background: #f5f5f5; 
                    direction: rtl;
                    line-height: 1.6;
                    padding: 20px;
                }}
                
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); 
                }}
                
                h1 {{ 
                    color: #333; 
                    text-align: center; 
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 30px;
                }}
                
                .form-group {{ 
                    margin-bottom: 25px; 
                    text-align: right;
                }}
                
                label {{ 
                    display: block; 
                    margin-bottom: 8px; 
                    font-weight: 600; 
                    color: #333;
                    font-size: 1rem;
                }}
                
                input, textarea {{ 
                    width: 100%; 
                    padding: 15px; 
                    border: 2px solid #ddd; 
                    border-radius: 10px; 
                    font-size: 16px;
                    font-family: 'Cairo', sans-serif;
                    transition: all 0.3s ease;
                    background: #f8f9fa;
                }}
                
                input:focus, textarea:focus {{
                    outline: none;
                    border-color: #007bff;
                    background: white;
                    box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
                }}
                
                textarea {{
                    resize: vertical;
                    min-height: 120px;
                }}
                
                button {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 15px 30px; 
                    border: none; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-weight: 600;
                    font-size: 1rem;
                    transition: all 0.3s ease;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 10px 0;
                }}
                
                button:hover {{ 
                    background: #0056b3; 
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,123,255,0.3);
                }}
                
                .btn {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background: #6c757d; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    margin: 10px 0; 
                    font-weight: 500;
                    transition: all 0.3s ease;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .btn:hover {{
                    background: #5a6268;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(108,117,125,0.3);
                }}
                
                .form-actions {{
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    flex-wrap: wrap;
                    margin-top: 30px;
                }}
                
                /* التصميم المتجاوب */
                @media (max-width: 768px) {{
                    body {{
                        padding: 10px;
                    }}
                    
                    .container {{
                        padding: 25px 20px;
                        margin: 10px;
                        border-radius: 12px;
                    }}
                    
                    h1 {{
                        font-size: 2rem;
                        margin-bottom: 25px;
                    }}
                    
                    .form-group {{
                        margin-bottom: 20px;
                    }}
                    
                    input, textarea {{
                        padding: 12px;
                        font-size: 16px; /* لمنع التكبير في iOS */
                    }}
                    
                    .form-actions {{
                        flex-direction: column;
                        gap: 10px;
                    }}
                    
                    button, .btn {{
                        width: 100%;
                        justify-content: center;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    body {{
                        padding: 5px;
                    }}
                    
                    .container {{
                        padding: 20px 15px;
                        margin: 5px;
                    }}
                    
                    h1 {{
                        font-size: 1.8rem;
                    }}
                    
                    input, textarea {{
                        padding: 10px;
                        font-size: 14px;
                    }}
                    
                    button, .btn {{
                        padding: 12px 25px;
                        font-size: 14px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✏️ تعديل منتج</h1>
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
                        <label>صورة المنتج:</label>
                        <input type="file" name="product_image" accept="image/*">
                    </div>
                    
                    <div class="form-group">
                        <label style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" name="is_home_essentials" {'checked' if product.is_home_essentials else ''}>
                            عرض في قسم "كل ما يحتاجه منزلك"
                        </label>
                    </div>
                    
                    <div class="form-group">
                        <label style="display: flex; align-items: center; gap: 10px;">
                            <input type="checkbox" name="is_new_arrival" {'checked' if product.is_new_arrival else ''}>
                            إضافة إلى قسم "وصل حديثاً"
                        </label>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit">تحديث المنتج</button>
                        <a href="/" class="btn">العودة لإدارة المنتجات</a>
                    </div>
                </form>
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
                <p>حدث خطأ أثناء تعديل المنتج: {str(e)}</p>
                <a href="/" class="btn">العودة لإدارة المنتجات</a>
            </div>
        </body>
        </html>
        """

@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """حذف منتج"""
    try:
        product = Product.query.get_or_404(product_id)
        product.is_active = False  # حذف ناعم
        db.session.commit()
        
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
                <a href="/" class="btn">العودة لإدارة المنتجات</a>
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
                <a href="/" class="btn">العودة لإدارة المنتجات</a>
            </div>
        </body>
        </html>
        """

@app.route('/add', methods=['GET', 'POST'])
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
            
            # معالجة خيارات العرض
            is_home_essentials = request.form.get('is_home_essentials') == 'on'
            is_new_arrival = request.form.get('is_new_arrival') == 'on'
            
            # معالجة الصور المتعددة
            image_url = ''  # الصورة الرئيسية للتوافق مع النظام القديم
            uploaded_images = []
            
            # معالجة الصور المتعددة
            if 'product_images' in request.files:
                files = request.files.getlist('product_images')
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
                main_category=main_category,
                main_category_ar=main_category,
                image_url=image_url,
                name_ar=name,
                description_ar=description,
                category_ar=category,
                brand_ar=brand,
                is_home_essentials=is_home_essentials,
                is_new_arrival=is_new_arrival,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(product)
            db.session.flush()  # للحصول على ID المنتج
            
            # إضافة الصور إلى قاعدة البيانات
            for img_data in uploaded_images:
                product_image = ProductImage(
                    product_id=product.id,
                    image_url=img_data['url'],
                    is_primary=img_data['is_primary'],
                    sort_order=img_data['sort_order'],
                    created_at=datetime.now()
                )
                db.session.add(product_image)
            
            db.session.commit()
            
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>تم الإضافة</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
                    h1 {{ color: #28a745; }}
                    .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>✅ تم إضافة المنتج بنجاح!</h1>
                    <p>تم إضافة المنتج "{product.name}" في قسم "{product.main_category}" بنجاح.</p>
                    
                    <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; text-align: right;">
                        <h3 style="margin: 0 0 10px 0; color: #28a745;">تفاصيل العرض:</h3>
                        <p style="margin: 5px 0; color: #666;">
                            {'✅' if product.is_home_essentials else '❌'} عرض في قسم "كل ما يحتاجه منزلك"
                        </p>
                        <p style="margin: 5px 0; color: #666;">
                            {'✅' if product.is_new_arrival else '❌'} إضافة إلى قسم "وصل حديثاً"
                        </p>
                    </div>
                    <a href="/" class="btn">العودة لإدارة المنتجات</a>
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
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .btn { display: inline-block; padding: 12px 24px; background: #6c757d; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }
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
                    <select name="main_category" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <option value="أصالة معاصرة">🏛️ أصالة معاصرة</option>
                        <option value="تفاصيل مميزة">🎨 تفاصيل مميزة</option>
                        <option value="لمسات فريدة">✨ لمسات فريدة</option>
                        <option value="زينة الطبيعة">🌿 زينة الطبيعة</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>صور المنتج:</label>
                    <input type="file" name="product_images" accept="image/*" multiple required>
                    <small style="color: #666; font-size: 0.9em;">يمكنك اختيار عدة صور في المرة الواحدة</small>
                </div>
                
                <!-- خيارات العرض المحسنة -->
                <div class="form-group">
                    <label style="font-weight: 600; color: #2c3e50; margin-bottom: 15px; display: block; font-size: 1.1em;">
                        🎯 خيارات العرض
                    </label>
                    
                    <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; border: 2px solid #e9ecef;">
                        <div class="form-group" style="margin-bottom: 15px;">
                            <label style="display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 12px; border-radius: 8px; transition: all 0.3s ease; background: white; border: 1px solid #dee2e6;">
                                <input type="checkbox" name="is_home_essentials" checked style="width: 18px; height: 18px; accent-color: #28a745; cursor: pointer;">
                                <span style="display: flex; align-items: center; gap: 8px; font-weight: 500; color: #2c3e50;">
                                    <span style="font-size: 1.2em;">🏠</span>
                                    عرض في قسم "كل ما يحتاجه منزلك"
                                </span>
                            </label>
                        </div>
                        
                        <div class="form-group" style="margin-bottom: 0;">
                            <label style="display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 12px; border-radius: 8px; transition: all 0.3s ease; background: white; border: 1px solid #dee2e6;">
                                <input type="checkbox" name="is_new_arrival" style="width: 18px; height: 18px; accent-color: #17a2b8; cursor: pointer;">
                                <span style="display: flex; align-items: center; gap: 8px; font-weight: 500; color: #2c3e50;">
                                    <span style="font-size: 1.2em;">🆕</span>
                                    إضافة إلى قسم "وصل حديثاً"
                                </span>
                            </label>
                        </div>
                    </div>
                </div>
                
                <!-- أزرار الإجراءات المحسنة -->
                <div style="display: flex; gap: 15px; margin-top: 30px; flex-wrap: wrap; justify-content: center;">
                    <button type="submit" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 15px 35px; border: none; border-radius: 10px; font-size: 1.1em; font-weight: 600; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3); display: flex; align-items: center; gap: 10px;">
                        💾 إضافة المنتج
                    </button>
                    <a href="/" style="background: linear-gradient(135deg, #6c757d 0%, #495057 100%); color: white; padding: 15px 35px; border: none; border-radius: 10px; text-decoration: none; font-size: 1.1em; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3); display: flex; align-items: center; gap: 10px;">
                        ↩️ العودة لإدارة المنتجات
                    </a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """

@app.route('/admin/products')
def admin_products():
    """صفحة إدارة المنتجات - مسار بديل"""
    try:
        products = Product.query.filter_by(is_active=True).all()
        
        products_html = ""
        for product in products:
            # دعم الصور المتعددة
            if hasattr(product, 'images') and product.images:
                # عرض الصور المتعددة
                images_html = ""
                for i, img in enumerate(product.images[:3]):  # أول 3 صور
                    primary_badge = " (رئيسية)" if img.is_primary else ""
                    images_html += f'<img src="{img.image_url}" style="max-width: 80px; max-height: 80px; border-radius: 8px; margin: 2px;" alt="{product.name}{primary_badge}">'
                if len(product.images) > 3:
                    images_html += f'<div style="display: inline-block; width: 80px; height: 80px; background: #f0f0f0; border-radius: 8px; text-align: center; line-height: 80px; font-size: 12px; color: #666;">+{len(product.images) - 3}</div>'
                image_html = f'<div style="display: flex; flex-wrap: wrap; gap: 5px;">{images_html}</div>'
            else:
                # الصورة الواحدة القديمة
                image_html = f'<img src="{product.image_url}" style="max-width: 150px; max-height: 150px; border-radius: 8px;" alt="{product.name}">' if product.image_url else '<p>📦 لا توجد صورة</p>'
            
            products_html += f"""
            <div class="product-card">
                <div style="display: flex; gap: 20px; align-items: start;">
                    <div style="flex-shrink: 0;">
                        {image_html}
                    </div>
                    <div style="flex-grow: 1;">
                        <h3 style="margin: 0 0 10px 0; color: #333;">{product.name}</h3>
                        <p style="margin: 5px 0; color: #666;"><strong>الاسم العربي:</strong> {product.name_ar or 'غير مترجم'}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الوصف:</strong> {product.description[:100]}{'...' if len(product.description) > 100 else ''}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الوصف العربي:</strong> {product.description_ar[:100] if product.description_ar else 'غير مترجم'}{'...' if product.description_ar and len(product.description_ar) > 100 else ''}</p>
                        <p style="margin: 5px 0; color: #28a745; font-weight: bold;"><strong>السعر:</strong> {product.price} $</p>
                        <p style="margin: 5px 0; color: #666;"><strong>الفئة:</strong> {product.category or 'غير محدد'}</p>
                        <p style="margin: 5px 0; color: #666;"><strong>العلامة التجارية:</strong> {product.brand or 'غير محدد'}</p>
                        <p style="margin: 5px 0; color: #667eea; font-weight: bold;"><strong>القسم الرئيسي:</strong> {product.main_category or 'أصالة معاصرة'}</p>
                        
                        <div class="product-actions">
                            <a href="/edit/{product.id}" class="btn btn-edit">✏️ تعديل</a>
                            <form method="POST" action="/delete/{product.id}" style="display: inline;">
                                <button type="submit" class="btn btn-delete" onclick="return confirm('هل أنت متأكد من حذف هذا المنتج؟')">🗑️ حذف</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>إدارة المنتجات - نظام التصنيف الجديد</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}
                
                body {{ 
                    font-family: 'Cairo', Arial, sans-serif; 
                    margin: 0; 
                    background: #f5f5f5; 
                    direction: rtl;
                    line-height: 1.6;
                }}
                
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    margin: 20px auto;
                }}
                
                h1 {{ 
                    color: #333; 
                    text-align: center; 
                    margin-bottom: 30px; 
                    font-size: 2.5rem;
                    font-weight: 700;
                }}
                
                .btn {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background: #007bff; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    margin: 10px; 
                    border: none; 
                    cursor: pointer; 
                    font-weight: 500;
                    transition: all 0.3s ease;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .btn:hover {{ 
                    background: #0056b3; 
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,123,255,0.3);
                }}
                
                .btn-edit {{ 
                    background: #28a745; 
                }}
                
                .btn-edit:hover {{ 
                    background: #218838; 
                    box-shadow: 0 4px 12px rgba(40,167,69,0.3);
                }}
                
                .btn-delete {{ 
                    background: #dc3545; 
                }}
                
                .btn-delete:hover {{ 
                    background: #c82333; 
                    box-shadow: 0 4px 12px rgba(220,53,69,0.3);
                }}
                
                .stats {{ 
                    background: #e9ecef; 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin-bottom: 30px; 
                    text-align: center; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                .product-card {{ 
                    border: 1px solid #ddd; 
                    padding: 25px; 
                    margin: 20px 0; 
                    border-radius: 15px; 
                    background: white; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                }}
                
                .product-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                }}
                
                .product-actions {{ 
                    margin-top: 20px; 
                    display: flex; 
                    gap: 15px; 
                    flex-wrap: wrap; 
                }}
                
                .success {{ 
                    color: #28a745; 
                    font-weight: bold; 
                    text-align: center; 
                    margin: 20px 0; 
                    padding: 15px;
                    background: #d4edda;
                    border-radius: 8px;
                    border: 1px solid #c3e6cb;
                }}
                
                /* التصميم المتجاوب */
                @media (max-width: 768px) {{
                    .container {{ 
                        padding: 20px; 
                        margin: 10px;
                        border-radius: 8px;
                    }}
                    
                    h1 {{
                        font-size: 2rem;
                        margin-bottom: 20px;
                    }}
                    
                    .product-card {{
                        padding: 20px;
                        margin: 15px 0;
                    }}
                    
                    .product-card > div {{
                        flex-direction: column !important;
                        gap: 15px;
                    }}
                    
                    .product-actions {{ 
                        flex-direction: column; 
                        gap: 10px;
                    }}
                    
                    .btn {{
                        width: 100%;
                        margin: 5px 0;
                        justify-content: center;
                    }}
                    
                    .stats {{
                        padding: 15px;
                        margin-bottom: 20px;
                    }}
                }}
                
                @media (max-width: 480px) {{
                    .container {{ 
                        padding: 15px; 
                        margin: 5px;
                    }}
                    
                    h1 {{
                        font-size: 1.8rem;
                    }}
                    
                    .product-card {{
                        padding: 15px;
                    }}
                    
                    .btn {{
                        padding: 10px 20px;
                        font-size: 14px;
                    }}
                }}
                
                /* تحسينات إضافية */
                .product-card img {{
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                .product-card h3 {{
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.3rem;
                }}
                
                .product-card p {{
                    margin: 8px 0;
                    line-height: 1.5;
                }}
                
                .product-card strong {{
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏷️ إدارة المنتجات - نظام التصنيف الجديد</h1>
                
                <div class="stats">
                    <h3>📊 إحصائيات المنتجات</h3>
                    <p><strong>إجمالي المنتجات:</strong> {len(products)}</p>
                    <p><strong>إجمالي القيمة:</strong> {sum(p.price for p in products):.2f} $</p>
                    <p><strong>الأقسام المتاحة:</strong> أصالة معاصرة، تفاصيل مميزة، لمسات فريدة، زينة الطبيعة</p>
                </div>
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <a href="/add" class="btn">➕ إضافة منتج جديد</a>
                    <a href="/" class="btn">🏠 الصفحة الرئيسية</a>
                    <a href="/category/اصالة-معاصرة" class="btn">🏛️ أصالة معاصرة</a>
                    <a href="/category/تفاصيل-مميزة" class="btn">🎨 تفاصيل مميزة</a>
                    <a href="/category/لمسات-فريدة" class="btn">✨ لمسات فريدة</a>
                    <a href="/category/زينة-الطبيعة" class="btn">🌿 زينة الطبيعة</a>
                </div>
                
                {products_html}
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"خطأ في عرض المنتجات: {str(e)}", 500

@app.route('/category/<category_name>')
def category_products(category_name):
    """عرض المنتجات حسب القسم المحدد بنفس تصميم الصفحة الرئيسية"""
    try:
        # تحديد معلومات القسم
        category_info = {
            'اصالة-معاصرة': {
                'title': '🏛️ أصالة معاصرة',
                'title_ar': 'أصالة معاصرة',
                'description': 'جمع بين الأصالة والحداثة في تصميم منزلك',
                'filter': 'أصالة معاصرة',
                'icon': '🏛️'
            },
            'تفاصيل-مميزة': {
                'title': '🎨 تفاصيل مميزة',
                'title_ar': 'تفاصيل مميزة',
                'description': 'اهتم بالتفاصيل الصغيرة التي تحدث فرقاً كبيراً',
                'filter': 'تفاصيل مميزة',
                'icon': '🎨'
            },
            'لمسات-فريدة': {
                'title': '✨ لمسات فريدة',
                'title_ar': 'لمسات فريدة',
                'description': 'قطع مميزة تضيف لمسة خاصة لمنزلك',
                'filter': 'لمسات فريدة',
                'icon': '✨'
            },
            'زينة-الطبيعة': {
                'title': '🌿 زينة الطبيعة',
                'title_ar': 'زينة الطبيعة',
                'description': 'أضف لمسة من الطبيعة إلى منزلك مع مجموعتنا المميزة',
                'filter': 'زينة الطبيعة',
                'icon': '🌿'
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
        
        # إذا لم يتم العثور على منتجات، جرب البحث في حقل category العادي
        if not products:
            products = Product.query.filter(
                Product.is_active == True,
                (Product.category == info['filter']) | (Product.category_ar == info['filter'])
            ).all()
        
        # إذا لم يتم العثور على منتجات، اعرض رسالة
        if not products:
            return f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>{info['title']} - فيليو</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                    .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                    .header {{ text-align: center; color: white; margin-bottom: 40px; }}
                    .header h1 {{ font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
                    .header p {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 20px; }}
                    .stats {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 40px; color: white; border: 1px solid rgba(255,255,255,0.2); }}
                    .stats h3 {{ font-size: 1.5rem; margin-bottom: 15px; }}
                    .stats p {{ font-size: 1.1rem; margin: 5px 0; }}
                    .breadcrumb {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.2); }}
                    .breadcrumb a {{ color: white; text-decoration: none; margin: 0 10px; transition: all 0.3s ease; }}
                    .breadcrumb a:hover {{ color: #ffd700; }}
                    .breadcrumb span {{ color: #ffd700; font-weight: bold; }}
                    .actions {{ text-align: center; margin-bottom: 40px; }}
                    .btn {{ display: inline-block; padding: 15px 30px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 25px; margin: 10px; border: none; cursor: pointer; font-size: 1.1rem; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
                    .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }}
                    .btn-outline {{ background: transparent; border: 2px solid white; color: white; }}
                    .btn-outline:hover {{ background: white; color: #667eea; }}
                    .btn-cart {{ background: linear-gradient(45deg, #28a745, #20c997); }}
                    .btn-edit {{ background: linear-gradient(45deg, #ffc107, #fd7e14); }}
                    .products-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 40px; }}
                    .product-card {{ background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.1); transition: all 0.3s ease; }}
                    .product-card:hover {{ transform: translateY(-10px); box-shadow: 0 25px 50px rgba(0,0,0,0.2); }}
                    .product-image {{ width: 100%; height: 250px; object-fit: cover; }}
                    .product-info {{ padding: 25px; }}
                    .product-name {{ color: #333; font-size: 1.3rem; margin-bottom: 10px; font-weight: bold; }}
                    .product-name-ar {{ color: #666; font-size: 1.1rem; margin-bottom: 15px; font-style: italic; }}
                    .product-description {{ color: #666; margin-bottom: 20px; line-height: 1.6; }}
                    .product-price {{ color: #28a745; font-weight: bold; font-size: 1.4rem; margin-bottom: 20px; }}
                    .product-actions {{ display: flex; gap: 10px; }}
                    .product-actions .btn {{ flex: 1; padding: 12px; font-size: 0.9rem; }}
                    .notification {{ position: fixed; top: 20px; right: 20px; padding: 15px 25px; border-radius: 10px; color: white; font-weight: bold; z-index: 1000; display: none; transform: translateX(100%); transition: all 0.3s ease; }}
                    .notification.show {{ transform: translateX(0); }}
                    .success {{ background: linear-gradient(45deg, #28a745, #20c997); }}
                    .error {{ background: linear-gradient(45deg, #dc3545, #c82333); }}
                    .back-btn {{ position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 15px; border-radius: 50%; text-decoration: none; transition: all 0.3s ease; }}
                    .back-btn:hover {{ background: rgba(255,255,255,0.3); transform: scale(1.1); }}
                    @media (max-width: 768px) {{
                        .container {{ padding: 15px; }}
                        .header h1 {{ font-size: 2rem; }}
                        .products-grid {{ grid-template-columns: 1fr; gap: 20px; }}
                        .product-actions {{ flex-direction: column; }}
                    }}
                </style>
            </head>
            <body>
                <a href="/" class="back-btn" title="العودة للصفحة الرئيسية">
                    <i class="fas fa-arrow-left"></i>
                </a>
                
                <div class="container">
                    <div class="header">
                        <h1>{info['icon']} {info['title']}</h1>
                        <p>{info['description']}</p>
                    </div>
                    
                    <div class="breadcrumb">
                        <a href="/">🏠 الصفحة الرئيسية</a> › 
                        <a href="/admin/products">إدارة المنتجات</a> › 
                        <span>{info['title_ar']}</span>
                    </div>
                    
                    <div class="stats">
                        <h3>📊 إحصائيات القسم</h3>
                        <p><strong>عدد المنتجات:</strong> {len(products) if products else 0}</p>
                        <p><strong>إجمالي القيمة:</strong> {sum([p.price for p in products]) if products else 0:.2f} $</p>
                    </div>
                    
                    <div class="actions">
                        <a href="/add" class="btn">➕ إضافة منتج جديد</a>
                        <a href="/cart" class="btn btn-cart">🛒 عرض السلة</a>
                        <a href="/admin/products" class="btn">📋 جميع المنتجات</a>
                    </div>
                    
                    <div class="products-grid">
                        {''.join([f'''
                        <div class="product-card">
                            <img src="{product.image_url or '/static/images/product1.jpg'}" alt="{product.name}" class="product-image" onerror="this.src='/static/images/product1.jpg'">
                            <div class="product-info">
                                <h3 class="product-name">{product.name}</h3>
                                <p class="product-name-ar">{product.name_ar or 'لا يوجد اسم عربي'}</p>
                                <p class="product-description">{product.description[:100] if product.description else ''}{'...' if product.description and len(product.description) > 100 else ''}</p>
                                <div class="product-price">السعر: {product.price} $</div>
                                <div class="product-actions">
                                    <a href="/edit/{product.id}" class="btn btn-edit">✏️ تعديل</a>
                                    <button onclick="addToCart({product.id})" class="btn btn-cart">🛒 أضف للسلة</button>
                                </div>
                            </div>
                        </div>
                        ''' for product in products])}
                    </div>
                </div>
                
                <!-- إشعارات -->
                <div id="notification" class="notification"></div>
                
                <script>
                    // إضافة للسلة
                    async function addToCart(productId) {{
                        try {{
                            const response = await fetch('/cart/add', {{
                                method: 'POST',
                                headers: {{
                                    'Content-Type': 'application/json',
                                }},
                                body: JSON.stringify({{
                                    product_id: productId,
                                    quantity: 1
                                }})
                            }});
                            
                            const data = await response.json();
                            
                            if (data.success) {{
                                showNotification('تم إضافة المنتج إلى السلة بنجاح! 🛒', 'success');
                                // تحديث عداد السلة إذا كان موجوداً
                                updateCartCount(data.cart_count);
                            }} else {{
                                showNotification('فشل في إضافة المنتج إلى السلة', 'error');
                            }}
                        }} catch (error) {{
                            console.error('خطأ في إضافة المنتج:', error);
                            showNotification('خطأ في الاتصال بالخادم', 'error');
                        }}
                    }}
                    
                    // تحديث عداد السلة
                    function updateCartCount(count) {{
                        // يمكن إضافة منطق تحديث عداد السلة هنا
                        console.log('عدد العناصر في السلة:', count);
                    }}
                    
                    function showNotification(message, type) {{
                        const notification = document.getElementById('notification');
                        notification.textContent = message;
                        notification.className = `notification ${{type}}`;
                        notification.style.display = 'block';
                        
                        // إظهار الإشعار
                        setTimeout(() => {{
                            notification.classList.add('show');
                        }}, 100);
                        
                        // إخفاء الإشعار بعد 3 ثواني
                        setTimeout(() => {{
                            notification.classList.remove('show');
                            setTimeout(() => {{
                                notification.style.display = 'none';
                            }}, 300);
                        }}, 3000);
                    }}
                    
                    // إضافة تأثيرات تفاعلية لبطاقات المنتجات
                    document.addEventListener('DOMContentLoaded', function() {{
                        const productCards = document.querySelectorAll('.product-card');
                        
                        productCards.forEach(card => {{
                            // تأثير عند مرور الفأرة
                            card.addEventListener('mouseenter', function() {{
                                this.style.transform = 'translateY(-10px)';
                            }});
                            
                            // تأثير عند إبعاد الفأرة
                            card.addEventListener('mouseleave', function() {{
                                this.style.transform = 'translateY(0)';
                            }});
                            
                            // تأثير عند النقر
                            card.addEventListener('click', function(e) {{
                                if (!e.target.closest('button') && !e.target.closest('a')) {{
                                    this.style.transform = 'scale(0.98)';
                                    setTimeout(() => {{
                                        this.style.transform = 'scale(1)';
                                    }}, 150);
                                }}
                            }});
                        }});
                    }});
                </script>
            </body>
            </html>
            """
        
        # إرجاع الصفحة مع المنتجات
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>{info['title']} - فيليو</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; color: white; margin-bottom: 40px; }}
                .header h1 {{ font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
                .header p {{ font-size: 1.2rem; opacity: 0.9; margin-bottom: 20px; }}
                .stats {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; text-align: center; margin-bottom: 40px; color: white; border: 1px solid rgba(255,255,255,0.2); }}
                .stats h3 {{ font-size: 1.5rem; margin-bottom: 15px; }}
                .stats p {{ font-size: 1.1rem; margin: 5px 0; }}
                .breadcrumb {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.2); }}
                .breadcrumb a {{ color: white; text-decoration: none; margin: 0 10px; transition: all 0.3s ease; }}
                .breadcrumb a:hover {{ color: #ffd700; }}
                .breadcrumb span {{ color: #ffd700; font-weight: bold; }}
                .actions {{ text-align: center; margin-bottom: 40px; }}
                .btn {{ display: inline-block; padding: 15px 30px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 25px; margin: 10px; border: none; cursor: pointer; font-size: 1.1rem; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
                .btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }}
                .btn-outline {{ background: transparent; border: 2px solid white; color: white; }}
                .btn-outline:hover {{ background: white; color: #667eea; }}
                .btn-cart {{ background: linear-gradient(45deg, #28a745, #20c997); }}
                .btn-edit {{ background: linear-gradient(45deg, #ffc107, #fd7e14); }}
                .products-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 40px; }}
                .product-card {{ background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.1); transition: all 0.3s ease; }}
                .product-card:hover {{ transform: translateY(-10px); box-shadow: 0 25px 50px rgba(0,0,0,0.2); }}
                .product-image {{ width: 100%; height: 250px; object-fit: cover; }}
                .product-info {{ padding: 25px; }}
                .product-name {{ color: #333; font-size: 1.3rem; margin-bottom: 10px; font-weight: bold; }}
                .product-name-ar {{ color: #666; font-size: 1.1rem; margin-bottom: 15px; font-style: italic; }}
                .product-description {{ color: #666; margin-bottom: 20px; line-height: 1.6; }}
                .product-price {{ color: #28a745; font-weight: bold; font-size: 1.4rem; margin-bottom: 20px; }}
                .product-actions {{ display: flex; gap: 10px; }}
                .product-actions .btn {{ flex: 1; padding: 12px; font-size: 0.9rem; }}
                .notification {{ position: fixed; top: 20px; right: 20px; padding: 15px 25px; border-radius: 10px; color: white; font-weight: bold; z-index: 1000; display: none; transform: translateX(100%); transition: all 0.3s ease; }}
                .notification.show {{ transform: translateX(0); }}
                .success {{ background: linear-gradient(45deg, #28a745, #20c997); }}
                .error {{ background: linear-gradient(45deg, #dc3545, #c82333); }}
                .back-btn {{ position: fixed; top: 20px; left: 20px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 15px; border-radius: 50%; text-decoration: none; transition: all 0.3s ease; }}
                .back-btn:hover {{ background: rgba(255,255,255,0.3); transform: scale(1.1); }}
                @media (max-width: 768px) {{
                    .container {{ padding: 15px; }}
                    .header h1 {{ font-size: 2rem; }}
                    .products-grid {{ grid-template-columns: 1fr; gap: 20px; }}
                    .product-actions {{ flex-direction: column; }}
                }}
            </style>
        </head>
        <body>
            <a href="/" class="back-btn" title="العودة للصفحة الرئيسية">
                <i class="fas fa-arrow-left"></i>
            </a>
            
            <div class="container">
                <div class="header">
                    <h1>{info['icon']} {info['title']}</h1>
                    <p>{info['description']}</p>
                </div>
                
                <div class="breadcrumb">
                    <a href="/">🏠 الصفحة الرئيسية</a> › 
                    <a href="/admin/products">إدارة المنتجات</a> › 
                    <span>{info['title_ar']}</span>
                </div>
                
                <div class="stats">
                    <h3>📊 إحصائيات القسم</h3>
                    <p><strong>عدد المنتجات:</strong> {len(products) if products else 0}</p>
                    <p><strong>إجمالي القيمة:</strong> {sum([p.price for p in products]) if products else 0:.2f} $</p>
                </div>
                
                <div class="actions">
                    <a href="/add" class="btn">➕ إضافة منتج جديد</a>
                    <a href="/cart" class="btn btn-cart">🛒 عرض السلة</a>
                    <a href="/admin/products" class="btn">📋 جميع المنتجات</a>
                </div>
                
                <div class="products-grid">
                    {''.join([f'''
                    <div class="product-card">
                        <img src="{product.image_url or '/static/images/product1.jpg'}" alt="{product.name}" class="product-image" onerror="this.src='/static/images/product1.jpg'">
                        <div class="product-info">
                            <h3 class="product-name">{product.name}</h3>
                            <p class="product-name-ar">{product.name_ar or 'لا يوجد اسم عربي'}</p>
                            <p class="product-description">{product.description[:100] if product.description else ''}{'...' if product.description and len(product.description) > 100 else ''}</p>
                            <div class="product-price">السعر: {product.price} $</div>
                            <div class="product-actions">
                                <a href="/edit/{product.id}" class="btn btn-edit">✏️ تعديل</a>
                                <button onclick="addToCart({product.id})" class="btn btn-cart">🛒 أضف للسلة</button>
                            </div>
                        </div>
                    </div>
                    ''' for product in products]) if products else '<p style="text-align: center; color: white; font-size: 1.2rem;">لا توجد منتجات في هذا القسم</p>'}
                </div>
            </div>
            
            <!-- إشعارات -->
            <div id="notification" class="notification"></div>
            
            <script>
                // إضافة للسلة
                async function addToCart(productId) {{
                    try {{
                        const response = await fetch('/cart/add', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                product_id: productId,
                                quantity: 1
                            }})
                        }});
                        
                        const data = await response.json();
                        
                        if (data.success) {{
                            showNotification('تم إضافة المنتج إلى السلة بنجاح! 🛒', 'success');
                            // تحديث عداد السلة إذا كان موجوداً
                            updateCartCount(data.cart_count);
                        }} else {{
                            showNotification('فشل في إضافة المنتج إلى السلة', 'error');
                        }}
                    }} catch (error) {{
                        console.error('خطأ في إضافة المنتج:', error);
                        showNotification('خطأ في الاتصال بالخادم', 'error');
                    }}
                }}
                
                // تحديث عداد السلة
                function updateCartCount(count) {{
                    // يمكن إضافة منطق تحديث عداد السلة هنا
                    console.log('عدد العناصر في السلة:', count);
                }}
                
                function showNotification(message, type) {{
                    const notification = document.getElementById('notification');
                    notification.textContent = message;
                    notification.className = `notification ${{type}}`;
                    notification.style.display = 'block';
                    
                    // إظهار الإشعار
                    setTimeout(() => {{
                        notification.classList.add('show');
                    }}, 100);
                    
                    // إخفاء الإشعار بعد 3 ثواني
                    setTimeout(() => {{
                        notification.classList.remove('show');
                        setTimeout(() => {{
                            notification.style.display = 'none';
                        }}, 300);
                    }}, 3000);
                }}
                
                // إضافة تأثيرات تفاعلية لبطاقات المنتجات
                document.addEventListener('DOMContentLoaded', function() {{
                    const productCards = document.querySelectorAll('.product-card');
                    
                    productCards.forEach(card => {{
                        // تأثير عند مرور الفأرة
                        card.addEventListener('mouseenter', function() {{
                            this.style.transform = 'translateY(-10px)';
                        }});
                        
                        // تأثير عند إبعاد الفأرة
                        card.addEventListener('mouseleave', function() {{
                            this.style.transform = 'translateY(0)';
                        }});
                        
                        // تأثير عند النقر
                        card.addEventListener('click', function(e) {{
                            if (!e.target.closest('button') && !e.target.closest('a')) {{
                                this.style.transform = 'scale(0.98)';
                                setTimeout(() => {{
                                    this.style.transform = 'scale(1)';
                                }}, 150);
                            }}
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
                             
    except Exception as e:
        return f"خطأ في عرض منتجات القسم {category_name}: {str(e)}", 500

@app.route('/api/test-categories')
def test_categories():
    """اختبار الأقسام والمنتجات"""
    try:
        # جلب جميع المنتجات
        all_products = Product.query.all()
        
        print(f"🔍 إجمالي المنتجات في قاعدة البيانات: {len(all_products)}")
        
        # تجميع المنتجات حسب القسم
        categories_data = {}
        for product in all_products:
            main_cat = product.main_category or 'غير محدد'
            if main_cat not in categories_data:
                categories_data[main_cat] = []
            categories_data[main_cat].append({
                'id': product.id,
                'name': product.name,
                'name_ar': product.name_ar,
                'main_category': product.main_category,
                'main_category_ar': product.main_category_ar
            })
        
        print(f"📁 الأقسام الموجودة: {list(categories_data.keys())}")
        
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>اختبار الأقسام</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .category {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .product {{ background: white; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 اختبار الأقسام والمنتجات</h1>
                <p>إجمالي المنتجات: {len(all_products)}</p>
                
                {''.join([f'''
                <div class="category">
                    <h3>📁 {category}</h3>
                    <p>عدد المنتجات: {len(products)}</p>
                    {''.join([f'''
                    <div class="product">
                        <strong>ID:</strong> {p['id']} | 
                        <strong>الاسم:</strong> {p['name']} | 
                        <strong>الاسم العربي:</strong> {p['name_ar']} | 
                        <strong>القسم الرئيسي:</strong> {p['main_category']} | 
                        <strong>القسم العربي:</strong> {p['main_category_ar']}
                    </div>
                    ''' for p in products])}
                </div>
                ''' for category, products in categories_data.items()])}
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/" style="padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">🏠 العودة للرئيسية</a>
                </div>
            </div>
            
            <!-- إشعارات -->
            <div id="notification" class="notification"></div>
            
            <script>
                // تحديث عداد السلة عند تحميل الصفحة
                document.addEventListener('DOMContentLoaded', function() {{
                    updateCartCount();
                }});
                
                // تحديث عداد السلة
                async function updateCartCount() {{
                    try {{
                        const response = await fetch('/api/cart/count');
                        const data = await response.json();
                        if (data.success) {{
                            document.getElementById('cart-count').textContent = data.count;
                        }}
                    }} catch (error) {{
                        console.error('خطأ في تحديث عداد السلة:', error);
                    }}
                }}
                
                // إضافة للسلة
                async function addToCart(productId) {{
                    try {{
                        const response = await fetch('/cart/add', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                product_id: productId,
                                quantity: 1
                            }})
                        }});
                        
                        const data = await response.json();
                        
                        if (data.success) {{
                            showNotification('تم إضافة المنتج إلى السلة بنجاح! 🛒', 'success');
                            updateCartCount();
                        }} else {{
                            showNotification('فشل في إضافة المنتج إلى السلة', 'error');
                        }}
                    }} catch (error) {{
                        console.error('خطأ في إضافة المنتج:', error);
                        showNotification('خطأ في الاتصال بالخادم', 'error');
                    }}
                }}
                
                function showNotification(message, type) {{
                    const notification = document.getElementById('notification');
                    notification.textContent = message;
                    notification.className = `notification ${{type}}`;
                    notification.style.display = 'block';
                    
                    setTimeout(() => {{
                        notification.style.display = 'none';
                    }}, 3000);
                }}
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"خطأ في اختبار الأقسام: {str(e)}", 500

# --- سلة المشتريات (Cart) ---
def _get_session_cart():
    """الحصول على محتويات السلة من الجلسة"""
    cart = session.get('cart')
    print(f"🔍 جلب السلة من الجلسة: {cart}")
    if not isinstance(cart, dict):
        cart = {}
    return cart

def _save_session_cart(cart_dict):
    """حفظ محتويات السلة في الجلسة"""
    print(f"💾 حفظ السلة في الجلسة: {cart_dict}")
    session['cart'] = cart_dict
    session.modified = True  # تأكيد تعديل الجلسة
    try:
        session.permanent = True
    except Exception:
        pass
    print(f"✅ تم حفظ السلة. الجلسة الآن: {dict(session)}")

def _cart_total_count(cart_dict):
    """حساب إجمالي عدد العناصر في السلة"""
    return int(sum(int(q) for q in cart_dict.values()))

@app.route('/api/cart/count', methods=['GET'])
def api_cart_count():
    """API للحصول على عدد العناصر في السلة"""
    cart = _get_session_cart()
    return jsonify({'success': True, 'count': _cart_total_count(cart)})

@app.route('/cart/add', methods=['POST'])
def cart_add():
    """إضافة منتج إلى السلة"""
    try:
        from flask import jsonify, request
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'بيانات غير صحيحة'}), 400
        
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        print(f"🔍 محاولة إضافة منتج: ID={product_id}, الكمية={quantity}")
        
        if not product_id or quantity <= 0:
            return jsonify({'success': False, 'error': 'معرف المنتج أو الكمية غير صحيحة'}), 400
        
        # التحقق من وجود المنتج
        product = Product.query.get(int(product_id))
        if not product:
            print(f"❌ المنتج غير موجود: ID={product_id}")
            return jsonify({'success': False, 'error': 'المنتج غير موجود'}), 404
        
        print(f"✅ تم العثور على المنتج: {product.name}")
        
        # إضافة المنتج إلى السلة
        cart = _get_session_cart()
        key = f"{product_id}"
        cart[key] = int(cart.get(key, 0)) + quantity
        _save_session_cart(cart)
        
        print(f"🛒 تم إضافة المنتج إلى السلة. محتويات السلة: {cart}")
        
        return jsonify({'success': True, 'cart_count': _cart_total_count(cart)})
        
    except Exception as e:
        print(f"❌ خطأ في إضافة المنتج إلى السلة: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/cart', methods=['GET'])
def cart_view():
    """عرض محتويات السلة"""
    try:
        from flask import render_template_string
        print(f"🔍 بدء عرض السلة. معرف الجلسة: {session.get('_id', 'غير موجود')}")
        cart = _get_session_cart()
        
        print(f"🛒 عرض السلة. محتويات السلة: {cart}")
        print(f"🔍 نوع البيانات: {type(cart)}, فارغة: {not cart}")
        
        if not cart:
            print("📭 السلة فارغة")
            return render_template_string("""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>السلة فارغة</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
                    .empty-cart { font-size: 48px; margin: 20px 0; }
                    .btn { padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div style="text-align: left; margin-bottom: 20px;">
                        <a href="/" class="btn" style="background: #6c757d; text-decoration: none; display: inline-block;">← العودة للرئيسية</a>
                    </div>
                    <div class="empty-cart">🛒</div>
                    <h1>السلة فارغة</h1>
                    <p>لم تقم بإضافة أي منتجات إلى السلة بعد.</p>
                    <a href="/" class="btn">🏠 العودة للرئيسية</a>
                </div>
            </body>
            </html>
            """)
        
        # جلب تفاصيل المنتجات في السلة
        cart_items = []
        total = 0.0
        
        print(f"🔍 جلب تفاصيل المنتجات من السلة...")
        
        for key, qty in cart.items():
            try:
                product_id = int(key)
                print(f"🔍 البحث عن منتج: ID={product_id}, الكمية={qty}")
                product = Product.query.get(product_id)
                if product:
                    item_total = float(product.price) * qty
                    total += item_total
                    cart_items.append({
                        'id': product.id,
                        'name': product.name_ar or product.name,
                        'price': float(product.price),
                        'quantity': qty,
                        'total': item_total,
                        'image_url': product.image_url
                    })
                    print(f"✅ تم إضافة المنتج: {product.name} - السعر: {product.price} - الكمية: {qty}")
                else:
                    print(f"❌ المنتج غير موجود: ID={product_id}")
            except (ValueError, TypeError) as e:
                print(f"⚠️ خطأ في معالجة المنتج: {e}")
                continue
        
        print(f"📊 إجمالي المنتجات في السلة: {len(cart_items)}, المجموع: {total}")
        
        return render_template_string("""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>سلة المشتريات</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .cart-item { display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #eee; }
                .cart-item img { width: 80px; height: 80px; object-fit: cover; border-radius: 5px; margin-left: 15px; }
                .cart-item-info { flex: 1; }
                .cart-item-actions { display: flex; align-items: center; gap: 10px; }
                .quantity-input { width: 60px; padding: 5px; text-align: center; }
                .btn { padding: 8px 16px; border: none; border-radius: 5px; cursor: pointer; }
                .btn-primary { background: #007bff; color: white; }
                .btn-danger { background: #dc3545; color: white; }
                .cart-total { text-align: right; font-size: 24px; font-weight: bold; margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
                .cart-actions { text-align: center; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div style="text-align: left; margin-bottom: 20px;">
                    <a href="/" class="btn" style="background: #6c757d; text-decoration: none; display: inline-block;">← العودة للرئيسية</a>
                </div>
                <h1>🛒 سلة المشتريات</h1>
                
                {% for item in cart_items %}
                <div class="cart-item">
                    <img src="{{ item.image_url or '/static/images/product1.jpg' }}" alt="{{ item.name }}">
                    <div class="cart-item-info">
                        <h3>{{ item.name }}</h3>
                        <p>السعر: {{ item.price }} $</p>
                        <p>المجموع: {{ item.total }} $</p>
                    </div>
                    <div class="cart-item-actions">
                        <input type="number" class="quantity-input" value="{{ item.quantity }}" min="1" onchange="updateQuantity({{ item.id }}, this.value)">
                        <button class="btn btn-danger" onclick="removeFromCart({{ item.id }})">حذف</button>
                    </div>
                </div>
                {% endfor %}
                
                <div class="cart-total">
                    المجموع الكلي: {{ "%.2f"|format(total) }} $
                </div>
                
                <div class="cart-actions">
                    <a href="/" class="btn btn-primary">🏠 العودة للرئيسية</a>
                    <button class="btn btn-primary" onclick="clearCart()">🗑️ تفريغ السلة</button>
                </div>
            </div>
            
            <script>
                function updateQuantity(productId, quantity) {
                    fetch('/cart/update', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({product_id: productId, quantity: parseInt(quantity)})
                    }).then(() => location.reload());
                }
                
                function removeFromCart(productId) {
                    if (confirm('هل أنت متأكد من حذف هذا المنتج من السلة؟')) {
                        fetch('/cart/remove', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({product_id: productId})
                        }).then(() => location.reload());
                    }
                }
                
                function clearCart() {
                    if (confirm('هل أنت متأكد من تفريغ السلة؟')) {
                        fetch('/cart/clear', {
                            method: 'POST'
                        }).then(() => location.reload());
                    }
                }
            </script>
        </body>
        </html>
        """, cart_items=cart_items, total=total)
        
    except Exception as e:
        return f"خطأ في عرض السلة: {str(e)}", 500

@app.route('/cart/update', methods=['POST'])
def cart_update():
    """تحديث كمية منتج في السلة"""
    try:
        from flask import request, redirect, url_for
        data = request.get_json()
        
        if not data:
            return redirect(url_for('cart_view'))
        
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            # حذف المنتج إذا كانت الكمية 0 أو أقل
            cart = _get_session_cart()
            cart.pop(product_id, None)
        else:
            # تحديث الكمية
            cart = _get_session_cart()
            cart[product_id] = quantity
        
        _save_session_cart(cart)
        return redirect(url_for('cart_view'))
        
    except Exception as e:
        return redirect(url_for('cart_view'))

@app.route('/cart/remove', methods=['POST'])
def cart_remove():
    """حذف منتج من السلة"""
    try:
        from flask import request, redirect, url_for
        data = request.get_json()
        
        if not data:
            return redirect(url_for('cart_view'))
        
        product_id = str(data.get('product_id'))
        cart = _get_session_cart()
        cart.pop(product_id, None)
        _save_session_cart(cart)
        
        return redirect(url_for('cart_view'))
        
    except Exception as e:
        return redirect(url_for('cart_view'))

@app.route('/cart/clear', methods=['POST'])
def cart_clear():
    """تفريغ السلة بالكامل"""
    try:
        _save_session_cart({})
        return redirect(url_for('cart_view'))
    except Exception as e:
        return redirect(url_for('cart_view'))

@app.route('/test-nature-category')
def test_nature_category():
    """اختبار قسم زينة الطبيعة"""
    try:
        # البحث عن منتجات في قسم زينة الطبيعة
        nature_products = Product.query.filter(
            Product.is_active == True,
            (Product.main_category == 'زينة الطبيعة') | (Product.main_category_ar == 'زينة الطبيعة')
        ).all()
        
        print(f"🌿 منتجات زينة الطبيعة: {len(nature_products)}")
        
        # البحث في حقل category العادي أيضاً
        nature_products_alt = Product.query.filter(
            Product.is_active == True,
            (Product.category == 'زينة الطبيعة') | (Product.category_ar == 'زينة الطبيعة')
        ).all()
        
        print(f"🌿 منتجات زينة الطبيعة (حقل category): {len(nature_products_alt)}")
        
        # عرض جميع المنتجات مع أقسامها
        all_products = Product.query.all()
        products_info = []
        for product in all_products:
            products_info.append({
                'id': product.id,
                'name': product.name,
                'name_ar': product.name_ar,
                'main_category': product.main_category,
                'main_category_ar': product.main_category_ar,
                'category': product.category,
                'category_ar': product.category_ar,
                'is_active': product.is_active
            })
        
        return f"""
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>اختبار قسم زينة الطبيعة</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .section {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .product {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }}
                .product.nature {{ border-left-color: #20c997; }}
                .btn {{ padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌿 اختبار قسم زينة الطبيعة</h1>
                
                <div class="section">
                    <h3>📊 إحصائيات</h3>
                    <p><strong>إجمالي المنتجات:</strong> {len(all_products)}</p>
                    <p><strong>منتجات زينة الطبيعة (main_category):</strong> {len(nature_products)}</p>
                    <p><strong>منتجات زينة الطبيعة (category):</strong> {len(nature_products_alt)}</p>
                </div>
                
                <div class="section">
                    <h3>🌿 منتجات زينة الطبيعة (main_category)</h3>
                    {''.join([f'''
                    <div class="product nature">
                        <strong>ID:</strong> {p.id} | 
                        <strong>الاسم:</strong> {p.name} | 
                        <strong>الاسم العربي:</strong> {p.name_ar} | 
                        <strong>القسم الرئيسي:</strong> {p.main_category} | 
                        <strong>السعر:</strong> {p.price} $
                    </div>
                    ''' for p in nature_products]) if nature_products else '<p>لا توجد منتجات في هذا القسم</p>'}
                </div>
                
                <div class="section">
                    <h3>🌿 منتجات زينة الطبيعة (category)</h3>
                    {''.join([f'''
                    <div class="product nature">
                        <strong>ID:</strong> {p.id} | 
                        <strong>الاسم:</strong> {p.name} | 
                        <strong>الاسم العربي:</strong> {p.name_ar} | 
                        <strong>القسم:</strong> {p.category} | 
                        <strong>السعر:</strong> {p.price} $
                    </div>
                    ''' for p in nature_products_alt]) if nature_products_alt else '<p>لا توجد منتجات في هذا القسم</p>'}
                </div>
                
                <div class="section">
                    <h3>🔍 جميع المنتجات مع أقسامها</h3>
                    {''.join([f'''
                    <div class="product">
                        <strong>ID:</strong> {p['id']} | 
                        <strong>الاسم:</strong> {p['name']} | 
                        <strong>القسم الرئيسي:</strong> {p['main_category']} | 
                        <strong>القسم:</strong> {p['category']} | 
                        <strong>نشط:</strong> {p['is_active']}
                    </div>
                    ''' for p in products_info])}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/" class="btn">🏠 العودة للرئيسية</a>
                    <a href="/category/زينة-الطبيعة" class="btn">🌿 عرض قسم زينة الطبيعة</a>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"خطأ في اختبار قسم زينة الطبيعة: {str(e)}", 500

@app.route('/add-sample-nature-products')
def add_sample_nature_products():
    """إضافة منتجات تجريبية لقسم زينة الطبيعة"""
    try:
        # التحقق من وجود منتجات في قسم زينة الطبيعة
        existing_products = Product.query.filter(
            (Product.main_category == 'زينة الطبيعة') | (Product.main_category_ar == 'زينة الطبيعة')
        ).count()
        
        if existing_products > 0:
            return f"✅ يوجد بالفعل {existing_products} منتج في قسم زينة الطبيعة"
        
        # إضافة منتجات تجريبية
        sample_products = [
            {
                'name': 'نبات الصبار الداخلي',
                'name_ar': 'نبات الصبار الداخلي',
                'description': 'نبات صبار جميل يضيف لمسة خضراء لمنزلك',
                'description_ar': 'نبات صبار جميل يضيف لمسة خضراء لمنزلك',
                'price': 45.0,
                'main_category': 'زينة الطبيعة',
                'main_category_ar': 'زينة الطبيعة',
                'category': 'نباتات داخلية',
                'category_ar': 'نباتات داخلية',
                'brand': 'طبيعة خضراء',
                'brand_ar': 'طبيعة خضراء',
                'image_url': '/static/images/product1.jpg',
                'is_active': True
            },
            {
                'name': 'مزهرية فخارية كلاسيكية',
                'name_ar': 'مزهرية فخارية كلاسيكية',
                'description': 'مزهرية فخارية جميلة مناسبة للنباتات والزهور',
                'description_ar': 'مزهرية فخارية جميلة مناسبة للنباتات والزهور',
                'price': 75.0,
                'main_category': 'زينة الطبيعة',
                'main_category_ar': 'زينة الطبيعة',
                'category': 'مزهريات',
                'category_ar': 'مزهريات',
                'brand': 'فخار أصيل',
                'brand_ar': 'فخار أصيل',
                'image_url': '/static/images/product1.jpg',
                'is_active': True
            },
            {
                'name': 'بذور نباتات عطرية',
                'name_ar': 'بذور نباتات عطرية',
                'description': 'مجموعة من البذور لنباتات عطرية جميلة',
                'description_ar': 'مجموعة من البذور لنباتات عطرية جميلة',
                'price': 25.0,
                'main_category': 'زينة الطبيعة',
                'main_category_ar': 'زينة الطبيعة',
                'category': 'بذور وشتلات',
                'category_ar': 'بذور وشتلات',
                'brand': 'حديقة عطرية',
                'brand_ar': 'حديقة عطرية',
                'image_url': '/static/images/product1.jpg',
                'is_active': True
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        
        return f"✅ تم إضافة {len(sample_products)} منتج تجريبي لقسم زينة الطبيعة"
        
    except Exception as e:
        return f"❌ خطأ في إضافة المنتجات التجريبية: {str(e)}", 500

@app.route('/admin')
def admin_dashboard():
    """لوحة تحكم المدير - مسار بديل"""
    return redirect('/')

# ===== صفحات إدارة الطلبات =====

@app.route('/admin/orders')
def admin_orders():
    """صفحة إدارة الطلبات"""
    try:
        # جلب الطلبات مع ترقيم الصفحات
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # فلترة الطلبات
        status_filter = request.args.get('status', '')
        search_term = request.args.get('search', '')
        
        query = Order.query
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        if search_term:
            query = query.filter(
                (Order.customer_name.contains(search_term)) |
                (Order.customer_email.contains(search_term)) |
                (Order.customer_phone.contains(search_term)) |
                (Order.order_number.contains(search_term))
            )
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # إحصائيات سريعة
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        
        return render_template('admin_orders.html',
                             orders=orders,
                             total_orders=total_orders,
                             pending_orders=pending_orders,
                             completed_orders=completed_orders,
                             current_status=status_filter,
                             current_search=search_term)
        
    except Exception as e:
        print(f"❌ خطأ في صفحة إدارة الطلبات: {e}")
        return f"خطأ في تحميل صفحة الطلبات: {str(e)}", 500

@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders_api():
    """API للحصول على جميع الطلبات"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', '')
        search_term = request.args.get('search', '')
        
        query = Order.query
        
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        if search_term:
            query = query.filter(
                (Order.customer_name.contains(search_term)) |
                (Order.customer_email.contains(search_term)) |
                (Order.customer_phone.contains(search_term)) |
                (Order.order_number.contains(search_term))
            )
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            }
        })
        
    except Exception as e:
        print(f"❌ خطأ في API الطلبات: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    """API لتحديث حالة الطلب"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        rejection_reason = data.get('rejection_reason', '')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'يرجى تحديد الحالة الجديدة'}), 400
        
        # التحقق من صحة الحالة
        valid_statuses = ['pending', 'processing', 'approved', 'rejected', 'completed', 'cancelled']
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
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة الطلب بنجاح',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ في تحديث حالة الطلب: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>', methods=['GET'])
def get_order_details_api(order_id):
    """API للحصول على تفاصيل طلب معين"""
    try:
        order = Order.query.get(order_id)
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
        print(f"❌ خطأ في الحصول على تفاصيل الطلب: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق إدارة المنتجات...")
    print("📍 السيرفر سيكون متاحًا على: http://127.0.0.1:5007")
    print("📱 للوصول من الهاتف: http://192.168.0.72:5007")
    app.run(debug=True, host='0.0.0.0', port=5007) 