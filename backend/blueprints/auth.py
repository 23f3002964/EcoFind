from flask import Blueprint, request, jsonify, make_response, current_app as app
from flask_security import auth_required, hash_password, verify_password, current_user
from flask_security.recoverable import send_reset_password_instructions
from backend.models import *
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
import json
import random
import string

auth_bp = Blueprint('auth', __name__)
datastore = None
mail = Mail()

# In-memory storage for OTPs (in production, use Redis or database)
# TODO: Replace with Redis or database storage for production
otp_storage = {}

def init_auth_blueprint(app_instance, datastore_instance):
    global datastore
    datastore = datastore_instance
    mail.init_app(app_instance)

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

    If you didn't request this, ignore this email.

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
            If you didn't request this, you can safely ignore this email.
        </p>
        <p style="color: #ccc; font-size: 11px; text-align: center; margin-top: 40px;">
            © 2025 {app_name}
        </p>
    </div>
    '''
    mail.send(msg)

def send_verification_email(user, user_detail):
    """Send email verification link to user"""
    token = user.get_reset_token(expires_sec=86400)  # 24 hours expiry
    verification_url = f"http://192.168.29.7:8081/verify-email/{token}"
    app_name = 'EcoFinds'
    
    msg = Message('Verify Your Email Address',
                  recipients=[user.email])
    
    msg.body = f'''
    Hi {user_detail.first_name},

    Thank you for registering with {app_name}!

    Please verify your email address by clicking the link below:
    {verification_url}

    If you didn't register for an account, you can safely ignore this email.

    Thanks,
    {app_name} Team
    '''
    
    msg.html = f'''
    <div style="font-family: Arial, sans-serif; max-width: 500px; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #333;">Verify Your Email Address</h2>
        <p style="color: #555;">
            Hi {user_detail.first_name} {user_detail.last_name},<br><br>
            Thank you for registering with {app_name}!
        </p>
        <p style="color: #555;">
            Please verify your email address by clicking the button below:
        </p>
        <div style="margin: 30px 0;">
            <a href="{verification_url}" style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px;">
                Verify Email
            </a>
        </div>
        <p style="color: #999; font-size: 12px;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            {verification_url}
        </p>
        <p style="color: #999; font-size: 12px;">
            If you didn't register for an account, you can safely ignore this email.
        </p>
        <p style="color: #ccc; font-size: 11px; text-align: center; margin-top: 40px;">
            © 2025 {app_name}
        </p>
    </div>
    '''
    
    mail.send(msg)

def send_otp_sms(phone_number, otp):
    """Simulate sending OTP via SMS (in production, integrate with SMS service)"""
    # TODO: Replace with actual SMS service integration (e.g., Twilio, AWS SNS, etc.)
    # Example with Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=f"Your EcoFinds verification code is: {otp}",
    #     from_='+1234567890',  # Your Twilio number
    #     to=phone_number
    # )
    print(f"Sending OTP {otp} to {phone_number}")
    # For demo purposes, we'll just store it in memory
    otp_storage[phone_number] = otp
    return True

@auth_bp.route("/login", methods=["POST"])
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
        # Check if user has verified email and phone
        if not user.email_verified:
            return jsonify({"message": "Please verify your email address before logging in."}), 401
        if not user.phone_verified:
            return jsonify({"message": "Please verify your phone number before logging in."}), 401
            
        return jsonify({"token": user.get_auth_token(), "email": user.email, "role": user.roles[0].name, "id": user.id}), 200
    
    return jsonify({"message": "Incorrect Password"}), 401

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get('email')
    f_name = data.get('first_name')
    l_name = data.get('last_name', None)
    phone_number = data.get('phone_number', None)
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
    if not phone_number:
        missing_fields.append("phone_number")

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

    # Validate phone number
    if phone_number:
        # Simple validation - remove spaces, dashes, parentheses
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if len(clean_phone) < 10:
            return jsonify({"error": "Invalid phone number format"}), 400

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
                phone_number=phone_number,
                dob=dob,
                bio=bio,
                gender=gender
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Send email verification
            send_verification_email(user, user.user_detail)
            
            # Generate and send OTP for phone verification
            otp = ''.join(random.choices(string.digits, k=6))
            send_otp_sms(phone_number, otp)
        else:
            return jsonify({"message": "User Already Exists."}), 409
        db.session.commit()
        return jsonify({"message": "User Created. Please check your email and phone for verification instructions."}), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"message":str(e)}), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user's email address using token"""
    user = User.verify_reset_token(token, max_age=86400)  # 24 hours
    if not user:
        return jsonify({"msg": "Invalid or expired token"}), 400
    
    # Mark user as email verified
    user.email_verified = True
    db.session.commit()
    
    return jsonify({"msg": "Email verified successfully"}), 200

@auth_bp.route('/verify-phone', methods=['POST'])
def verify_phone():
    """Verify user's phone number using OTP"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    otp = data.get('otp')
    
    if not phone_number or not otp:
        return jsonify({"msg": "Phone number and OTP required"}), 400
    
    # Check if OTP matches
    stored_otp = otp_storage.get(phone_number)
    if not stored_otp or stored_otp != otp:
        return jsonify({"msg": "Invalid or expired OTP"}), 400
    
    # Remove used OTP
    if phone_number in otp_storage:
        del otp_storage[phone_number]
    
    # Mark user as phone verified
    user = UserDetail.query.filter_by(phone_number=phone_number).first()
    if user:
        user.user.email_verified = True
        user.user.phone_verified = True
        db.session.commit()
    
    return jsonify({"msg": "Phone verified successfully"}), 200

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to user's phone"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({"msg": "Phone number required"}), 400
    
    # Generate and send new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    # TODO: Add rate limiting to prevent abuse
    if send_otp_sms(phone_number, otp):
        return jsonify({"msg": "OTP resent successfully"}), 200
    else:
        return jsonify({"msg": "Failed to send OTP"}), 500

@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email required"}), 400

    user = datastore.find_user(email=email)
    if user:
        send_reset_email(user)
    return jsonify({"msg": "If registered, a reset link has been sent."}), 200

@auth_bp.route('/reset_password', methods=['POST'])
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