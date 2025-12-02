from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json

products_bp = Blueprint('products', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    condition = request.args.get('condition')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    is_auction = request.args.get('is_auction', type=bool)
    
    query = Product.query.filter_by(is_active=True, is_sold=False)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            or_(
                Product.title.contains(search),
                Product.description.contains(search),
                Product.brand.contains(search),
                Product.model.contains(search)
            )
        )
    
    if condition:
        query = query.filter_by(condition=condition)
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if is_auction is not None:
        query = query.filter_by(is_auction=is_auction)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Product, sort_by).desc())
    else:
        query = query.order_by(getattr(Product, sort_by))
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Optimize by joining related tables to avoid N+1 queries
    products_with_details = []
    for p in products.items:
        # Pre-fetch related data to avoid additional queries
        category_name = p.category.name if p.category else None
        seller_username = p.seller.username if p.seller else None
        seller_rating = p.seller.rating if p.seller else None
        
        product_dict = {
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'price': p.price,
            'condition': p.condition,
            'category': category_name,
            'seller': seller_username,
            'seller_rating': seller_rating,
            'images': json.loads(p.images) if p.images else [],
            'is_auction': p.is_auction,
            'current_bid': p.current_bid,
            'auction_end_time': p.auction_end_time.isoformat() if p.auction_end_time else None,
            'location': p.location,
            'brand': p.brand,
            'model': p.model,
            'views': p.views,
            'created_at': p.created_at.isoformat()
        }
        products_with_details.append(product_dict)
    
    return jsonify({
        'products': products_with_details,
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    }), 200

@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Optimize by joining related tables
    product = db.session.query(Product)\
        .options(db.joinedload(Product.category))\
        .options(db.joinedload(Product.seller).joinedload(User.user_detail))\
        .filter(Product.id == product_id)\
        .first_or_404()
    
    # Increment view count
    product.views += 1
    db.session.commit()
    
    seller_detail = product.seller.user_detail
    
    return jsonify({
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'price': product.price,
        'condition': product.condition,
        'category': {
            'id': product.category.id,
            'name': product.category.name
        },
        'seller': {
            'id': product.seller.id,
            'username': product.seller.username,
            'rating': product.seller.rating,
            'total_reviews': product.seller.total_reviews,
            'first_name': seller_detail.first_name if seller_detail else None,
            'last_name': seller_detail.last_name if seller_detail else None
        },
        'images': json.loads(product.images) if product.images else [],
        'is_auction': product.is_auction,
        'current_bid': product.current_bid,
        'minimum_bid': product.minimum_bid,
        'reserve_price': product.reserve_price,
        'auction_end_time': product.auction_end_time.isoformat() if product.auction_end_time else None,
        'location': product.location,
        'brand': product.brand,
        'model': product.model,
        'material': product.material,
        'views': product.views,
        'is_sold': product.is_sold,
        'created_at': product.created_at.isoformat()
    }), 200

@products_bp.route('/api/products', methods=['POST'])
@auth_required()
def create_product():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'price', 'condition', 'category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate condition
    valid_conditions = ['New', 'Like New', 'Good', 'Fair', 'Used']
    if data['condition'] not in valid_conditions:
        return jsonify({'error': f'Invalid condition. Must be one of: {valid_conditions}'}), 400
    
    product = Product(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        condition=data['condition'],
        category_id=data['category_id'],
        seller_id=current_user.id,
        location=data.get('location'),
        brand=data.get('brand'),
        model=data.get('model'),
        material=data.get('material'),
        is_auction=data.get('is_auction', False),
        images=json.dumps(data.get('images', []))
    )
    
    # Handle auction settings
    if product.is_auction:
        product.minimum_bid = data.get('minimum_bid', product.price)
        product.reserve_price = data.get('reserve_price')
        auction_duration = data.get('auction_duration', 7)  # days
        product.auction_end_time = datetime.utcnow() + timedelta(days=auction_duration)
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify({
        'message': 'Product created successfully',
        'product_id': product.id
    }), 201

@products_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@auth_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        product.title = data['title']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'condition' in data:
        valid_conditions = ['New', 'Like New', 'Good', 'Fair', 'Used']
        if data['condition'] not in valid_conditions:
            return jsonify({'error': f'Invalid condition. Must be one of: {valid_conditions}'}), 400
        product.condition = data['condition']
    if 'location' in data:
        product.location = data['location']
    if 'brand' in data:
        product.brand = data['brand']
    if 'model' in data:
        product.model = data['model']
    if 'material' in data:
        product.material = data['material']
    if 'images' in data:
        product.images = json.dumps(data['images'])
    
    db.session.commit()
    
    return jsonify({'message': 'Product updated successfully'}), 200

@products_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@auth_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

@products_bp.route('/api/my-products', methods=['GET'])
@auth_required()
def get_my_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [{
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'condition': p.condition,
            'is_auction': p.is_auction,
            'current_bid': p.current_bid,
            'is_sold': p.is_sold,
            'is_active': p.is_active,
            'views': p.views,
            'created_at': p.created_at.isoformat()
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    }), 200

# ============= CATEGORY MANAGEMENT =============

@products_bp.route('/api/categories', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    
    return jsonify({
        'categories': [{
            'id': cat.id,
            'name': cat.name,
            'description': cat.description,
            'subcategories': [{
                'id': sub.id,
                'name': sub.name,
                'description': sub.description
            } for sub in cat.subcategories]
        } for cat in categories]
    }), 200

@products_bp.route('/api/categories', methods=['POST'])
@auth_required()
def create_category():
    # Check if user is admin
    if not any(role.name == 'Admin' for role in current_user.roles):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    category = Category(
        name=data['name'],
        description=data.get('description'),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({'message': 'Category created successfully', 'category_id': category.id}), 201

# ============= AUCTION SYSTEM =============

@products_bp.route('/api/products/<int:product_id>/bid', methods=['POST'])
@auth_required()
def place_bid(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    bid_amount = data.get('amount')
    
    if not product.is_auction:
        return jsonify({'error': 'Product is not an auction item'}), 400
    
    if product.seller_id == current_user.id:
        return jsonify({'error': 'Cannot bid on your own product'}), 400
    
    if datetime.utcnow() > product.auction_end_time:
        return jsonify({'error': 'Auction has ended'}), 400
    
    if bid_amount <= product.current_bid or bid_amount < product.minimum_bid:
        return jsonify({'error': 'Bid amount must be higher than current bid and minimum bid'}), 400
    
    bid = Bid(
        product_id=product_id,
        bidder_id=current_user.id,
        amount=bid_amount
    )
    
    product.current_bid = bid_amount
    
    db.session.add(bid)
    db.session.commit()
    
    return jsonify({'message': 'Bid placed successfully'}), 201

@products_bp.route('/api/products/<int:product_id>/bids', methods=['GET'])
def get_product_bids(product_id):
    bids = Bid.query.filter_by(product_id=product_id).order_by(Bid.created_at.desc()).all()
    
    return jsonify({
        'bids': [{
            'id': bid.id,
            'bidder': bid.bidder.username,
            'amount': bid.amount,
            'created_at': bid.created_at.isoformat()
        } for bid in bids]
    }), 200

@products_bp.route('/api/my-bids', methods=['GET'])
@auth_required()
def get_my_bids():
    bids = Bid.query.filter_by(bidder_id=current_user.id).order_by(Bid.created_at.desc()).all()
    
    return jsonify({
        'bids': [{
            'id': bid.id,
            'product': {
                'id': bid.product.id,
                'title': bid.product.title,
                'current_bid': bid.product.current_bid,
                'auction_end_time': bid.product.auction_end_time.isoformat() if bid.product.auction_end_time else None,
                'is_sold': bid.product.is_sold
            },
            'amount': bid.amount,
            'is_winning': bid.amount == bid.product.current_bid,
            'created_at': bid.created_at.isoformat()
        } for bid in bids]
    }), 200