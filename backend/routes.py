from flask import current_app as app, request, jsonify, make_response
from flask_security import auth_required, hash_password, verify_password
from flask_security.recoverable import reset_password_token_status, send_reset_password_instructions
from backend.models import *
from flask_mail import Message, Mail

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