from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import db, redis_server
from app.settings_module.models import Ignore, Favorites
from app.settings_module.settings_functions import *

settings_blueprint = Blueprint('settings', __name__, url_prefix='/settings')

# Routes for our search engine

# Main search page
@settings_blueprint.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings/settings.html', redis=redis_server)
    else:
        pass


@settings_blueprint.route('/criteria', methods=['GET', 'POST'])
def criteria():
    change_max_views(request.form['views'])
    change_comments_needed(request.form['comments'])
    change_like_ratio(request.form['likeratio'])
    return render_template('settings/settings.html', redis=redis_server)
