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
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    preferred_language = db.Column(db.String(10), default='en')
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='bearers')
    user_detail = db.relationship('UserDetail', backref='user', uselist=False, lazy=True)
    products = db.relationship('Product', backref='seller', lazy=True)
    bids = db.relationship('Bid', backref='bidder', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    purchases = db.relationship('Purchase', backref='buyer', lazy=True)
    sent_messages = db.relationship('Chat', foreign_keys='Chat.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Chat', foreign_keys='Chat.receiver_id', backref='receiver', lazy=True)
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy=True)
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', backref='reviewee', lazy=True)
    saved_items = db.relationship('SavedItem', backref='user', lazy=True)
    disputes_filed = db.relationship('Dispute', foreign_keys='Dispute.complainant_id', backref='complainant', lazy=True)

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
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    images = db.Column(db.Text)
    is_auction = db.Column(db.Boolean, default=False)
    auction_end_time = db.Column(db.DateTime)
    minimum_bid = db.Column(db.Float)
    reserve_price = db.Column(db.Float)
    current_bid = db.Column(db.Float, default=0.0)
    is_sold = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    material = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    saved_by = db.relationship('SavedItem', backref='product', lazy=True)

class Bid(db.Model):
    __tablename__ = 'bid'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    __tablename__ = 'cartitem'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    __tablename__='purchase'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_address = db.Column(db.Text)

class Chat(db.Model):
    __tablename__='chat'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedItem(db.Model):
    __tablename__='saveditem'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedSearch(db.Model):
    __tablename__ ='savedsearch'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_query = db.Column(db.String(200), nullable=False)
    filters = db.Column(db.Text)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Dispute(db.Model):
    __tablename__='dispute'
    id = db.Column(db.Integer, primary_key=True)
    complainant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    respondent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
