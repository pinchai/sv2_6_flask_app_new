from admin import admin_bp
from flask import render_template, request, redirect, url_for
from admin.auth import login_required
from extensions import db
from models.category import Category
import os
from helpers import UPLOAD_DIR, save_image


@admin_bp.get('/category')
@login_required
def category():
    module = 'category'
    categories = Category.query.all()
    return render_template(
        'admin/category/index.html',
        module=module,
        categories=categories
    )


@admin_bp.get('/category/add')
@login_required
def add_category():
    module = 'category'
    return render_template('admin/category/add.html', module=module)


@admin_bp.post('/category/add')
@login_required
def do_add_category():
    form = request.form
    file = request.files.get("image")
    filename = save_image(file)

    category_obj = Category(
        name=form.get('name'),
        description=form.get('description'),
        image=filename
    )
    db.session.add(category_obj)
    db.session.commit()

    return redirect(url_for('admin_bp.category'))


@admin_bp.get('/category/edit/<int:category_id>')
@login_required
def edit_category(category_id):
    module = 'category'
    category_obj = db.session.get(Category, category_id)
    if not category_obj:
        return redirect(url_for('admin_bp.category'))
    return render_template(
        'admin/category/edit.html',
        module=module,
        category=category_obj
    )


@admin_bp.post('/category/edit')
@login_required
def do_edit_category():
    form = request.form
    category_id = form.get('category_id')
    category_obj = db.session.get(Category, category_id)
    if not category_obj:
        return redirect(url_for('admin_bp.category'))

    category_obj.name = form.get('name')
    category_obj.description = form.get('description')

    file = request.files.get("image")
    new_filename = save_image(file)
    if new_filename:
        if category_obj.image:
            old_path = os.path.join(UPLOAD_DIR, category_obj.image)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        category_obj.image = new_filename

    db.session.commit()
    return redirect(url_for('admin_bp.category'))


@admin_bp.get('/category/confirm-delete/<int:category_id>')
@login_required
def confirm_delete_category(category_id):
    module = 'category'
    category_obj = db.session.get(Category, category_id)
    if not category_obj:
        return redirect(url_for('admin_bp.category'))
    return render_template(
        'admin/category/confirm_delete.html',
        module=module,
        category=category_obj
    )


@admin_bp.post('/category/delete')
@login_required
def delete_category():
    form = request.form
    category_id = form.get('category_id')
    category_obj = db.session.get(Category, category_id)
    if not category_obj:
        return redirect(url_for('admin_bp.category'))

    if category_obj.image:
        old_path = os.path.join(UPLOAD_DIR, category_obj.image)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(category_obj)
    db.session.commit()
    return redirect(url_for('admin_bp.category'))
