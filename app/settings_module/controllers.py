from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from app import db
from app.settings_module.models import Ignore, Favorites
from app.settings_module.settings_functions import *

settings_blueprint = Blueprint('settings', __name__, url_prefix='/settings')

# Routes for our search engine

# Main search page
@settings_blueprint.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings/settings.html')
    else:
        pass

