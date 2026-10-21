from admin import admin_bp
from flask import render_template, request, redirect, url_for
from admin.auth import login_required
from extensions import db
from models.brand import Brand
import os
from helpers import UPLOAD_DIR, save_image


@admin_bp.get('/brand')
@login_required
def brand():
    module = 'brand'
    brands = Brand.query.all()
    return render_template(
        'admin/brand/index.html',
        module=module,
        brands=brands
    )


@admin_bp.get('/brand/add')
@login_required
def add_brand():
    module = 'brand'
    return render_template('admin/brand/add.html', module=module)


@admin_bp.post('/brand/add')
@login_required
def do_add_brand():
    form = request.form
    file = request.files.get("image")
    filename = save_image(file)

    brand = Brand(
        name=form.get('name'),
        description=form.get('description'),
        image=filename
    )
    db.session.add(brand)
    db.session.commit()

    return redirect(url_for('admin_bp.brand'))


@admin_bp.get('/brand/edit/<int:brand_id>')
@login_required
def edit_brand(brand_id):
    module = 'brand'
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return redirect(url_for('admin_bp.brand'))
    return render_template(
        'admin/brand/edit.html',
        module=module,
        brand=brand
    )


@admin_bp.post('/brand/edit')
@login_required
def do_edit_brand():
    form = request.form
    brand_id = form.get('brand_id')
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return redirect(url_for('admin_bp.brand'))

    brand.name = form.get('name')
    brand.description = form.get('description')

    file = request.files.get("image")
    new_filename = save_image(file)
    if new_filename:
        if brand.image:
            old_path = os.path.join(UPLOAD_DIR, brand.image)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        brand.image = new_filename

    db.session.commit()
    return redirect(url_for('admin_bp.brand'))


@admin_bp.get('/brand/confirm-delete/<int:brand_id>')
@login_required
def confirm_delete_brand(brand_id):
    module = 'brand'
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return redirect(url_for('admin_bp.brand'))
    return render_template(
        'admin/brand/confirm_delete.html',
        module=module,
        brand=brand
    )


@admin_bp.post('/brand/delete')
@login_required
def delete_brand():
    form = request.form
    brand_id = form.get('brand_id')
    brand = db.session.get(Brand, brand_id)
    if not brand:
        return redirect(url_for('admin_bp.brand'))

    if brand.image:
        old_path = os.path.join(UPLOAD_DIR, brand.image)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(brand)
    db.session.commit()
    return redirect(url_for('admin_bp.brand'))
