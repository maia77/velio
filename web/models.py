from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    """نموذج المنتج"""
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    # إظهار المنتج في قسم "كل ما يحتاجه منزلك" و"وصل حديثاً"
    is_home_essentials = db.Column(db.Boolean, default=True)
    is_new_arrival = db.Column(db.Boolean, default=False)
    
    # علاقة مع الصور المتعددة
    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """تحويل المنتج إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'name_ar': self.name_ar,
            'description': self.description,
            'description_ar': self.description_ar,
            'price': self.price,
            'category': self.category,
            'category_ar': self.category_ar,
            'brand': self.brand,
            'brand_ar': self.brand_ar,
            'image_url': self.image_url,
            'main_category': self.main_category,
            'main_category_ar': self.main_category_ar,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'is_home_essentials': self.is_home_essentials,
            'is_new_arrival': self.is_new_arrival
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'


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


class Comment(db.Model):
    """نموذج التعليقات على المنتجات"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1..5 اختياري
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'content': self.content,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_approved': self.is_approved,
        }

    def __repr__(self):
        return f'<Comment #{self.id} on Product {self.product_id}>'


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
        """الحصول على عرض حالة الطلب باللغة المطلوبة"""
        status_map = {
            'pending': {'ar': 'قيد المراجعة', 'en': 'Pending'},
            'processing': {'ar': 'قيد المعالجة', 'en': 'Processing'},
            'approved': {'ar': 'تم الموافقة', 'en': 'Approved'},
            'shipped': {'ar': 'تم الإرسال', 'en': 'Shipped'},
            'rejected': {'ar': 'تم الرفض', 'en': 'Rejected'},
            'completed': {'ar': 'مكتمل', 'en': 'Completed'},
            'cancelled': {'ar': 'ملغي', 'en': 'Cancelled'}
        }
        return status_map.get(self.status, {}).get(language, self.status)
    
    def __repr__(self):
        return f'<Order {self.order_number} - {self.customer_name}>'


class OrderStatusHistory(db.Model):
    """نموذج تاريخ حالة الطلبات"""
    __tablename__ = 'order_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.String(50), nullable=True)  # من قام بتغيير الحالة
    notes = db.Column(db.Text, nullable=True)  # ملاحظات إضافية
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
        return f'<OrderStatusHistory {self.id} - Order {self.order_id}: {self.old_status} -> {self.new_status}>'