from api import api_bp
from flask import request, jsonify
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import UPLOAD_DIR, save_image
import os
from sqlalchemy import text

from flask_jwt_extended import (JWTManager, create_access_token)



@api_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    sql = text("SELECT * FROM user WHERE username = :username")
    user = db.session.execute(sql, {"username": username}).fetchone()

    if user:
        if check_password_hash(user[4], password):
            access = create_access_token(identity=username)
            return jsonify(access_token=access)
        else:
            return jsonify({"message": "Incorrect username or password"}), 401
    else:
        return jsonify({"message": "Invalid username or password"}), 401