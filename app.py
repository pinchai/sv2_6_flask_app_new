from flask import Flask, render_template

from config import Config
from extensions import db, migrate, limiter, csrf, core

from front import front_bp
from admin import admin_bp
from api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
limiter.init_app(app)
csrf.init_app(app)
core.init_app(app, resources={
    r"/api/*": {"origins": "http://localhost:4200"}
})
app.register_blueprint(front_bp, url_prefix="/")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(api_bp, url_prefix="/api")
csrf.exempt(api_bp)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.errorhandler(429)
def to_many_requests(e):
    return render_template('error/429.html'), 429


@app.errorhandler(500)
def server_error(e):
    return render_template('error/500.html'), 500


# load model

import models

if __name__ == '__main__':
    app.run()
