from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
from extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))  # Placeholder for image
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_sold = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    purchase_items = db.relationship('PurchaseItem', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_sold': self.is_sold,
            'seller_id': self.seller_id,
            'seller_username': self.seller.username if self.seller else None, # Added seller_username
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None
        }


class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    total_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.now)
    
    # Foreign keys
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    items = db.relationship('PurchaseItem', backref='purchase', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'total_amount': self.total_amount,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'buyer_id': self.buyer_id,
            'items': [item.to_dict() for item in self.items]
        }


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    
    # Foreign keys
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quantity': self.quantity,
            'price_at_purchase': self.price_at_purchase,
            'purchase_id': self.purchase_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None
        }
