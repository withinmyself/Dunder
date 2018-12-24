import os

import redis

from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_bootstrap import Bootstrap


app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

Bootstrap(app)


if os.getenv('REDISTOGO_URL') == None:
    redis_server = redis.Redis(host='0.0.0.0', port='6379')
else:
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    redis_server = redis.from_url(redis_url)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

# Import a module / component using its blueprint handler variable (mod_auth)
from app.search_module.controllers import search_routes as search_bp
from app.settings_module.controllers import settings_routes as settings_bp
from app.users_module.controllers import users_routes as users_bp
# Register blueprint(s)
app.register_blueprint(search_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(users_bp)

# Build the database:
db.create_all()
