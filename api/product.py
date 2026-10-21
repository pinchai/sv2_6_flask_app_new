from api import api_bp
from flask import request, jsonify
from extensions import db
from models.product import Product
from models.category import Category
from models.brand import Brand
from helpers import UPLOAD_DIR, save_image
import os


@api_bp.get('/product')
@api_bp.get('/products')
def get_products():
    category_id = request.args.get('category_id')
    brand_id = request.args.get('brand_id')
    search = request.args.get('search') or request.args.get('q')

    query = Product.query

    if category_id and category_id.isdigit():
        query = query.filter_by(category_id=int(category_id))

    if brand_id and brand_id.isdigit():
        query = query.filter_by(brand_id=int(brand_id))

    if search:
        query = query.filter(Product.name.ilike(f"%{search.strip()}%"))

    products = query.all()
    return jsonify([p.to_dict() for p in products]), 200


@api_bp.get('/product/<int:product_id>')
@api_bp.get('/products/<int:product_id>')
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@api_bp.post('/product')
@api_bp.post('/products')
def create_product():
    data = request.get_json(silent=True) or request.form.to_dict()

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"error": "Product name is required"}), 400

    price_raw = data.get('price')
    if price_raw is None or str(price_raw).strip() == '':
        return jsonify({"error": "Product price is required"}), 400

    try:
        price = float(price_raw)
        if price < 0:
            return jsonify({"error": "Price must be non-negative"}), 400
    except ValueError:
        return jsonify({"error": "Invalid price format"}), 400

    description = data.get('description')

    # Category validation
    category_id = data.get('category_id')
    cat_val = None
    if category_id not in (None, '', 'null'):
        try:
            cat_val = int(category_id)
            if not db.session.get(Category, cat_val):
                return jsonify({"error": f"Category with id {cat_val} does not exist"}), 400
        except ValueError:
            return jsonify({"error": "category_id must be an integer"}), 400

    # Brand validation
    brand_id = data.get('brand_id')
    brand_val = None
    if brand_id not in (None, '', 'null'):
        try:
            brand_val = int(brand_id)
            if not db.session.get(Brand, brand_val):
                return jsonify({"error": f"Brand with id {brand_val} does not exist"}), 400
        except ValueError:
            return jsonify({"error": "brand_id must be an integer"}), 400

    # Handle optional image file
    file = request.files.get('image')
    filename = save_image(file)

    product = Product(
        name=name,
        price=price,
        description=description,
        image=filename,
        category_id=cat_val,
        brand_id=brand_val
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "product": product.to_dict()
    }), 201


@api_bp.route('/product/<int:product_id>', methods=['PUT', 'PATCH'])
@api_bp.route('/products/<int:product_id>', methods=['PUT', 'PATCH'])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True) or request.form.to_dict()

    if 'name' in data:
        name = str(data['name']).strip()
        if not name:
            return jsonify({"error": "Product name cannot be empty"}), 400
        product.name = name

    if 'price' in data:
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({"error": "Price must be non-negative"}), 400
            product.price = price
        except ValueError:
            return jsonify({"error": "Invalid price format"}), 400

    if 'description' in data:
        product.description = data['description']

    if 'category_id' in data:
        cat_id = data['category_id']
        if cat_id in (None, '', 'null'):
            product.category_id = None
        else:
            try:
                c_val = int(cat_id)
                if not db.session.get(Category, c_val):
                    return jsonify({"error": f"Category with id {c_val} does not exist"}), 400
                product.category_id = c_val
            except ValueError:
                return jsonify({"error": "category_id must be an integer"}), 400

    if 'brand_id' in data:
        b_id = data['brand_id']
        if b_id in (None, '', 'null'):
            product.brand_id = None
        else:
            try:
                br_val = int(b_id)
                if not db.session.get(Brand, br_val):
                    return jsonify({"error": f"Brand with id {br_val} does not exist"}), 400
                product.brand_id = br_val
            except ValueError:
                return jsonify({"error": "brand_id must be an integer"}), 400

    # Handle image upload if provided
    file = request.files.get('image')
    new_filename = save_image(file)
    if new_filename:
        if product.image:
            old_path = os.path.join(UPLOAD_DIR, product.image)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        product.image = new_filename

    db.session.commit()

    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict()
    }), 200


@api_bp.delete('/product/<int:product_id>')
@api_bp.delete('/products/<int:product_id>')
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if product.image:
        old_path = os.path.join(UPLOAD_DIR, product.image)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"Product {product_id} deleted successfully"}), 200
