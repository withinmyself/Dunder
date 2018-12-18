
import redis

from flask import Flask, render_template

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

redis_server = redis.Redis(host='127.0.0.1', port='6379')



# Import a module / component using its blueprint handler variable (mod_auth)
from app.search_module.controllers import search_blueprint as search_bp
from app.settings_module.controllers import settings_blueprint as settings_bp

# Register blueprint(s)
app.register_blueprint(search_bp)
app.register_blueprint(settings_bp)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
db.create_all()
