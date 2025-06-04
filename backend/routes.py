from flask import current_app as app, request, jsonify, make_response
from flask_security.recoverable import reset_password_token_status, send_reset_password_instructions
from backend.models import *
from flask_mail import Message, Mail
from flask_security import auth_required, hash_password, verify_password, current_user
from flask_security.recoverable import reset_password_token_status, send_reset_password_instructions
from backend.models import *
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
import json



datastore = app.security.datastore
mail = Mail()

@app.route("/protected", methods=['POST'])
@auth_required()
def protected():
    return "Protected Route"

@app.route('/', methods=['GET'])
def home():
    return "<h3> Backend App or Api app Running Fine.</h3>"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get('email').strip()
    password = data.get('password').strip()

    if not email or not password:
        return jsonify({"message": "Invalid input"}), 404

    user = datastore.find_user(email=email)
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    if verify_password(password, user.password):
        return jsonify({"token": user.get_auth_token(), "email": user.email, "role": user.roles[0].name, "id": user.id}), 200
    
    return jsonify({"message": "Incorrect Password"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get('email')
    f_name = data.get('first_name')
    l_name = data.get('last_name', None)
    gender = data.get('gender', None)
    dob = data.get('dob')
    bio = data.get('bio', None)
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    missing_fields = []
    if not email:
        missing_fields.append("email")
    if not f_name:
        missing_fields.append("first_name")
    if not dob:
         missing_fields.append("dob")
    if not password:
        missing_fields.append("password")
    if not confirm_password:
        missing_fields.append("confirm_password")

    if missing_fields:
        return make_response(jsonify({
            "status": "failure",
            "message": "Missing required fields.",
            "missing_fields": missing_fields,
        }), 400)

    # Parse date in dd-mm-yyyy format
    try:
        dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use yyyy-mm-dd"}), 400


    # Check if password and confirm password match
    if password != confirm_password:
        return make_response(jsonify({
            "status": "failure",
            "message": "Password and confirm password do not match.",
        }), 400)

    try:
        if not datastore.find_user(email=email):
            # Create the user
            user = datastore.create_user(email=email, password=hash_password(password), roles=['User'])
            
            # Create and assign UserDetail
            user.user_detail = UserDetail(
                first_name=f_name,
                last_name=l_name,
                dob=dob,
                bio=bio,
                gender=gender
            )
            db.session.add(user)
        else:
            return jsonify({"message": "User Already Exists."}), 409
        db.session.commit()
        return jsonify({"message": "User Created."}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message":str(e)}), 500


def send_reset_email(user):
    token = user.get_reset_token()
    user_detail = UserDetail.query.filter_by(user_id = user.id).first_or_404()
    reset_url = f"http://192.168.29.7:8081/reset-password/{token}"
    app_name = 'Stater App'
    msg = Message('Reset Your Password',
                  recipients=[user.email])
    
    # 1. Plaintext version (always include)
    msg.body = f'''
    Hi {user_detail.first_name},

    You requested a password reset.

    Reset your password by clicking the link below:
    {reset_url}

    If you didn’t request this, ignore this email.

    Thanks,
    {app_name} Team
    '''

    # HTML version with full name and button
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 500px; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #333;">Reset Your Password</h2>
        <p style="color: #555;">
            Hi {user_detail.first_name} {user_detail.last_name},<br><br>
            We got a request to reset your {app_name} password.
        </p>
        <div style="margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #3897f0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                Reset Password
            </a>
        </div>
        <p style="color: #999; font-size: 12px;">
            If you didn’t request this, you can safely ignore this email.
        </p>
        <p style="color: #ccc; font-size: 11px; text-align: center; margin-top: 40px;">
            © 2025 {app_name}
        </p>
    </div>
    '''
    mail.send(msg)

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email required"}), 400

    user = datastore.find_user(email=email)
    if user:
        send_reset_email(user)
    return jsonify({"msg": "If registered, a reset link has been sent."}), 200


@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    password = data.get('password')

    if not token or not password:
        return jsonify({"msg": "Token and password required"}), 400

    user = User.verify_reset_token(token)
    if not user:
        return jsonify({"msg": "Invalid or expired token"}), 400

    user.password = hash_password(password)  # Make sure hash_password is imported
    db.session.commit()

    return jsonify({"msg": "Password reset successful"}), 200



# ============= USER PROFILE MANAGEMENT =============

# @app.route('/api/profile/<int:id>', methods=['GET'])
# @auth_required()
# def get_profile(id):
#     id = id
#     user = UserDetail.query.filter_by(user_id = id).first_or_404()

#     return jsonify({
#             'last_name': user.last_name if user else None,
#             'phone_number': user.phone_number if user else None,
#             'address': user.address if user else None,
#             'dob': user.dob.isoformat() if user and user.dob else None,
#             'bio': user.bio if user else None,
#             'gender': user.gender if user else None
#     }), 200

@app.route('/api/profile/<int:id>', methods=['PUT'])
@auth_required()
def update_profile(id):
    # Get the user to be updated using the ID from the URL
    target_user = User.query.filter_by(user_id = id).first_or_404()
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update user fields
        if 'username' in data:
            # Check if username is taken by another user
            existing_user = User.query.filter(
                User.username == data['username'], 
                User.id != target_user.id
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already taken'}), 400
            target_user.username = data['username']
        
        
        if 'preferred_language' in data:
            valid_languages = ['en', 'hi', 'gu']
            if data['preferred_language'] not in valid_languages:
                return jsonify({'error': f'Invalid language. Must be one of: {valid_languages}'}), 400
            target_user.preferred_language = data['preferred_language']
        
        if 'active' in data:
            target_user.active = data['active']
        
        # Update user detail fields
        user_detail = target_user.user_detail
        if not user_detail:
            user_detail = UserDetail(user_id=target_user.id)
            db.session.add(user_detail)
            target_user.user_detail = user_detail
        
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
                'id': target_user.id,
                'username': target_user.username,
                'email': target_user.email,
                'preferred_language': target_user.preferred_language,
                'active': target_user.active,
                'rating': target_user.rating,
                'total_reviews': target_user.total_reviews,
                'user_detail': {
                    'first_name': user_detail.first_name,
                    'last_name': user_detail.last_name,
                    'phone_number': user_detail.phone_number,
                    'address': user_detail.address,
                    'dob': user_detail.dob.isoformat() if user_detail.dob else None,
                    'bio': user_detail.bio,
                    'gender': user_detail.gender,
                    'updated_at': user_detail.updated_at.isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred while updating profile: {str(e)}'}), 500

# ============= CATEGORY MANAGEMENT =============

@app.route('/api/categories', methods=['GET'])
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

@app.route('/api/categories', methods=['POST'])
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

# ============= PRODUCT MANAGEMENT =============

@app.route('/api/products', methods=['GET'])
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
    
    return jsonify({
        'products': [{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'price': p.price,
            'condition': p.condition,
            'category': p.category.name,
            'seller': p.seller.username,
            'seller_rating': p.seller.rating,
            'images': json.loads(p.images) if p.images else [],
            'is_auction': p.is_auction,
            'current_bid': p.current_bid,
            'auction_end_time': p.auction_end_time.isoformat() if p.auction_end_time else None,
            'location': p.location,
            'brand': p.brand,
            'model': p.model,
            'views': p.views,
            'created_at': p.created_at.isoformat()
        } for p in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': page
    }), 200

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    
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

@app.route('/api/products', methods=['POST'])
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

@app.route('/api/products/<int:product_id>', methods=['PUT'])
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

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@auth_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'}), 200

@app.route('/api/my-products', methods=['GET'])
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

# ============= AUCTION SYSTEM =============

@app.route('/api/products/<int:product_id>/bid', methods=['POST'])
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

@app.route('/api/products/<int:product_id>/bids', methods=['GET'])
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

@app.route('/api/my-bids', methods=['GET'])
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

# ============= CART MANAGEMENT =============

@app.route('/api/cart', methods=['GET'])
@auth_required()
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    total_amount = sum(item.product.price * item.quantity for item in cart_items if item.product.is_active and not item.product.is_sold)
    
    return jsonify({
        'items': [{
            'id': item.id,
            'product': {
                'id': item.product.id,
                'title': item.product.title,
                'price': item.product.price,
                'images': json.loads(item.product.images) if item.product.images else [],
                'seller': item.product.seller.username,
                'is_active': item.product.is_active,
                'is_sold': item.product.is_sold
            },
            'quantity': item.quantity,
            'subtotal': item.product.price * item.quantity,
            'added_at': item.added_at.isoformat()
        } for item in cart_items],
        'total_amount': total_amount,
        'total_items': len(cart_items)
    }), 200

@app.route('/api/cart', methods=['POST'])
@auth_required()
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id == current_user.id:
        return jsonify({'error': 'Cannot add your own product to cart'}), 400
    
    if product.is_auction or product.is_sold or not product.is_active:
        return jsonify({'error': 'Product not available for purchase'}), 400
    
    # Check if item already in cart
    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({'message': 'Item added to cart successfully'}), 201

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
@auth_required()
def update_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    quantity = data.get('quantity', 1)
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({'message': 'Cart item updated successfully'}), 200

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
@auth_required()
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200

@app.route('/api/cart/clear', methods=['DELETE'])
@auth_required()
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared successfully'}), 200

# ============= PURCHASE MANAGEMENT =============

@app.route('/api/checkout', methods=['POST'])
@auth_required()
def checkout():
    data = request.get_json()
    delivery_address = data.get('delivery_address')
    
    if not delivery_address:
        return jsonify({'error': 'Delivery address is required'}), 400
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    purchases = []
    total_amount = 0
    
    for item in cart_items:
        if item.product.is_sold or not item.product.is_active:
            return jsonify({'error': f'Product {item.product.title} is no longer available'}), 400
        
        purchase = Purchase(
            buyer_id=current_user.id,
            product_id=item.product_id,
            seller_id=item.product.seller_id,
            amount=item.product.price * item.quantity,
            delivery_address=delivery_address
        )
        
        # Mark product as sold
        item.product.is_sold = True
        
        purchases.append(purchase)
        total_amount += purchase.amount
        
        db.session.add(purchase)
    
    # Clear cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Purchase completed successfully',
        'total_amount': total_amount,
        'purchase_count': len(purchases)
    }), 201

@app.route('/api/purchases', methods=['GET'])
@auth_required()
def get_purchases():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    purchases = Purchase.query.filter_by(buyer_id=current_user.id).order_by(Purchase.purchase_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'purchases': [{
            'id': purchase.id,
            'product': {
                'id': purchase.product_id,
                'title': Product.query.get(purchase.product_id).title,
                'images': json.loads(Product.query.get(purchase.product_id).images) if Product.query.get(purchase.product_id).images else []
            },
            'seller': User.query.get(purchase.seller_id).username,
            'amount': purchase.amount,
            'status': purchase.status,
            'delivery_address': purchase.delivery_address,
            'purchase_date': purchase.purchase_date.isoformat()
        } for purchase in purchases.items],
        'total': purchases.total,
        'pages': purchases.pages,
        'current_page': page
    }), 200

@app.route('/api/sales', methods=['GET'])
@auth_required()
def get_sales():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    sales = Purchase.query.filter_by(seller_id=current_user.id).order_by(Purchase.purchase_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'sales': [{
            'id': sale.id,
            'product': {
                'id': sale.product_id,
                'title': Product.query.get(sale.product_id).title
            },
            'buyer': User.query.get(sale.buyer_id).username,
            'amount': sale.amount,
            'status': sale.status,
            'delivery_address': sale.delivery_address,
            'purchase_date': sale.purchase_date.isoformat()
        } for sale in sales.items],
        'total': sales.total,
        'pages': sales.pages,
        'current_page': page
    }), 200

# ============= MESSAGING SYSTEM =============

@app.route('/api/chats', methods=['GET'])
@auth_required()
def get_chats():
    # Get unique conversations
    sent_chats = db.session.query(Chat.receiver_id, Chat.product_id).filter_by(sender_id=current_user.id).distinct()
    received_chats = db.session.query(Chat.sender_id, Chat.product_id).filter_by(receiver_id=current_user.id).distinct()
    
    conversations = []
    processed_pairs = set()
    
    for chat in sent_chats.union(received_chats):
        other_user_id = chat[0] if chat[0] != current_user.id else chat[1]
        product_id = chat[1]
        
        pair_key = (min(current_user.id, other_user_id), max(current_user.id, other_user_id), product_id)
        if pair_key in processed_pairs:
            continue
        processed_pairs.add(pair_key)
        
        # Get last message
        last_message = Chat.query.filter(
            or_(
                and_(Chat.sender_id == current_user.id, Chat.receiver_id == other_user_id),
                and_(Chat.sender_id == other_user_id, Chat.receiver_id == current_user.id)
            )
        ).filter_by(product_id=product_id).order_by(Chat.created_at.desc()).first()
        
        if last_message:
            other_user = User.query.get(other_user_id)
            product = Product.query.get(product_id) if product_id else None
            
            conversations.append({
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'first_name': other_user.user_detail.first_name if other_user.user_detail else None
                },
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'images': json.loads(product.images) if product.images else []
                } if product else None,
                'last_message': {
                    'message': last_message.message,
                    'created_at': last_message.created_at.isoformat(),
                    'is_from_me': last_message.sender_id == current_user.id
                },
                'unread_count': Chat.query.filter_by(
                    sender_id=other_user_id,
                    receiver_id=current_user.id,
                    product_id=product_id,
                    is_read=False
                ).count()
            })
    
    return jsonify({'conversations': conversations}), 200

@app.route('/api/chats/<int:other_user_id>', methods=['GET'])
@auth_required()
def get_chat_messages(other_user_id):
    product_id = request.args.get('product_id', type=int)
    
    query = Chat.query.filter(
        or_(
            and_(Chat.sender_id == current_user.id, Chat.receiver_id == other_user_id),
            and_(Chat.sender_id == other_user_id, Chat.receiver_id == current_user.id)
        )
    )
    
    if product_id:
        query = query.filter_by(product_id=product_id)
    
    messages = query.order_by(Chat.created_at).all()
    
    # Mark messages as read
    Chat.query.filter_by(
        sender_id=other_user_id,
        receiver_id=current_user.id,
        product_id=product_id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    return jsonify({
        'messages': [{
            'id': msg.id,
            'message': msg.message,
            'is_from_me': msg.sender_id == current_user.id,
            'created_at': msg.created_at.isoformat()
        } for msg in messages]
    }), 200

@app.route('/api/chats', methods=['POST'])
@auth_required()
def send_message():
    data = request.get_json()
    
    if not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400
    
    message = Chat(
        sender_id=current_user.id,
        receiver_id=data['receiver_id'],
        product_id=data.get('product_id'),
        message=data['message']
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'message': 'Message sent successfully'}), 201

# ============= REVIEWS AND RATINGS =============

@app.route('/api/reviews', methods=['POST'])
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

@app.route('/api/users/<int:user_id>/reviews', methods=['GET'])
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

# ============= SAVED ITEMS =============

@app.route('/api/saved-items', methods=['GET'])
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

@app.route('/api/saved-items', methods=['POST'])
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

@app.route('/api/saved-items/<int:item_id>', methods=['DELETE'])
@auth_required()
def remove_saved_item(item_id):
    saved_item = SavedItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(saved_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from saved items'}), 200

# ============= SAVED SEARCHES =============

@app.route('/api/saved-searches', methods=['GET'])
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

@app.route('/api/saved-searches', methods=['POST'])
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

@app.route('/api/saved-searches/<int:search_id>', methods=['DELETE'])
@auth_required()
def delete_saved_search(search_id):
    saved_search = SavedSearch.query.filter_by(id=search_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(saved_search)
    db.session.commit()
    
    return jsonify({'message': 'Saved search deleted successfully'}), 200

# ============= DISPUTE MANAGEMENT =============

@app.route('/api/disputes', methods=['POST'])
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

@app.route('/api/disputes', methods=['GET'])
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

@app.route('/api/search', methods=['GET'])
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

@app.route('/api/recommendations', methods=['GET'])
@auth_required()
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

@app.route('/api/dashboard', methods=['GET'])
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

# ============= ADMIN ENDPOINTS =============

@app.route('/api/admin/disputes', methods=['GET'])
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

@app.route('/api/admin/disputes/<int:dispute_id>', methods=['PUT'])
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

@app.route('/api/admin/users', methods=['GET'])
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

@app.route('/api/admin/products', methods=['GET'])
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

# ============= TRANSLATIONS =============

@app.route('/api/translations', methods=['GET'])
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
