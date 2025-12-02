from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, current_user
from backend.models import *
from datetime import datetime
from sqlalchemy import or_, and_
import json

messaging_bp = Blueprint('messaging', __name__)

# ============= MESSAGING SYSTEM =============

@messaging_bp.route('/api/chats', methods=['GET'])
@auth_required()
def get_chats():
    """Get all conversations for the current user."""
    try:
        # Get unique conversations
        sent_chats = db.session.query(Chat.receiver_id, Chat.product_id).filter_by(sender_id=current_user.id).distinct()
        received_chats = db.session.query(Chat.sender_id, Chat.product_id).filter_by(receiver_id=current_user.id).distinct()
        
        conversations = []
        processed_pairs = set()
        
        for chat in sent_chats.union(received_chats):
            other_user_id = chat[0] if chat[0] != current_user.id else (chat[1] if chat[1] else 0)
            product_id = chat[1]
            
            # Skip if we've already processed this conversation
            pair_key = (min(current_user.id, other_user_id), max(current_user.id, other_user_id), product_id or 0)
            if pair_key in processed_pairs:
                continue
            processed_pairs.add(pair_key)
            
            # Get last message
            last_message = Chat.query.filter(
                or_(
                    and_(Chat.sender_id == current_user.id, Chat.receiver_id == other_user_id),
                    and_(Chat.sender_id == other_user_id, Chat.receiver_id == current_user.id)
                )
            ).filter(or_(Chat.product_id == product_id, Chat.product_id == None)).order_by(Chat.created_at.desc()).first()
            
            if last_message:
                other_user = User.query.get(other_user_id)
                product = Product.query.get(product_id) if product_id else None
                
                if other_user:
                    conversations.append({
                        'other_user': {
                            'id': other_user.id,
                            'username': other_user.username,
                            'first_name': other_user.user_detail.first_name if other_user.user_detail else None
                        },
                        'product': {
                            'id': product.id,
                            'title': product.title,
                            'price': product.price,
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
    except Exception as e:
        print(f"Error getting chats: {e}")
        return jsonify({'error': 'Failed to fetch conversations'}), 500

@messaging_bp.route('/api/chats/<int:other_user_id>', methods=['GET'])
@auth_required()
def get_chat_messages(other_user_id):
    """Get messages between current user and another user for a specific product."""
    try:
        product_id = request.args.get('product_id', type=int)
        
        query = Chat.query.filter(
            or_(
                and_(Chat.sender_id == current_user.id, Chat.receiver_id == other_user_id),
                and_(Chat.sender_id == other_user_id, Chat.receiver_id == current_user.id)
            )
        )
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        else:
            query = query.filter(Chat.product_id.is_(None))
        
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
    except Exception as e:
        print(f"Error getting chat messages: {e}")
        return jsonify({'error': 'Failed to fetch messages'}), 500

@messaging_bp.route('/api/chats', methods=['POST'])
@auth_required()
def send_message():
    """Send a message to another user."""
    try:
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        if not data.get('receiver_id'):
            return jsonify({'error': 'Receiver ID is required'}), 400
        
        message = Chat(
            sender_id=current_user.id,
            receiver_id=data['receiver_id'],
            product_id=data.get('product_id'),
            message=data['message']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message.id
        }), 201
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'error': 'Failed to send message'}), 500