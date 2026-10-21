from admin import admin_bp
from flask import render_template, request, redirect, url_for
from admin.auth import login_required
from extensions import db
from models.product import Product
from models.category import Category
from models.brand import Brand
import os
from helpers import UPLOAD_DIR, save_image


@admin_bp.get('/product')
@login_required
def product():
    module = 'product'
    products = Product.query.all()
    return render_template(
        'admin/product/index.html',
        module=module,
        products=products
    )


@admin_bp.get('/product/add')
@login_required
def add_product():
    module = 'product'
    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template(
        'admin/product/add.html',
        module=module,
        categories=categories,
        brands=brands
    )


@admin_bp.post('/product/add')
@login_required
def do_add_product():
    form = request.form
    file = request.files.get("image")
    filename = save_image(file)

    category_id = form.get('category_id')
    brand_id = form.get('brand_id')

    try:
        price = float(form.get('price', 0.0) or 0.0)
    except ValueError:
        price = 0.0

    product_obj = Product(
        name=form.get('name'),
        price=price,
        description=form.get('description'),
        image=filename,
        category_id=int(category_id) if category_id and category_id.isdigit() else None,
        brand_id=int(brand_id) if brand_id and brand_id.isdigit() else None
    )
    db.session.add(product_obj)
    db.session.commit()

    return redirect(url_for('admin_bp.product'))


@admin_bp.get('/product/edit/<int:product_id>')
@login_required
def edit_product(product_id):
    module = 'product'
    product_obj = db.session.get(Product, product_id)
    if not product_obj:
        return redirect(url_for('admin_bp.product'))

    categories = Category.query.all()
    brands = Brand.query.all()
    return render_template(
        'admin/product/edit.html',
        module=module,
        product=product_obj,
        categories=categories,
        brands=brands
    )


@admin_bp.post('/product/edit')
@login_required
def do_edit_product():
    form = request.form
    product_id = form.get('product_id')
    product_obj = db.session.get(Product, product_id)
    if not product_obj:
        return redirect(url_for('admin_bp.product'))

    product_obj.name = form.get('name')
    try:
        product_obj.price = float(form.get('price', 0.0) or 0.0)
    except ValueError:
        product_obj.price = 0.0

    product_obj.description = form.get('description')

    category_id = form.get('category_id')
    brand_id = form.get('brand_id')
    product_obj.category_id = int(category_id) if category_id and category_id.isdigit() else None
    product_obj.brand_id = int(brand_id) if brand_id and brand_id.isdigit() else None

    file = request.files.get("image")
    new_filename = save_image(file)
    if new_filename:
        if product_obj.image:
            old_path = os.path.join(UPLOAD_DIR, product_obj.image)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        product_obj.image = new_filename

    db.session.commit()
    return redirect(url_for('admin_bp.product'))


@admin_bp.get('/product/confirm-delete/<int:product_id>')
@login_required
def confirm_delete_product(product_id):
    module = 'product'
    product_obj = db.session.get(Product, product_id)
    if not product_obj:
        return redirect(url_for('admin_bp.product'))
    return render_template(
        'admin/product/confirm_delete.html',
        module=module,
        product=product_obj
    )


@admin_bp.post('/product/delete')
@login_required
def delete_product():
    form = request.form
    product_id = form.get('product_id')
    product_obj = db.session.get(Product, product_id)
    if not product_obj:
        return redirect(url_for('admin_bp.product'))

    if product_obj.image:
        old_path = os.path.join(UPLOAD_DIR, product_obj.image)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(product_obj)
    db.session.commit()
    return redirect(url_for('admin_bp.product'))
