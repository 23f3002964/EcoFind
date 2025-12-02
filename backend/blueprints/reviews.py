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
    
    # Check if user has purchased from this seller
    purchase = Purchase.query.filter_by(
        buyer_id=current_user.id,
        seller_id=data['reviewee_id'],
        status='completed'
    ).first()
    
    if not purchase:
        return jsonify({'error': 'Can only review after completed transaction'}), 400
    
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
    reviews = Review.query.filter_by(reviewee_id=data['reviewee_id']).all()
    reviewee.rating = sum(r.rating for r in reviews) / len(reviews)
    reviewee.total_reviews = len(reviews)
    
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
            'reviewer': review.reviewer.username,
            'rating': review.rating,
            'comment': review.comment,
            'product_title': Product.query.get(review.product_id).title if review.product_id else None,
            'created_at': review.created_at.isoformat()
        } for review in reviews.items],
        'total': reviews.total,
        'pages': reviews.pages,
        'current_page': page
    }), 200