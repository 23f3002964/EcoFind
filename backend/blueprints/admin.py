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
    search = request.args.get('search')
    
    query = Dispute.query
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            or_(
                Dispute.title.contains(search),
                Dispute.description.contains(search)
            )
        )
    
    disputes = query.order_by(Dispute.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'disputes': [{
            'id': dispute.id,
            'title': dispute.title,
            'description': dispute.description,
            'status': dispute.status,
            'complainant': {
                'id': dispute.complainant.id,
                'username': dispute.complainant.username,
                'email': dispute.complainant.email
            },
            'respondent': {
                'id': dispute.respondent.id,
                'username': dispute.respondent.username,
                'email': dispute.respondent.email
            },
            'product': {
                'id': dispute.product.id,
                'title': dispute.product.title
            } if dispute.product else None,
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
    
    updated_fields = []
    
    if 'status' in data:
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        dispute.status = data['status']
        updated_fields.append('status')
    
    if 'admin_notes' in data:
        dispute.admin_notes = data['admin_notes']
        updated_fields.append('admin_notes')
    
    # Send notification to both parties about the update
    if updated_fields:
        dispute.updated_at = datetime.utcnow()
        
        # Notify complainant
        complainant_notification = Notification(
            user_id=dispute.complainant_id,
            title=f"Dispute Update: {dispute.title}",
            message=f"The dispute '{dispute.title}' has been updated. Status: {dispute.status}. Please check the disputes section for details.",
            related_product_id=dispute.product_id
        )
        db.session.add(complainant_notification)
        
        # Notify respondent
        respondent_notification = Notification(
            user_id=dispute.respondent_id,
            title=f"Dispute Update: {dispute.title}",
            message=f"The dispute '{dispute.title}' has been updated. Status: {dispute.status}. Please check the disputes section for details.",
            related_product_id=dispute.product_id
        )
        db.session.add(respondent_notification)
    
    db.session.commit()
    
    return jsonify({'message': 'Dispute updated successfully'}), 200

@admin_bp.route('/api/admin/disputes/<int:dispute_id>/assign', methods=['POST'])
@auth_required()
def admin_assign_dispute(dispute_id):
    """Assign a dispute to an admin for handling"""
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    dispute = Dispute.query.get_or_404(dispute_id)
    data = request.get_json()
    
    # In a more complex system, we might assign to specific admins
    # For now, we'll just mark as in_progress
    dispute.status = 'in_progress'
    dispute.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Dispute assigned successfully'}), 200

@admin_bp.route('/api/admin/disputes/stats', methods=['GET'])
@auth_required()
def admin_dispute_stats():
    """Get dispute statistics for admin dashboard"""
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get counts by status
    status_counts = {}
    for status in ['open', 'in_progress', 'resolved', 'closed']:
        status_counts[status] = Dispute.query.filter_by(status=status).count()
    
    # Get recent disputes
    recent_disputes = Dispute.query.order_by(Dispute.created_at.desc()).limit(5).all()
    
    # Get disputes by date (for chart data)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_disputes_count = Dispute.query.filter(Dispute.created_at >= thirty_days_ago).count()
    
    return jsonify({
        'status_counts': status_counts,
        'recent_disputes': [{
            'id': dispute.id,
            'title': dispute.title,
            'status': dispute.status,
            'created_at': dispute.created_at.isoformat()
        } for dispute in recent_disputes],
        'recent_disputes_count': recent_disputes_count
    }), 200

# New endpoint for getting admin dashboard data
@admin_bp.route('/api/admin/dashboard', methods=['GET'])
@auth_required()
def admin_dashboard():
    """Get comprehensive admin dashboard data"""
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    
    # Get product statistics
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True, is_sold=False).count()
    
    # Get dispute statistics
    status_counts = {}
    for status in ['open', 'in_progress', 'resolved', 'closed']:
        status_counts[status] = Dispute.query.filter_by(status=status).count()
    
    # Get recent activity
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    
    return jsonify({
        'user_stats': {
            'total': total_users,
            'active': active_users
        },
        'product_stats': {
            'total': total_products,
            'active': active_products
        },
        'dispute_stats': status_counts,
        'recent_users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.user_detail.created_at.isoformat() if user.user_detail else None
        } for user in recent_users],
        'recent_products': [{
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'created_at': product.created_at.isoformat()
        } for product in recent_products]
    }), 200

@admin_bp.route('/api/admin/users', methods=['GET'])
@auth_required()
def admin_get_users():
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search')
    
    query = User.query
    
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    users = query.order_by(User.id).paginate(
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
            'created_at': user.user_detail.created_at.isoformat() if user.user_detail else None
        } for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    }), 200