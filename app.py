from flask import Flask, render_template, redirect, url_for, request, session
from product import products as pro, get_product_by_category
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydb.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-this"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=1440)  # session TTL

UPLOAD_DIR = os.path.join("static", "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}


def allowed(name):
    return "." in name and name.rsplit(".", 1)[-1].lower() in ALLOWED_EXT


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.String(80), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(120), nullable=False, default='admin')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_login"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.get('/')
def home():
    return render_template('front/index.html', products=pro)


@app.get('/products')
def products():
    return render_template('front/products.html', products=pro)


@app.get('/product/<product_name>')
def product(product_name):
    from product import get_product_by_title
    product = get_product_by_title(product_name)
    related_product = get_product_by_category(product['category'])
    return render_template(
        'front/product.html',
        product=product,
        related_product=related_product,
    )


@app.get('/cart')
def cart():
    return render_template('front/cart.html')


@app.get('/account')
def account():
    return render_template('front/account.html')


@app.get('/forgot-password')
def forgot_password():
    return render_template('front/forgot-password.html')


@app.get('/login')
def login():
    return render_template('front/login.html')


@app.get('/create-user')
def create_user():
    return render_template('front/create-user.html')


@app.get('/checkout')
def checkout():
    return render_template('front/checkout.html')


@app.get('/admin/dashboard')
@login_required
def dashboard():
    module = 'dashboard'
    return render_template('admin/dashboard/index.html', module=module)


@app.get('/admin/user')
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


@app.get('/admin/user/add')
@login_required
def add_user():
    module = 'user'
    return render_template('admin/user/add.html', module=module)


@app.post('/admin/user/add')
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

    return redirect(url_for('user'))


@app.get('/admin/user/edit/<int:user_id>')
@login_required
def edit_user(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('user'))
    return render_template(
        'admin/user/edit.html',
        module=module,
        user=user
    )


@app.post('/admin/user/edit')
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

    return redirect(url_for('user'))


@app.get('/admin/user/confirm-delete/<int:user_id>')
@login_required
def confirm_delete(user_id):
    module = 'user'
    sql = text("SELECT * FROM user WHERE id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    user = None
    if result:
        user = dict(result._mapping)
    else:
        return redirect(url_for('user'))
    return render_template(
        'admin/user/confirm_delete.html',
        module=module,
        user=user

    )


@app.post('/admin/user/delete')
@login_required
def delete_user():
    module = 'user'
    form = request.form
    user_id = form.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('user'))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user'))


@app.get('/admin/login')
def admin_login():
    module = 'login'
    return render_template('admin/login.html')


@app.post('/admin/login')
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
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('admin_login'))

    return redirect(url_for('dashboard'))


# @app.before_request
# def before_request():
#     path = request.path
#     if 'admin' in path:
#         if session.get('is_login'):
#             return redirect(url_for('dashboard'))
#         else:
#             return redirect(url_for('admin_login'))
#     return None


if __name__ == '__main__':
    app.run()
