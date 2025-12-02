from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime
import json

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/profile/<int:id>', methods=['GET'])
@auth_required()
def get_profile(id):
    id = id
    user = UserDetail.query.filter_by(user_id = id).first_or_404()

    return jsonify({
            'first_name' : user.first_name if user else None,
            'last_name': user.last_name if user else None,
            'phone_number': user.phone_number if user else None,
            'address': user.address if user else None,
            'dob': user.dob.isoformat() if user and user.dob else None,
            'bio': user.bio if user else None,
            'gender': user.gender if user else None
    }), 200

@users_bp.route('/api/profile/<int:id>', methods=['PUT'])
@auth_required()
def update_profile(id):
    # Get the user to be updated using the ID from the URL
    user_detail = UserDetail.query.filter_by(user_id = id).first_or_404()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update user fields

        if 'first_name' in data:
            if not data['first_name'].strip():
                return jsonify({'error': 'First name cannot be empty'}), 400
            user_detail.first_name = data['first_name'].strip()
            
        if 'last_name' in data:
            user_detail.last_name = data['last_name'].strip() if data['last_name'] else None
            
        if 'phone_number' in data:
            # Basic phone number validation
            phone = data['phone_number'].strip() if data['phone_number'] else None
            if phone and len(phone) < 10:
                return jsonify({'error': 'Invalid phone number format'}), 400
            user_detail.phone_number = phone
            
        if 'address' in data:
            user_detail.address = data['address'].strip() if data['address'] else None
            
        if 'bio' in data:
            bio = data['bio'].strip() if data['bio'] else None
            if bio and len(bio) > 500:  # Limit bio length
                return jsonify({'error': 'Bio cannot exceed 500 characters'}), 400
            user_detail.bio = bio
            
        if 'gender' in data:
            valid_genders = ['Male', 'Female', 'Other', 'Prefer not to say']
            if data['gender'] and data['gender'] not in valid_genders:
                return jsonify({'error': f'Invalid gender. Must be one of: {valid_genders}'}), 400
            user_detail.gender = data['gender'] if data['gender'] else None
            
        if 'dob' in data:
            if data['dob']:
                try:
                    dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
                    # Check if date is not in the future
                    if dob > datetime.now().date():
                        return jsonify({'error': 'Date of birth cannot be in the future'}), 400
                    # Check if user is not too old (reasonable limit)
                    if (datetime.now().date() - dob).days > 36500:  # 100 years
                        return jsonify({'error': 'Invalid date of birth'}), 400
                    user_detail.dob = dob
                except ValueError:
                    return jsonify({'error': 'Invalid date format. Use yyyy-mm-dd'}), 400
            else:
                user_detail.dob = None
        
        # Update the updated_at timestamp
        user_detail.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Return updated profile data
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                    'first_name': user_detail.first_name,
                    'last_name': user_detail.last_name,
                    'phone_number': user_detail.phone_number,
                    'address': user_detail.address,
                    'dob': user_detail.dob.isoformat() if user_detail.dob else None,
                    'bio': user_detail.bio,
                    'gender': user_detail.gender,
                    'updated_at': user_detail.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred while updating profile: {str(e)}'}), 500

@users_bp.route('/api/dashboard', methods=['GET'])
@auth_required()
def get_dashboard():
    # User's statistics
    total_listings = Product.query.filter_by(seller_id=current_user.id).count()
    active_listings = Product.query.filter_by(seller_id=current_user.id, is_active=True, is_sold=False).count()
    sold_items = Product.query.filter_by(seller_id=current_user.id, is_sold=True).count()
    total_purchases = Purchase.query.filter_by(buyer_id=current_user.id).count()
    total_sales = Purchase.query.filter_by(seller_id=current_user.id).count()
    unread_messages = Chat.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    
    # Recent activity
    recent_listings = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).limit(5).all()
    recent_purchases = Purchase.query.filter_by(buyer_id=current_user.id).order_by(Purchase.purchase_date.desc()).limit(5).all()
    recent_sales = Purchase.query.filter_by(seller_id=current_user.id).order_by(Purchase.purchase_date.desc()).limit(5).all()
    
    return jsonify({
        'stats': {
            'total_listings': total_listings,
            'active_listings': active_listings,
            'sold_items': sold_items,
            'total_purchases': total_purchases,
            'total_sales': total_sales,
            'unread_messages': unread_messages,
            'user_rating': current_user.rating,
            'total_reviews': current_user.total_reviews
        },
        'recent_listings': [{
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'views': p.views,
            'is_sold': p.is_sold,
            'created_at': p.created_at.isoformat()
        } for p in recent_listings],
        'recent_purchases': [{
            'id': purchase.id,
            'product_title': Product.query.get(purchase.product_id).title,
            'amount': purchase.amount,
            'purchase_date': purchase.purchase_date.isoformat()
        } for purchase in recent_purchases],
        'recent_sales': [{
            'id': sale.id,
            'product_title': Product.query.get(sale.product_id).title,
            'amount': sale.amount,
            'buyer': User.query.get(sale.buyer_id).username,
            'purchase_date': sale.purchase_date.isoformat()
        } for sale in recent_sales]
    }), 200