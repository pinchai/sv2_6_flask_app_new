from admin import admin_bp
from flask import render_template
from admin.auth import login_required
from sqlalchemy import text
from extensions import db

from werkzeug.security import generate_password_hash
from flask import request, redirect, url_for
from models.user import User
from werkzeug.utils import secure_filename
import os
from helpers import allowed, UPLOAD_DIR


@admin_bp.get('/user')
@login_required
def user():
    module = 'user'
    sql = text("SELECT * FROM user")
    result = db.session.execute(sql)
    rows = [dict(row._mapping) for row in result]

    return render_template(
        'admin/user/index.html',
        module=module,
        users=rows
    )


@admin_bp.get('/user/add')
@login_required
def add_user():
    module = 'user'
    return render_template('admin/user/add.html', module=module)


@admin_bp.post('/user/add')
@login_required
def do_add_user():
    form = request.form
    file = request.files["image"]
    if file and allowed(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_DIR, filename))

    password = generate_password_hash(form.get('password'))
    user = User(
        username=form.get('username'),
        email=form.get('email'),
        password=password,
        profile=filename,
        role=form.get('role')
    )
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('admin_bp.user'))


@admin_bp.get('/user/edit/<int:user_id>')
@login_required
def edit_user(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('admin_bp.user'))
    return render_template(
        'admin/user/edit.html',
        module=module,
        user=user
    )


@admin_bp.post('/user/edit')
@login_required
def do_edit_user():
    module = 'user'
    form = request.form

    user = User.query.get(form.get('user_id'))

    user.username = form.get('username')
    user.email = form.get('email')
    user.profile = 'new profile'
    user.role = form.get('role')
    if form.get('password') is not None and form.get('password') != '':
        user.password = generate_password_hash(form.get('password'))
    db.session.commit()

    return redirect(url_for('admin_bp.user'))


@admin_bp.get('/user/confirm-delete/<int:user_id>')
@login_required
def confirm_delete(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('admin_bp.user'))
    return render_template(
        'admin/user/confirm_delete.html',
        module=module,
        user=user

    )


@admin_bp.post('/user/delete')
@login_required
def delete_user():
    module = 'user'
    form = request.form
    user_id = form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('admin_bp.user'))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_bp.user'))
