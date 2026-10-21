from admin import admin_bp
from flask import render_template, request, redirect, url_for, session
from admin.auth import login_required
from sqlalchemy import text
from extensions import db
from werkzeug.security import generate_password_hash
from models.user import User
import os
from helpers import allowed, UPLOAD_DIR, save_image


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
    file = request.files.get("image")
    filename = save_image(file)

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

    user_id = form.get('user_id')
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('admin_bp.user'))

    user.username = form.get('username')
    user.email = form.get('email')
    user.role = form.get('role')

    file = request.files.get("image")
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

    password = form.get('password')
    if password is not None and password.strip() != '':
        user.password = generate_password_hash(password)

    db.session.commit()

    if session.get('user_id') == user.id:
        session['profile'] = user.profile
        session['username'] = user.username
        session['email'] = user.email
        session['role'] = user.role

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
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for('admin_bp.user'))

    if user.profile:
        old_path = os.path.join(UPLOAD_DIR, user.profile)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_bp.user'))
