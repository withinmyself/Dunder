from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import db, redis_server
from app.settings_module.models import Ignore, Favorites
from app.settings_module.settings_functions import *

settings_routes = Blueprint('settings', __name__, url_prefix='/settings')

# Routes for our search engine

# Main search page
@settings_routes.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings/settings.html', redis=redis_server)
    else:
        pass


@settings_routes.route('/criteria', methods=['GET', 'POST'])
def criteria():
    change_max_views(request.form['views'])
    change_comments_needed(request.form['comments'])
    change_like_ratio(request.form['likeratio'])
    return render_template('settings/settings.html', redis=redis_server)



@settings_routes.route('/make_favorite/', methods=['POST'])
def make_favorite():
    videoId = request.form['videoId']
    add_favorite(videoId)
    currentBand = db.session.query(Albums).filter_by(videoId=videoId).first()
    return render_template('search/results.html',
                    videoId=currentBand.videoId,
                    nextToken = currentBand.nextToken,
                    genre=currentBand.genre,
                    videoTitle=currentBand.videoTitle,
                    commentPlug=currentBand.topComment,
                    isFavorite=currentBand.isFavorite,
                    publishedBefore=request.form['publishedBefore'],
                    publishedAfter=request.form['publishedAfter'])
