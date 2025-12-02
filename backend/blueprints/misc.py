from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json

# Add imports for caching
from flask_caching import Cache

# Initialize cache later when app context is available
cache = None

def init_cache(app_instance):
    """Initialize cache with the app instance."""
    global cache
    try:
        cache = Cache(app_instance, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': app_instance.config.get('REDIS_URL', 'redis://localhost:6379/0')})
    except ImportError:
        # Fallback to simple in-memory cache if redis is not available
        cache = Cache(app_instance, config={'CACHE_TYPE': 'simple'})

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
    
    # Validate that complainant and respondent are different
    if current_user.id == data['respondent_id']:
        return jsonify({'error': 'Cannot file dispute against yourself'}), 400
    
    # Check if product exists (if provided)
    product = None
    if data.get('product_id'):
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'error': 'Product not found'}), 404
    
    dispute = Dispute(
        complainant_id=current_user.id,
        respondent_id=data['respondent_id'],
        product_id=data.get('product_id'),
        title=data['title'],
        description=data['description']
    )
    
    db.session.add(dispute)
    db.session.commit()
    
    # Send notification to respondent
    notification = Notification(
        user_id=data['respondent_id'],
        title="New Dispute Filed Against You",
        message=f"A dispute titled '{data['title']}' has been filed against you. Please check the disputes section for details.",
        related_product_id=data.get('product_id')
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'message': 'Dispute created successfully', 'dispute_id': dispute.id}), 201

@misc_bp.route('/api/disputes', methods=['GET'])
@auth_required()
def get_user_disputes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = Dispute.query.filter(
        or_(Dispute.complainant_id == current_user.id, Dispute.respondent_id == current_user.id)
    )
    
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
            'is_complainant': dispute.complainant_id == current_user.id,
            'other_party': {
                'id': dispute.respondent.id if dispute.complainant_id == current_user.id else dispute.complainant.id,
                'username': dispute.respondent.username if dispute.complainant_id == current_user.id else dispute.complainant.username
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

@misc_bp.route('/api/disputes/<int:dispute_id>', methods=['PUT'])
@auth_required()
def update_dispute(dispute_id):
    dispute = Dispute.query.get_or_404(dispute_id)
    
    # Only complainant or respondent can update their own dispute
    if current_user.id not in [dispute.complainant_id, dispute.respondent_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Users can only add evidence or update description
    if 'description' in data and current_user.id == dispute.complainant_id:
        dispute.description = data['description']
    
    if 'evidence' in data:
        # In a full implementation, this would handle file uploads
        # For now, we'll just append to the description
        dispute.description += f"\n\nEvidence: {data['evidence']}"
    
    dispute.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Dispute updated successfully'}), 200

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
def get_recommendations():
    # Check if cache is available
    if cache:
        # Use cached version if available
        cached_result = cache.get('recommendations')
        if cached_result:
            return cached_result
    
    # Enhanced recommendation algorithm based on multiple factors
    # 1. User's saved items and purchase history
    saved_categories = db.session.query(Product.category_id).join(SavedItem).filter(SavedItem.user_id == current_user.id).distinct()
    purchased_categories = db.session.query(Product.category_id).join(Purchase).filter(Purchase.buyer_id == current_user.id).distinct()
    
    # 2. User's search history (if implemented)
    searched_categories = db.session.query(Product.category_id).join(SavedSearch).filter(SavedSearch.user_id == current_user.id).distinct()
    
    # Combine all category interests
    category_ids = [cat[0] for cat in saved_categories.union(purchased_categories).union(searched_categories)]
    
    # 3. Get user's preferred conditions
    preferred_conditions = db.session.query(Product.condition).join(Purchase).filter(Purchase.buyer_id == current_user.id).distinct()
    condition_list = [cond[0] for cond in preferred_conditions]
    
    if not category_ids:
        # Fallback to popular products
        recommendations = Product.query.filter_by(is_active=True, is_sold=False).order_by(Product.views.desc()).limit(10).all()
    else:
        # Enhanced recommendation query with multiple factors
        query = Product.query.filter(
            Product.category_id.in_(category_ids),
            Product.is_active == True,
            Product.is_sold == False,
            Product.seller_id != current_user.id
        )
        
        # Apply condition preference if user has bought items before
        if condition_list:
            query = query.filter(Product.condition.in_(condition_list))
            
        # Order by multiple factors: recency, views, and seller rating
        recommendations = query.order_by(
            Product.created_at.desc(),  # Recently added
            Product.views.desc(),       # Popular items
            Product.seller.has(User.rating.desc())  # Highly rated sellers
        ).limit(10).all()
    
    result = jsonify({
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
    
    # Cache the result if cache is available
    if cache:
        cache.set('recommendations', result, timeout=180)  # Cache for 3 minutes
        
    return result

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
            # Header and Navigation
            'welcome': 'Welcome to EcoFinds',
            'search_placeholder': 'Search for products...',
            'categories': 'Categories',
            'my_account': 'My Account',
            'cart': 'Cart',
            'messages': 'Messages',
            'saved_items': 'Saved Items',
            'dashboard': 'Dashboard',
            'profile': 'Profile',
            'logout': 'Logout',
            'language': 'Language',
            
            # Common Actions
            'save': 'Save',
            'cancel': 'Cancel',
            'delete': 'Delete',
            'edit': 'Edit',
            'view': 'View',
            'close': 'Close',
            'submit': 'Submit',
            'update': 'Update',
            
            # Dashboard
            'my_dashboard': 'My Dashboard',
            'total_listings': 'Total Listings',
            'active_listings': 'Active Listings',
            'sold_items': 'Sold Items',
            'total_purchases': 'Total Purchases',
            'total_sales': 'Total Sales',
            'unread_messages': 'Unread Messages',
            'user_rating': 'User Rating',
            'total_reviews': 'Total Reviews',
            
            # Product Related
            'products': 'Products',
            'add_product': 'Add Product',
            'my_listings': 'My Listings',
            'browse_products': 'Browse Products',
            'product_details': 'Product Details',
            'price': 'Price',
            'condition': 'Condition',
            'location': 'Location',
            'description': 'Description',
            'seller': 'Seller',
            'contact_seller': 'Contact Seller',
            
            # User Profile
            'personal_information': 'Personal Information',
            'full_name': 'Full Name',
            'email': 'Email',
            'date_of_birth': 'Date of Birth',
            'gender': 'Gender',
            'bio': 'Bio',
            'joined': 'Joined',
            'status': 'Status',
            'active': 'Active',
            'rating': 'Rating',
            'no_bio_available': 'No bio available',
            
            # Reviews
            'reviews': 'Reviews',
            'leave_review': 'Leave Review',
            'review_comment': 'Review Comment',
            'submit_review': 'Submit Review',
            
            # Disputes
            'disputes': 'Disputes',
            'file_dispute': 'File Dispute',
            'dispute_title': 'Dispute Title',
            'dispute_description': 'Dispute Description',
            'submit_dispute': 'Submit Dispute',
            
            # Notifications
            'notifications': 'Notifications',
            'mark_all_read': 'Mark All Read',
            'unread_notifications': 'unread notifications',
            'loading': 'Loading',
            'no_notifications': 'No notifications',
            'related_product': 'Related product',
            'view_all_notifications': 'View all notifications',
            'failed_mark_all_read': 'Failed to mark all notifications as read',
            'days_ago': 'd ago',
            'hours_ago': 'h ago',
            'minutes_ago': 'm ago',
            'just_now': 'Just now',
            
            # Chats/Messages
            'no_conversations_yet': 'No conversations yet',
            'conversations_will_appear_here': 'Your conversations with other users will appear here.',
            'general_conversation': 'General conversation',
            'failed_load_conversations': 'Failed to load conversations. Please try again.',
            
            # Saved Searches
            'saved_searches': 'Saved Searches',
            'save_search': 'Save Search',
            
            # Price Alerts
            'price_alerts': 'Price Alerts',
            'create_alert': 'Create Alert',
            'target_price': 'Target Price',
            
            # Authentication
            'login': 'Login',
            'signup': 'Sign Up',
            'forgot_password': 'Forgot Password',
            'reset_password': 'Reset Password',
            'verify_email': 'Verify Email',
            'verify_phone': 'Verify Phone',
            'i_accept_terms': 'I accept the',
            'terms_and_conditions': 'Terms and Conditions',
            
            # Form Labels
            'username': 'Username',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'phone_number': 'Phone Number',
            'address': 'Address',
            
            # Status Labels
            'open': 'Open',
            'in_progress': 'In Progress',
            'resolved': 'Resolved',
            'closed': 'Closed',
            
            # Home Page
            'why_use_ecofinds': 'Why Use EcoFinds?',
            'eco_friendly_focus': 'Eco-Friendly Focus',
            'eco_friendly_description': 'We list only verified sustainable and eco-conscious businesses.',
            'local_discovery': 'Local Discovery',
            'local_discovery_description': 'Find green shops, cafes, and services in your neighborhood.',
            'support_good_causes': 'Support Good Causes',
            'support_good_causes_description': 'Your purchases make a difference for the planet and people.',
            'ready_to_make_difference': 'Ready to Make a Difference?',
            'join_eco_conscious_shoppers': 'Join thousands of eco-conscious shoppers today.',
            'about_ecofinds': 'About EcoFinds',
            'mission_statement': "We're on a mission to connect eco-conscious consumers with sustainable businesses worldwide.",
            'all_rights_reserved': 'All rights reserved.',
            
            # NavBar
            'home': 'Home',
            'browse': 'Browse',
            'about': 'About',
            'users': 'Users',
            'expand_sidebar': 'Expand Sidebar',
            'collapse_sidebar': 'Collapse Sidebar',
            'confirm_logout': 'Are you sure you want to logout?'
        },
        'hi': {
            # Header and Navigation
            'welcome': 'EcoFinds में आपका स्वागत है',
            'search_placeholder': 'उत्पादों की खोज करें...',
            'categories': 'श्रेणियाँ',
            'my_account': 'मेरा खाता',
            'cart': 'कार्ट',
            'messages': 'संदेश',
            'saved_items': 'सहेजी गई वस्तुएँ',
            'dashboard': 'डैशबोर्ड',
            'profile': 'प्रोफ़ाइल',
            'logout': 'लॉग आउट',
            'language': 'भाषा',
            
            # Common Actions
            'save': 'सहेजें',
            'cancel': 'रद्द करें',
            'delete': 'हटाएँ',
            'edit': 'संपादित करें',
            'view': 'देखें',
            'close': 'बंद करें',
            'submit': 'जमा करें',
            'update': 'अपडेट करें',
            
            # Dashboard
            'my_dashboard': 'मेरा डैशबोर्ड',
            'total_listings': 'कुल लिस्टिंग',
            'active_listings': 'सक्रिय लिस्टिंग',
            'sold_items': 'बेचे गए आइटम',
            'total_purchases': 'कुल खरीदारी',
            'total_sales': 'कुल बिक्री',
            'unread_messages': 'अपठित संदेश',
            'user_rating': 'उपयोगकर्ता रेटिंग',
            'total_reviews': 'कुल समीक्षाएँ',
            
            # Product Related
            'products': 'उत्पाद',
            'add_product': 'उत्पाद जोड़ें',
            'my_listings': 'मेरी लिस्टिंग',
            'browse_products': 'उत्पाद ब्राउज़ करें',
            'product_details': 'उत्पाद विवरण',
            'price': 'मूल्य',
            'condition': 'शर्त',
            'location': 'स्थान',
            'description': 'विवरण',
            'seller': 'विक्रेता',
            'contact_seller': 'विक्रेता से संपर्क करें',
            
            # User Profile
            'personal_information': 'व्यक्तिगत जानकारी',
            'full_name': 'पूरा नाम',
            'email': 'ईमेल',
            'date_of_birth': 'जन्म तिथि',
            'gender': 'लिंग',
            'bio': 'जीवनी',
            'joined': 'शामिल हुए',
            'status': 'स्थिति',
            'active': 'सक्रिय',
            'rating': 'रेटिंग',
            'no_bio_available': 'कोई जीवनी उपलब्ध नहीं है',
            
            # Reviews
            'reviews': 'समीक्षाएँ',
            'leave_review': 'समीक्षा छोड़ें',
            'review_comment': 'समीक्षा टिप्पणी',
            'submit_review': 'समीक्षा जमा करें',
            
            # Disputes
            'disputes': 'विवाद',
            'file_dispute': 'विवाद दर्ज करें',
            'dispute_title': 'विवाद शीर्षक',
            'dispute_description': 'विवाद विवरण',
            'submit_dispute': 'विवाद जमा करें',
            
            # Notifications
            'notifications': 'अधिसूचनाएँ',
            'mark_all_read': 'सभी को पढ़ा हुआ चिह्नित करें',
            'unread_notifications': 'अपठित अधिसूचनाएँ',
            'loading': 'लोड हो रहा है',
            'no_notifications': 'कोई अधिसूचनाएँ नहीं',
            'related_product': 'संबंधित उत्पाद',
            'view_all_notifications': 'सभी अधिसूचनाएँ देखें',
            'failed_mark_all_read': 'सभी अधिसूचनाओं को पढ़ा हुआ चिह्नित करने में विफल',
            'days_ago': 'दिन पहले',
            'hours_ago': 'घंटे पहले',
            'minutes_ago': 'मिनट पहले',
            'just_now': 'अभी',
            
            # Chats/Messages
            'no_conversations_yet': 'अभी तक कोई वार्तालाप नहीं',
            'conversations_will_appear_here': 'आपके अन्य उपयोगकर्ताओं के साथ वार्तालाप यहाँ दिखाई देंगे।',
            'general_conversation': 'सामान्य वार्तालाप',
            'failed_load_conversations': 'वार्तालाप लोड करने में विफल। कृपया पुनः प्रयास करें।',
            
            # Saved Searches
            'saved_searches': 'सहेजी गई खोजें',
            'save_search': 'खोज सहेजें',
            
            # Price Alerts
            'price_alerts': 'मूल्य अलर्ट',
            'create_alert': 'अलर्ट बनाएँ',
            'target_price': 'लक्ष्य मूल्य',
            
            # Authentication
            'login': 'लॉग इन करें',
            'signup': 'साइन अप करें',
            'forgot_password': 'पासवर्ड भूल गए',
            'reset_password': 'पासवर्ड रीसेट करें',
            'verify_email': 'ईमेल सत्यापित करें',
            'verify_phone': 'फ़ोन सत्यापित करें',
            'i_accept_terms': 'मैं स्वीकार करता हूँ',
            'terms_and_conditions': 'नियम और शर्तें',
            
            # Form Labels
            'username': 'उपयोगकर्ता नाम',
            'password': 'पासवर्ड',
            'confirm_password': 'पासवर्ड की पुष्टि करें',
            'first_name': 'पहला नाम',
            'last_name': 'अंतिम नाम',
            'phone_number': 'फ़ोन नंबर',
            'address': 'पता',
            
            # Status Labels
            'open': 'खुला',
            'in_progress': 'प्रगति पर है',
            'resolved': 'हल किया गया',
            'closed': 'बंद',
            
            # Home Page
            'why_use_ecofinds': 'EcoFinds क्यों उपयोग करें?',
            'eco_friendly_focus': 'पर्यावरण अनुकूल ध्यान',
            'eco_friendly_description': 'हम केवल सत्यापित स्थायी और पर्यावरण जागरूक व्यवसायों की सूची बनाते हैं।',
            'local_discovery': 'स्थानीय खोज',
            'local_discovery_description': 'अपने पड़ोस में हरित दुकानें, कैफे और सेवाएं खोजें।',
            'support_good_causes': 'अच्छे कारणों का समर्थन करें',
            'support_good_causes_description': 'आपकी खरीदारी पृथ्वी और लोगों के लिए अंतर लाती है।',
            'ready_to_make_difference': 'अंतर लाने के लिए तैयार हैं?',
            'join_eco_conscious_shoppers': 'आज हजारों पर्यावरण जागरूक खरीदारों के साथ जुड़ें।',
            'about_ecofinds': 'EcoFinds के बारे में',
            'mission_statement': 'हम पर्यावरण जागरूक उपभोक्ताओं को विश्वव्यापी स्थायी व्यवसायों से जोड़ने के लिए प्रतिबद्ध हैं।',
            'all_rights_reserved': 'सर्वाधिकार सुरक्षित।',
            
            # NavBar
            'home': 'होम',
            'browse': 'ब्राउज़ करें',
            'about': 'हमारे बारे में',
            'users': 'उपयोगकर्ता',
            'expand_sidebar': 'साइडबार विस्तार करें',
            'collapse_sidebar': 'साइडबार संक्षिप्त करें',
            'confirm_logout': 'क्या आप वाकई लॉगआउट करना चाहते हैं?'
        },
        'gu': {
            # Header and Navigation
            'welcome': 'EcoFinds માં આપનું સ્વાગત છે',
            'search_placeholder': 'ઉત્પાદનો માટે શોધો...',
            'categories': 'શ્રેણીઓ',
            'my_account': 'મારું એકાઉન્ટ',
            'cart': 'કાર્ટ',
            'messages': 'સંદેશા',
            'saved_items': 'સાચવેલી વસ્તુઓ',
            'dashboard': 'ડેશબોર્ડ',
            'profile': 'પ્રોફાઇલ',
            'logout': 'લૉગ આઉટ',
            'language': 'ભાષા',
            
            # Common Actions
            'save': 'સાચવો',
            'cancel': 'રદ કરો',
            'delete': 'કાઢી મૂકો',
            'edit': 'સંપાદિત કરો',
            'view': 'જુઓ',
            'close': 'બંધ કરો',
            'submit': 'સબમિટ કરો',
            'update': 'અપડેટ કરો',
            
            # Dashboard
            'my_dashboard': 'મારું ડેશબોર્ડ',
            'total_listings': 'કુલ લિસ્ટિંગ',
            'active_listings': 'સક્રિય લિસ્ટિંગ',
            'sold_items': 'વેચાયેલ વસ્તુઓ',
            'total_purchases': 'કુલ ખરીદીઓ',
            'total_sales': 'કુલ વેચાણ',
            'unread_messages': 'અપઠાયેલ સંદેશા',
            'user_rating': 'વપરાશકર્તા રેટિંગ',
            'total_reviews': 'કુલ સમીક્ષાઓ',
            
            # Product Related
            'products': 'ઉત્પાદનો',
            'add_product': 'ઉત્પાદન ઉમેરો',
            'my_listings': 'મારી લિસ્ટિંગ',
            'browse_products': 'ઉત્પાદનો બ્રાઉઝ કરો',
            'product_details': 'ઉત્પાદન વિગતો',
            'price': 'કિંમત',
            'condition': 'શરત',
            'location': 'સ્થાન',
            'description': 'વર્ણન',
            'seller': 'વિક્રેતા',
            'contact_seller': 'વિક્રેતાનો સંપર્ક કરો',
            
            # User Profile
            'personal_information': 'વ્યક્તિગત માહિતી',
            'full_name': 'પૂરું નામ',
            'email': 'ઇમેઇલ',
            'date_of_birth': 'જન્મ તારીખ',
            'gender': 'લિંગ',
            'bio': 'બાયો',
            'joined': 'જોડાયો',
            'status': 'સ્થિતિ',
            'active': 'સક્રિય',
            'rating': 'રેટિંગ',
            'no_bio_available': 'કોઈ બાયો ઉપલબ્ધ નથી',
            
            # Reviews
            'reviews': 'સમીક્ષાઓ',
            'leave_review': 'સમીક્ષા આપો',
            'review_comment': 'સમીક્ષા ટિપ્પણી',
            'submit_review': 'સમીક્ષા સબમિટ કરો',
            
            # Disputes
            'disputes': 'વિવાદો',
            'file_dispute': 'વિવાદ ફાઇલ કરો',
            'dispute_title': 'વિવાદ શીર્ષક',
            'dispute_description': 'વિવાદ વર્ણન',
            'submit_dispute': 'વિવાદ સબમિટ કરો',
            
            # Notifications
            'notifications': 'સૂચનો',
            'mark_all_read': 'બધાને વાંચેલ તરીકે ચિહ્નિત કરો',
            'unread_notifications': 'અપઠાયેલ સૂચનો',
            'loading': 'લોડ થઈ રહ્યું છે',
            'no_notifications': 'કોઈ સૂચનો નથી',
            'related_product': 'સંબંધિત ઉત્પાદન',
            'view_all_notifications': 'બધી સૂચનો જુઓ',
            'failed_mark_all_read': 'બધી સૂચનોને વાંચેલ તરીકે ચિહ્નિત કરવામાં નિષ્ફળ',
            'days_ago': 'દિવસ પહેલાં',
            'hours_ago': 'કલાક પહેલાં',
            'minutes_ago': 'મિનિટ પહેલાં',
            'just_now': 'હમણાં',
            
            # Chats/Messages
            'no_conversations_yet': 'હજુ સુધી કોઈ વાર્તાલાપ નથી',
            'conversations_will_appear_here': 'તમારા અન્ય વપરાશકર્તાઓ સાથેના વાર્તાલાપ અહીં દેખાશે.',
            'general_conversation': 'સામાન્ય વાર્તાલાપ',
            'failed_load_conversations': 'વાર્તાલાપ લોડ કરવામાં નિષ્ફળ. કૃપા કરીને ફરી પ્રયત્ન કરો.',
            
            # Saved Searches
            'saved_searches': 'સાચવેલી શોધો',
            'save_search': 'શોધ સાચવો',
            
            # Price Alerts
            'price_alerts': 'કિંમત ચેતવણીઓ',
            'create_alert': 'ચેતવણી બનાવો',
            'target_price': 'લક્ષ્ય કિંમત',
            
            # Authentication
            'login': 'લૉગ ઇન કરો',
            'signup': 'સાઇન અપ કરો',
            'forgot_password': 'પાસવર્ડ ભૂલી ગયા',
            'reset_password': 'પાસવર્ડ રીસેટ કરો',
            'verify_email': 'ઇમેઇલ ચકાસો',
            'verify_phone': 'ફોન ચકાસો',
            'i_accept_terms': 'હું સ્વીકારું છું',
            'terms_and_conditions': 'નિયમો અને શરતો',
            
            # Form Labels
            'username': 'વપરાશકર્તા નામ',
            'password': 'પાસવર્ડ',
            'confirm_password': 'પાસવર્ડની પુષ્ટિ કરો',
            'first_name': 'પ્રથમ નામ',
            'last_name': 'છેલ્લું નામ',
            'phone_number': 'ફોન નંબર',
            'address': 'સરનામું',
            
            # Status Labels
            'open': 'ખોલો',
            'in_progress': 'પ્રગતિ પર છે',
            'resolved': 'ઉકેલાયો',
            'closed': 'બંધ',
            
            # Home Page
            'why_use_ecofinds': 'EcoFinds શા માટે વાપરવું?',
            'eco_friendly_focus': 'પર્યાવરણ મૈત્રીપૂર્ણ ધ્યાન',
            'eco_friendly_description': 'અમે ફક્ત ચકાસાયેલ ટકાઉ અને પર્યાવરણ મૈત્રીપૂર્ણ વ્યવસાયોની યાદી કરીએ છીએ.',
            'local_discovery': 'સ્થાનિક શોધ',
            'local_discovery_description': 'તમારા પડોશમાં લીલી દુકાનો, કેફે અને સેવાઓ શોધો.',
            'support_good_causes': 'સારા કારણોને આધાર આપો',
            'support_good_causes_description': 'તમારી ખરીદી પૃથ્વી અને લોકો માટે તફાવત લાવે છે.',
            'ready_to_make_difference': 'તફાવત લાવવા માટે તૈયાર છો?',
            'join_eco_conscious_shoppers': 'આજે હજારો પર્યાવરણ મૈત્રીપૂર્ણ ખરીદદારો સાથે જોડાઓ.',
            'about_ecofinds': 'EcoFinds વિશે',
            'mission_statement': 'અમે પર્યાવરણ મૈત્રીપૂર્ણ ગ્રાહકોને વિશ્વવ્યાપી ટકાઉ વ્યવસાયો સાથે જોડવાનું મિશન ધરાવીએ છીએ.',
            'all_rights_reserved': 'સર્વાધિકાર સુરક્ષિત',
            
            # NavBar
            'home': 'હોમ',
            'browse': 'બ્રાઉઝ કરો',
            'about': 'અમારા વિશે',
            'users': 'વપરાશકર્તાઓ',
            'expand_sidebar': 'સાઇડબાર વિસ્તારો',
            'collapse_sidebar': 'સાઇડબાર સંકુચિત કરો',
            'confirm_logout': 'શું તમે ખરેખર લૉગઆઉટ કરવા માંગો છો?'
        }
    }
    
    return jsonify(translations.get(lang, translations['en'])), 200

# ============= NOTIFICATIONS =============

@misc_bp.route('/api/notifications', methods=['GET'])
@auth_required()
def get_notifications():
    """Get user's notifications with pagination and filtering options"""
    # Get query parameters for pagination and filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    include_read = request.args.get('include_read', False, type=bool)
    
    # Build query for user's notifications
    query = Notification.query.filter_by(user_id=current_user.id)
    
    # Optionally filter out read notifications
    if not include_read:
        query = query.filter_by(is_read=False)
    
    # Order by creation time (newest first) and paginate
    notifications = query.order_by(Notification.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Return notifications in JSON format
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'related_product_id': n.related_product_id,
            'created_at': n.created_at.isoformat()
        } for n in notifications.items],
        'total': notifications.total,
        'pages': notifications.pages,
        'current_page': page
    }), 200

@misc_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@auth_required()
def mark_notification_as_read(notification_id):
    """Mark a specific notification as read"""
    # Find notification belonging to current user
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    
    # Mark as read and save to database
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as read'}), 200

@misc_bp.route('/api/notifications/read-all', methods=['PUT'])
@auth_required()
def mark_all_notifications_as_read():
    """Mark all of the user's unread notifications as read"""
    # Update all unread notifications for current user
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return jsonify({'message': 'All notifications marked as read'}), 200

# ============= PRICE ALERTS =============

@misc_bp.route('/api/price-alerts', methods=['GET'])
@auth_required()
def get_price_alerts():
    """Get user's price alerts with pagination"""
    # Get query parameters for pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query for user's price alerts
    query = PriceAlert.query.filter_by(user_id=current_user.id)
    
    # Order by creation time (newest first) and paginate
    price_alerts = query.order_by(PriceAlert.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Return price alerts in JSON format
    return jsonify({
        'price_alerts': [{
            'id': pa.id,
            'product': {
                'id': pa.product.id,
                'title': pa.product.title,
                'price': pa.product.price
            },
            'target_price': pa.target_price,
            'status': pa.status,
            'created_at': pa.created_at.isoformat()
        } for pa in price_alerts.items],
        'total': price_alerts.total,
        'pages': price_alerts.pages,
        'current_page': page
    }), 200

@misc_bp.route('/api/price-alerts', methods=['POST'])
@auth_required()
def create_price_alert():
    """Create a new price alert for a product"""
    data = request.get_json()
    
    # Validate required fields
    product_id = data.get('product_id')
    target_price = data.get('target_price')
    
    if not product_id or not target_price:
        return jsonify({'error': 'Product ID and target price are required'}), 400
    
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if user already has an alert for this product
    existing_alert = PriceAlert.query.filter_by(
        user_id=current_user.id, 
        product_id=product_id
    ).first()
    
    if existing_alert:
        return jsonify({'error': 'You already have a price alert for this product'}), 400
    
    # Create new price alert
    price_alert = PriceAlert(
        user_id=current_user.id,
        product_id=product_id,
        target_price=float(target_price)
    )
    
    db.session.add(price_alert)
    db.session.commit()
    
    return jsonify({
        'message': 'Price alert created successfully',
        'price_alert_id': price_alert.id
    }), 201

@misc_bp.route('/api/price-alerts/<int:alert_id>', methods=['DELETE'])
@auth_required()
def delete_price_alert(alert_id):
    """Delete a price alert"""
    # Find price alert belonging to current user
    price_alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first_or_404()
    
    # Delete the price alert
    db.session.delete(price_alert)
    db.session.commit()
    
    return jsonify({'message': 'Price alert deleted successfully'}), 200
