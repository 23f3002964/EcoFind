# routes.py
from flask import request, jsonify,render_template
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
    

    # ------------------------------- login routes ------------------------------- #
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
    

    # ------------------------------- logout route ------------------------------- #
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
        



    # ------------------------------ Product Routes ------------------------------ #
    @app.route('/api/products', methods=['GET'])
    def get_products():
        try:
            # Get query parameters for filtering
            category_id = request.args.get('category_id', type=int)
            search_query = request.args.get('q', '')
            
            # Start with base query
            query = Product.query.filter_by(is_sold=False)
            
            # Apply filters if provided
            if category_id:
                query = query.filter_by(category_id=category_id)
            
            if search_query:
                query = query.filter(Product.title.ilike(f'%{search_query}%'))
            
            # Execute query and return results
            products = query.all()
            return jsonify({'products': [product.to_dict() for product in products]}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    

    @app.route('/api/products/<int:product_id>', methods=['GET'])
    def get_product(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            return jsonify({'product': product.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products', methods=['POST'])
    @login_required
    def create_product():
        try:
            data = request.get_json()
            
            # Validate required fields
            if not all(key in data for key in ['title', 'description', 'price', 'category_id']):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Validate category exists
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Invalid category ID'}), 400
            
            # Create new product
            product = Product(
                title=data['title'],
                description=data['description'],
                price=float(data['price']),
                image_url=data.get('image_url', ''),
                seller_id=current_user.id,
                category_id=data['category_id']
            )
            
            db.session.add(product)
            db.session.commit()
            
            return jsonify({'message': 'Product created successfully', 'product': product.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products/<int:product_id>', methods=['PUT'])
    @login_required
    def update_product(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            
            # Check if user is the seller
            if product.seller_id != current_user.id:
                return jsonify({'error': 'Unauthorized to edit this product'}), 403
            
            data = request.get_json()
            
            # Update product fields if provided
            if 'title' in data:
                product.title = data['title']
            if 'description' in data:
                product.description = data['description']
            if 'price' in data:
                product.price = float(data['price'])
            if 'image_url' in data:
                product.image_url = data['image_url']
            if 'category_id' in data:
                # Validate category exists
                category = Category.query.get(data['category_id'])
                if not category:
                    return jsonify({'error': 'Invalid category ID'}), 400
                product.category_id = data['category_id']
            
            db.session.commit()
            return jsonify({'message': 'Product updated successfully', 'product': product.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    @login_required
    def delete_product(product_id):
        try:
            product = Product.query.get_or_404(product_id)
            
            # Check if user is the seller
            if product.seller_id != current_user.id:
                return jsonify({'error': 'Unauthorized to delete this product'}), 403
            
            db.session.delete(product)
            db.session.commit()
            
            return jsonify({'message': 'Product deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/products', methods=['GET'])
    @login_required
    def get_user_products():
        try:
            products = Product.query.filter_by(seller_id=current_user.id).all()
            return jsonify({'products': [product.to_dict() for product in products]}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500



    # ------------------------------ Category Routes ----------------------------- #
    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            return jsonify({'categories': [category.to_dict() for category in categories]}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/categories', methods=['POST'])
    @login_required
    def create_category():
        try:
            data = request.get_json()
            
            if not data or not data.get('name'):
                return jsonify({'error': 'Category name is required'}), 400
            
            if Category.query.filter_by(name=data['name']).first():
                return jsonify({'error': 'Category already exists'}), 409
            
            category = Category(
                name=data['name'],
                description=data.get('description', '')
            )
            
            db.session.add(category)
            db.session.commit()
            
            return jsonify({'message': 'Category created successfully', 'category': category.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    

    # -------------------------------- Cart Routes ------------------------------- #
    @app.route('/api/cart', methods=['GET'])
    @login_required
    def get_cart():
        try:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            return jsonify({'cart_items': [item.to_dict() for item in cart_items]}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cart', methods=['POST'])
    @login_required
    def add_to_cart():
        try:
            data = request.get_json()
            
            if not data or not data.get('product_id'):
                return jsonify({'error': 'Product ID is required'}), 400
            
            product = Product.query.get_or_404(data['product_id'])
            
            # Check if product is already sold
            if product.is_sold:
                return jsonify({'error': 'Product is already sold'}), 400
            
            # Check if product is already in cart
            existing_item = CartItem.query.filter_by(
                user_id=current_user.id,
                product_id=product.id
            ).first()
            
            if existing_item:
                existing_item.quantity += data.get('quantity', 1)
            else:
                cart_item = CartItem(
                    user_id=current_user.id,
                    product_id=product.id,
                    quantity=data.get('quantity', 1)
                )
                db.session.add(cart_item)
            
            db.session.commit()
            return jsonify({'message': 'Product added to cart successfully'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cart/<int:cart_item_id>', methods=['PUT'])
    @login_required
    def update_cart_item(cart_item_id):
        try:
            cart_item = CartItem.query.get_or_404(cart_item_id)
            
            # Check if user owns this cart item
            if cart_item.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized to modify this cart item'}), 403
            
            data = request.get_json()
            
            if 'quantity' in data:
                if data['quantity'] <= 0:
                    db.session.delete(cart_item)
                else:
                    cart_item.quantity = data['quantity']
            
            db.session.commit()
            return jsonify({'message': 'Cart item updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/cart/<int:cart_item_id>', methods=['DELETE'])
    @login_required
    def remove_from_cart(cart_item_id):
        try:
            cart_item = CartItem.query.get_or_404(cart_item_id)
            
            # Check if user owns this cart item
            if cart_item.user_id != current_user.id:
                return jsonify({'error': 'Unauthorized to delete this cart item'}), 403
            
            db.session.delete(cart_item)
            db.session.commit()
            
            return jsonify({'message': 'Item removed from cart successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        

    # ------------------------------ Purchase Routes ----------------------------- #
    @app.route('/api/purchases', methods=['POST'])
    @login_required

    def create_purchase():
        try:
            # Get user's cart items
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
            
            if not cart_items:
                return jsonify({'error': 'Cart is empty'}), 400
            
            # Calculate total amount
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            
            # Create purchase
            purchase = Purchase(
                buyer_id=current_user.id,
                total_amount=total_amount
            )
            db.session.add(purchase)
            db.session.flush()  # This flushes the transaction and assigns an ID to the purchase
            
            # Create purchase items and mark products as sold
            for cart_item in cart_items:
                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,  # Now purchase.id is available
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.product.price
                )
                db.session.add(purchase_item)
                
                # Mark product as sold
                cart_item.product.is_sold = True
                
                # Remove from cart
                db.session.delete(cart_item)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Purchase completed successfully',
                'purchase': purchase.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/purchases', methods=['GET'])
    @login_required
    def get_user_purchases():
        try:
            purchases = Purchase.query.filter_by(buyer_id=current_user.id).order_by(Purchase.purchase_date.desc()).all()
            return jsonify({'purchases': [purchase.to_dict() for purchase in purchases]}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/purchases/<int:purchase_id>', methods=['GET'])
    @login_required
    def get_purchase(purchase_id):
        try:
            purchase = Purchase.query.get_or_404(purchase_id)
            
            # Check if user is the buyer
            if purchase.buyer_id != current_user.id:
                return jsonify({'error': 'Unauthorized to view this purchase'}), 403
            
            return jsonify({'purchase': purchase.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ------------------------------- error handler ------------------------------ #
        # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden'}), 403

        
    

    

        



        
    
 
