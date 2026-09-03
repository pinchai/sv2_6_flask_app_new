from front import front_bp
from flask import render_template

@front_bp.get('/account')
def account():
    return render_template('front/account.html')


@front_bp.get('/forgot-password')
def forgot_password():
    return render_template('front/forgot-password.html')


@front_bp.get('/login')
def login():
    return render_template('front/login.html')


@front_bp.get('/create-user')
def create_user():
    return render_template('front/create-user.html')