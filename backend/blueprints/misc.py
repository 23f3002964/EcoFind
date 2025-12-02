from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json

# Add imports for caching
try:
    from flask_caching import Cache
    cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0')})
except ImportError:
    # Fallback to simple in-memory cache if redis is not available
    from flask_caching import Cache
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

misc_bp = Blueprint('misc', __name__)

# ============= SAVED ITEMS =============

@misc_bp.route('/api/saved-items', methods=['GET'])
@auth_required()
def get_saved_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    saved_items = SavedItem.query.filter_by(user_id=current_user.id).order_by(SavedItem.saved_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'saved_items': [{
            'id': item.id,
            'product': {
                'id': item.product.id,
                'title': item.product.title,
                'price': item.product.price,
                'images': json.loads(item.product.images) if item.product.images else [],
                'is_sold': item.product.is_sold,
                'is_active': item.product.is_active
            },
            'saved_at': item.saved_at.isoformat()
        } for item in saved_items.items],
        'total': saved_items.total,
        'pages': saved_items.pages,
        'current_page': page
    }), 200

@misc_bp.route('/api/saved-items', methods=['POST'])
@auth_required()
def save_item():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400
    
    # Check if already saved
    existing = SavedItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        return jsonify({'error': 'Item already saved'}), 400
    
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    saved_item = SavedItem(user_id=current_user.id, product_id=product_id)
    db.session.add(saved_item)
    db.session.commit()
    
    return jsonify({'message': 'Item saved successfully'}), 201

@misc_bp.route('/api/saved-items/<int:item_id>', methods=['DELETE'])
@auth_required()
def remove_saved_item(item_id):
    saved_item = SavedItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(saved_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from saved items'}), 200

# ============= SAVED SEARCHES =============

@misc_bp.route('/api/saved-searches', methods=['GET'])
@auth_required()
def get_saved_searches():
    searches = SavedSearch.query.filter_by(user_id=current_user.id).order_by(SavedSearch.created_at.desc()).all()
    
    return jsonify({
        'saved_searches': [{
            'id': search.id,
            'name': search.name,
            'search_query': search.search_query,
            'filters': json.loads(search.filters) if search.filters else {},
            'created_at': search.created_at.isoformat()
        } for search in searches]
    }), 200

@misc_bp.route('/api/saved-searches', methods=['POST'])
@auth_required()
def save_search():
    data = request.get_json()
    
    saved_search = SavedSearch(
        user_id=current_user.id,
        search_query=data.get('search_query', ''),
        filters=json.dumps(data.get('filters', {})),
        name=data.get('name', f"Search {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    )
    
    db.session.add(saved_search)
    db.session.commit()
    
    return jsonify({'message': 'Search saved successfully'}), 201

@misc_bp.route('/api/saved-searches/<int:search_id>', methods=['DELETE'])
@auth_required()
def delete_saved_search(search_id):
    saved_search = SavedSearch.query.filter_by(id=search_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(saved_search)
    db.session.commit()
    
    return jsonify({'message': 'Saved search deleted successfully'}), 200

# ============= DISPUTE MANAGEMENT =============

@misc_bp.route('/api/disputes', methods=['POST'])
@auth_required()
def create_dispute():
    data = request.get_json()
    
    required_fields = ['respondent_id', 'title', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    dispute = Dispute(
        complainant_id=current_user.id,
        respondent_id=data['respondent_id'],
        product_id=data.get('product_id'),
        title=data['title'],
        description=data['description']
    )
    
    db.session.add(dispute)
    db.session.commit()
    
    return jsonify({'message': 'Dispute created successfully', 'dispute_id': dispute.id}), 201

@misc_bp.route('/api/disputes', methods=['GET'])
@auth_required()
def get_user_disputes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    disputes = Dispute.query.filter(
        or_(Dispute.complainant_id == current_user.id, Dispute.respondent_id == current_user.id)
    ).order_by(Dispute.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'disputes': [{
            'id': dispute.id,
            'title': dispute.title,
            'description': dispute.description,
            'status': dispute.status,
            'is_complainant': dispute.complainant_id == current_user.id,
            'other_party': dispute.respondent.username if dispute.complainant_id == current_user.id else dispute.complainant.username,
            'product_title': Product.query.get(dispute.product_id).title if dispute.product_id else None,
            'admin_notes': dispute.admin_notes,
            'created_at': dispute.created_at.isoformat()
        } for dispute in disputes.items],
        'total': disputes.total,
        'pages': disputes.pages,
        'current_page': page
    }), 200

# ============= SEARCH AND RECOMMENDATIONS =============

@misc_bp.route('/api/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)
    condition = request.args.get('condition')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    location = request.args.get('location')
    sort_by = request.args.get('sort_by', 'relevance')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    products_query = Product.query.filter_by(is_active=True, is_sold=False)
    
    if query:
        products_query = products_query.filter(
            or_(
                Product.title.contains(query),
                Product.description.contains(query),
                Product.brand.contains(query),
                Product.model.contains(query)
            )
        )
    
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    
    if condition:
        products_query = products_query.filter_by(condition=condition)
    
    if min_price:
        products_query = products_query.filter(Product.price >= min_price)
    
    if max_price:
        products_query = products_query.filter(Product.price <= max_price)
    
    if location:
        products_query = products_query.filter(Product.location.contains(location))
    
    # Apply sorting
    if sort_by == 'price_low':
        products_query = products_query.order_by(Product.price)
    elif sort_by == 'price_high':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'newest':
        products_query = products_query.order_by(Product.created_at.desc())
    elif sort_by == 'popular':
        products_query = products_query.order_by(Product.views.desc())
    else:  # relevance
        products_query = products_query.order_by(Product.created_at.desc())
    
    products = products_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'products': [{
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'condition': p.condition,
            'location': p.location,
            'images': json.loads(p.images) if p.images else [],
            'seller': p.seller.username,
            'seller_rating': p.seller.rating,
            'is_auction': p.is_auction,
            'current_bid': p.current_bid,
            'views': p.views
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    }), 200

@misc_bp.route('/api/recommendations', methods=['GET'])
@auth_required()
@cache.cached(timeout=180, key_prefix='recommendations')  # Cache for 3 minutes
def get_recommendations():
    # Simple recommendation based on user's saved items and purchase history
    saved_categories = db.session.query(Product.category_id).join(SavedItem).filter(SavedItem.user_id == current_user.id).distinct()
    purchased_categories = db.session.query(Product.category_id).join(Purchase).filter(Purchase.buyer_id == current_user.id).distinct()
    
    category_ids = [cat[0] for cat in saved_categories.union(purchased_categories)]
    
    if not category_ids:
        # Fallback to popular products
        recommendations = Product.query.filter_by(is_active=True, is_sold=False).order_by(Product.views.desc()).limit(10).all()
    else:
        recommendations = Product.query.filter(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.is_sold == False,
            Product.seller_id != current_user.id
        ).order_by(Product.created_at.desc()).limit(10).all()
    
    return jsonify({
        'recommendations': [{
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'images': json.loads(p.images) if p.images else [],
            'seller': p.seller.username,
            'seller_rating': p.seller.rating,
            'condition': p.condition
        } for p in recommendations]
    }), 200

# ============= DASHBOARD AND ANALYTICS =============

@misc_bp.route('/api/dashboard', methods=['GET'])
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

# ============= TRANSLATIONS =============

@misc_bp.route('/api/translations', methods=['GET'])
def get_translations():
    lang = request.args.get('lang', 'en')
    
    translations = {
        'en': {
            'welcome': 'Welcome to EcoFinds',
            'search_placeholder': 'Search for products...',
            'categories': 'Categories',
            'my_account': 'My Account',
            'cart': 'Cart',
            'messages': 'Messages',
            'saved_items': 'Saved Items',
            'dashboard': 'Dashboard',
            'profile': 'Profile',
            'logout': 'Logout'
        },
        'hi': {
            'welcome': 'EcoFinds में आपका स्वागत है',
            'search_placeholder': 'उत्पाद खोजें...',
            'categories': 'श्रेणियां',
            'my_account': 'मेरा खाता',
            'cart': 'कार्ट',
            'messages': 'संदेश',
            'saved_items': 'सहेजे गए आइटम',
            'dashboard': 'डैशबोर्ड',
            'profile': 'प्रोफ़ाइल',
            'logout': 'लॉग आउट'
        },
        'gu': {
            'welcome': 'EcoFinds માં તમારું સ્વાગત છે',
            'search_placeholder': 'ઉત્પાદનો શોધો...',
            'categories': 'કેટેગરીઝ',
            'my_account': 'મારું એકાઉન્ટ',
            'cart': 'કાર્ટ',
            'messages': 'સંદેશા',
            'saved_items': 'સાચવેલી વસ્તુઓ',
            'dashboard': 'ડેશબોર્ડ',
            'profile': 'પ્રોફાઇલ',
            'logout': 'લૉગ આઉટ'
        }
    }
    
    return jsonify(translations.get(lang, translations['en'])), 200