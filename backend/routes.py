# routes.py
from flask import request, jsonify
from flask_login import login_required, current_user, login_user, logout_user, login_manager
from models import User, Category, Product, CartItem, Purchase, PurchaseItem
from app import db
from extensions import login_manager

def register_routes(app):
    # Now use app inside this function

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Authentication Routes
    @app.route('/api/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            if not data or not data.get('email') or not data.get('password') or not data.get('username'):
                return jsonify({'error': 'Email, username and password are required'}), 400
            
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already registered'}), 409
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already taken'}), 409
            
            user = User(
                email=data['email'],
                username=data['username'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone_number=data.get('phone_number', ''),
                address=data.get('address', '')
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            
            return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password are required'}), 400
            
            user = User.query.filter_by(email=data['email']).first()
            if not user or not user.check_password(data['password']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            login_user(user, remember=True)
            return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logout', methods=['GET','POST'])
    @login_required
    def logout():
        try:
            logout_user()
            return jsonify({'message': 'Logout successful'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user', methods=['GET'])
    @login_required
    def get_current_user():
        try:
            return jsonify({'user': current_user.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
     
    # ---------------------------- User Profile Routes --------------------------- #
    @app.route('/api/user/profile', methods=['PUT'])
    @login_required
    def update_profile():
        try:
            data = request.get_json()
            user = current_user
            
            # Update user fields if provided
            if data.get('username') and data['username'] != user.username:
                if User.query.filter_by(username=data['username']).first():
                    return jsonify({'error': 'Username already taken'}), 409
                user.username = data['username']
            
            if data.get('email') and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return jsonify({'error': 'Email already registered'}), 409
                user.email = data['email']
            
            # Update optional fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone_number' in data:
                user.phone_number = data['phone_number']
            if 'address' in data:
                user.address = data['address']
            
            # Update password if provided
            if data.get('password'):
                user.set_password(data['password'])
            
            db.session.commit()
            return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        



        
    
 
