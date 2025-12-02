from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime
from sqlalchemy import or_, and_
import json

reviews_bp = Blueprint('reviews', __name__)

# ============= REVIEWS AND RATINGS =============

@reviews_bp.route('/api/reviews', methods=['POST'])
@auth_required()
def create_review():
    data = request.get_json()
    
    # Validate required fields
    if not data.get('reviewee_id') or not data.get('rating'):
        return jsonify({'error': 'Reviewee ID and rating are required'}), 400
    
    # Check if user has a transaction with this user (either as buyer or seller)
    purchase_as_buyer = Purchase.query.filter_by(
        buyer_id=current_user.id,
        seller_id=data['reviewee_id'],
        status='completed'
    ).first()
    
    purchase_as_seller = Purchase.query.filter_by(
        buyer_id=data['reviewee_id'],
        seller_id=current_user.id,
        status='completed'
    ).first()
    
    # Must have completed transaction with the user
    if not purchase_as_buyer and not purchase_as_seller:
        return jsonify({'error': 'Can only review users you have transacted with'}), 400
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        reviewer_id=current_user.id,
        reviewee_id=data['reviewee_id'],
        product_id=data.get('product_id')
    ).first()
    
    if existing_review:
        return jsonify({'error': 'Review already exists'}), 400
    
    # Validate rating
    rating = data.get('rating')
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    review = Review(
        reviewer_id=current_user.id,
        reviewee_id=data['reviewee_id'],
        product_id=data.get('product_id'),
        rating=rating,
        comment=data.get('comment', '')
    )
    
    db.session.add(review)
    
    # Update user's average rating
    reviewee = User.query.get(data['reviewee_id'])
    if reviewee:
        reviews = Review.query.filter_by(reviewee_id=data['reviewee_id']).all()
        if reviews:
            reviewee.rating = sum(r.rating for r in reviews) / len(reviews)
            reviewee.total_reviews = len(reviews)
        else:
            reviewee.rating = 0.0
            reviewee.total_reviews = 0
    
    db.session.commit()
    
    return jsonify({'message': 'Review created successfully'}), 201

@reviews_bp.route('/api/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = Review.query.filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'reviews': [{
            'id': review.id,
            'reviewer': {
                'id': review.reviewer.id,
                'username': review.reviewer.username,
                'rating': review.reviewer.rating
            },
            'rating': review.rating,
            'comment': review.comment,
            'product_title': Product.query.get(review.product_id).title if review.product_id else None,
            'created_at': review.created_at.isoformat()
        } for review in reviews.items],
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': page
    }), 200

@reviews_bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
@auth_required()
def delete_review(review_id):
    """Allow users to report inappropriate reviews"""
    review = Review.query.get_or_404(review_id)
    
    # Only reviewer, reviewee, or admin can delete/report a review
    if not (current_user.id == review.reviewer_id or 
            current_user.id == review.reviewee_id or
            any(role.name == 'Admin' for role in current_user.roles)):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # For regular users, we'll mark as reported rather than delete
    # For admins, we'll actually delete
    if any(role.name == 'Admin' for role in current_user.roles):
        db.session.delete(review)
        db.session.commit()
        return jsonify({'message': 'Review deleted successfully'}), 200
    else:
        # Mark review as reported for admin review
        # In a full implementation, we might add a 'reported' flag to the review model
        # For now, we'll send a notification to admins
        admins = User.query.filter(User.roles.any(name='Admin')).all()
        for admin in admins:
            notification = Notification(
                user_id=admin.id,
                title="Review Reported",
                message=f"A review by {review.reviewer.username} for {review.reviewee.username} has been reported.",
                related_product_id=review.product_id
            )
            db.session.add(notification)
        
        db.session.commit()
        return jsonify({'message': 'Review reported successfully. Admin will review shortly.'}), 200

# New endpoint for getting user's own reviews (as reviewer)
@reviews_bp.route('/api/my-reviews', methods=['GET'])
@auth_required()
def get_my_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    reviews = Review.query.filter_by(reviewer_id=current_user.id).order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'reviews': [{
            'id': review.id,
            'reviewee': {
                'id': review.reviewee.id,
                'username': review.reviewee.username,
                'rating': review.reviewee.rating
            },
            'product': {
                'id': review.product.id,
                'title': review.product.title
            } if review.product else None,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat()
        } for review in reviews.items],
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': page
    }), 200
