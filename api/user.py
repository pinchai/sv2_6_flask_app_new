from api import api_bp
from flask import request, jsonify
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash
from helpers import UPLOAD_DIR, save_image
import os


@api_bp.get('/user')
@api_bp.get('/users')
def get_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@api_bp.get('/user/<int:user_id>')
@api_bp.get('/users/<int:user_id>')
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@api_bp.post('/user')
@api_bp.post('/users')
def create_user():
    data = request.get_json(silent=True) or request.form.to_dict()

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    # Check for existing email or username
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    # Handle image upload if provided
    file = request.files.get('image')
    filename = save_image(file)

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        profile=filename,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": new_user.to_dict()
    }), 201


@api_bp.route('/user/<int:user_id>', methods=['PUT', 'PATCH'])
@api_bp.route('/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or request.form.to_dict()

    # Check email uniqueness if changing email
    if 'email' in data:
        email = data['email'].strip()
        if email and email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                return jsonify({"error": "Email already exists"}), 400
            user.email = email

    # Check username uniqueness if changing username
    if 'username' in data:
        username = data['username'].strip()
        if username and username != user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                return jsonify({"error": "Username already exists"}), 400
            user.username = username

    if 'role' in data and data['role']:
        user.role = data['role']

    if data.get('password') and str(data['password']).strip():
        user.password = generate_password_hash(str(data['password']).strip())

    # Handle image update if file uploaded
    file = request.files.get('image')
    new_filename = save_image(file)
    if new_filename:
        if user.profile:
            old_path = os.path.join(UPLOAD_DIR, user.profile)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        user.profile = new_filename

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    }), 200


@api_bp.delete('/user/<int:user_id>')
@api_bp.delete('/users/<int:user_id>')
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.profile:
        old_path = os.path.join(UPLOAD_DIR, user.profile)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {user_id} deleted successfully"}), 200
