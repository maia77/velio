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