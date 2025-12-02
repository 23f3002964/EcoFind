from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime
from sqlalchemy import or_, and_
import json

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/api/cart', methods=['GET'])
@auth_required()
def get_cart():
    # Optimize by joining related tables
    cart_items = db.session.query(CartItem)\
        .options(db.joinedload(CartItem.product))\
        .filter(CartItem.user_id == current_user.id)\
        .all()
    
    cart_items_with_details = []
    total_amount = 0
    
    for item in cart_items:
        if item.product and item.product.is_active and not item.product.is_sold:
            product_images = json.loads(item.product.images) if item.product.images else []
            
            subtotal = item.product.price * item.quantity
            total_amount += subtotal
            
            item_dict = {
                'id': item.id,
                'product': {
                    'id': item.product.id,
                    'title': item.product.title,
                    'price': item.product.price,
                    'images': product_images,
                    'seller': item.product.seller.username if item.product.seller else None,
                    'is_active': item.product.is_active,
                    'is_sold': item.product.is_sold
                },
                'quantity': item.quantity,
                'subtotal': subtotal,
                'added_at': item.added_at.isoformat()
            }
            cart_items_with_details.append(item_dict)
    
    return jsonify({
        'items': cart_items_with_details,
        'total_amount': total_amount,
        'total_items': len(cart_items_with_details)
    }), 200

@cart_bp.route('/api/cart', methods=['POST'])
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

@cart_bp.route('/api/cart/<int:item_id>', methods=['PUT'])
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

@cart_bp.route('/api/cart/<int:item_id>', methods=['DELETE'])
@auth_required()
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart'}), 200

@cart_bp.route('/api/cart/clear', methods=['DELETE'])
@auth_required()
def clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared successfully'}), 200

# ============= PURCHASE MANAGEMENT =============

@cart_bp.route('/api/checkout', methods=['POST'])
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

@cart_bp.route('/api/purchases', methods=['GET'])
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

@cart_bp.route('/api/sales', methods=['GET'])
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