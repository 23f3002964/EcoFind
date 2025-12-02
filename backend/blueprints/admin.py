from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/disputes', methods=['GET'])
@auth_required()
def admin_get_disputes():
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Dispute.query
    if status:
        query = query.filter_by(status=status)
    
    disputes = query.order_by(Dispute.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'disputes': [{
            'id': dispute.id,
            'title': dispute.title,
            'description': dispute.description,
            'status': dispute.status,
            'complainant': dispute.complainant.username,
            'respondent': dispute.respondent.username,
            'product_title': Product.query.get(dispute.product_id).title if dispute.product_id else None,
            'admin_notes': dispute.admin_notes,
            'created_at': dispute.created_at.isoformat(),
            'updated_at': dispute.updated_at.isoformat()
        } for dispute in disputes.items],
        'total': disputes.total,
        'pages': disputes.pages,
        'current_page': page
    }), 200

@admin_bp.route('/api/admin/disputes/<int:dispute_id>', methods=['PUT'])
@auth_required()
def admin_update_dispute(dispute_id):
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    dispute = Dispute.query.get_or_404(dispute_id)
    data = request.get_json()
    
    if 'status' in data:
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        dispute.status = data['status']
    
    if 'admin_notes' in data:
        dispute.admin_notes = data['admin_notes']
    
    db.session.commit()
    
    return jsonify({'message': 'Dispute updated successfully'}), 200

@admin_bp.route('/api/admin/users', methods=['GET'])
@auth_required()
def admin_get_users():
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    users = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'active': user.active,
            'rating': user.rating,
            'total_reviews': user.total_reviews,
            'roles': [role.name for role in user.roles],
            'total_products': Product.query.filter_by(seller_id=user.id).count(),
            'total_purchases': Purchase.query.filter_by(buyer_id=user.id).count()
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200

@admin_bp.route('/api/admin/products', methods=['GET'])
@auth_required()
def admin_get_products():
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Product.query
    if search:
        query = query.filter(Product.title.contains(search))
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [{
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'condition': p.condition,
            'seller': p.seller.username,
            'is_active': p.is_active,
            'is_sold': p.is_sold,
            'is_auction': p.is_auction,
            'views': p.views,
            'created_at': p.created_at.isoformat()
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    }), 200