from admin import admin_bp
from flask import render_template
from flask import session, redirect, request, url_for
from werkzeug.security import check_password_hash
from  extensions import db
from sqlalchemy import text
from functools import wraps


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_login"):
            return redirect(url_for("admin_bp.admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped

@admin_bp.get('/login')
def admin_login():
    module = 'login'
    session.clear()
    return render_template('admin/login.html')


@admin_bp.post('/login')
def admin_do_login():
    module = 'login'
    form = request.form
    username = form.get('username').strip()
    password = form.get('password')

    sql = text("SELECT * FROM user WHERE username = :username")
    user = db.session.execute(sql, {"username": username}).fetchone()

    if user:
        # check password
        if check_password_hash(user[4], password):
            session.clear()
            session['is_login'] = True
            session['user_id'] = user[0]
            session['profile'] = user[1]
            session['username'] = user[2]
            session['email'] = user[3]
            return redirect(url_for('admin_bp.dashboard'))
    else:
        return redirect(url_for('admin_bp.admin_login'))

    return redirect(url_for('admin_bp.dashboard'))


@admin_bp.get('/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_bp.admin_login'))