from flask import Flask

from config import Config
from extensions import db, migrate

from front import front_bp
from admin import admin_bp
from api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(front_bp, url_prefix="/")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(api_bp, url_prefix="/api")

# load model

import models

if __name__ == '__main__':
    app.run()
