from flask import Blueprint, request, jsonify
from flask_security import verify_password, hash_password
from flask_security.utils import login_user, logout_user
from models.models import db, User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # user by email
    user = User.query.filter_by(email=email).first()

    # password
    if user and verify_password(password, user.password):
        login_user(user) # Creates session/token context
        
        role = user.roles[0].name if user.roles else 'user'
        
        return jsonify({
            'message': 'Login successful',
            'token': user.fs_uniquifier, # used as token identifier
            'email': user.email,
            'role': role
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    # Default new users to 'user' role
    user_role = Role.query.filter_by(name='user').first()
    
    new_user = User(
        email=email,
        username=username,
        password=hash_password(password),
        active=True,
        fs_uniquifier=email # using email as unique ID
    )
    
    if user_role:
        new_user.roles.append(user_role)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['POST'])
def get_profile():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    role = user.roles[0].name if user.roles else 'user'

    return jsonify({
        'email': user.email,
        'username': user.username,
        'role': role
    }), 200


@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if username:
        user.username = username

    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200


@auth_bp.route('/profile/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not (email and current_password and new_password):
        return jsonify({'message': 'Missing required fields'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not verify_password(current_password, user.password):
        return jsonify({'message': 'Current password is incorrect'}), 400

    user.password = hash_password(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200