from admin import admin_bp
from flask import render_template
from admin.auth import login_required
from extensions import db
from models.user import User
from models.product import Product
from models.category import Category
from models.brand import Brand
from sqlalchemy import func


@admin_bp.get('/dashboard')
@login_required
def dashboard():
    module = 'dashboard'

    user_count = User.query.count()
    product_count = Product.query.count()
    category_count = Category.query.count()
    brand_count = Brand.query.count()

    total_inventory = db.session.query(func.sum(Product.price)).scalar() or 0.0
    avg_price = db.session.query(func.avg(Product.price)).scalar() or 0.0

    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()

    stats = {
        'users': user_count,
        'products': product_count,
        'categories': category_count,
        'brands': brand_count,
        'total_inventory': total_inventory,
        'avg_price': avg_price
    }

    return render_template(
        'admin/dashboard/index.html',
        module=module,
        stats=stats,
        recent_products=recent_products,
        recent_users=recent_users
    )
