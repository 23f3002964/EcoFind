from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_security import UserMixin, RoleMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

# Association table for many-to-many User <-> Role
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='bearers')
    user_detail = db.relationship('UserDetail', backref='user', uselist=False, lazy=True)
    products = db.relationship('Product', backref='seller', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)

    def get_reset_token(self, expires_sec=300):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}, salt=app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_reset_token(token, max_age=300):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=max_age)
            return User.query.get(data['user_id'])
        except Exception:
            return None

class UserDetail(db.Model):
    __tablename__ = 'user_detail'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    dob = db.Column(db.Date, nullable=True)
    bio = db.Column(db.Text, nullable=True) 
    gender = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationship: one category can have many products
    products = db.relationship('Product', backref='category', lazy=True)

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
    
    # Foreign keys – note the corrected reference to 'user.id'
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    purchase_items = db.relationship('PurchaseItem', backref='product', lazy=True)

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys – note the corrected reference to 'user.id'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4()))
    total_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.now)
    
    # Foreign key – referencing the buyer from the User model
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship: one purchase can have multiple purchase items
    items = db.relationship('PurchaseItem', backref='purchase', lazy=True)

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    
    # Foreign keys
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
