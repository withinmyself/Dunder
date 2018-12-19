from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import db, redis_server
from app.settings_module.models import Ignore, Favorites
from app.settings_module.settings_functions import *
from app.search_module.search_functions import random_genre
from app.search_module.models import Albums

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
    stayOrGo = request.form['stayOrGo']
    videoId = request.form['videoId']
    if stayOrGo == 'stay':
        videoTitle = request.form['videoTitle']
        if db.session.query(Favorites).filter_by(videoId=videoId).first() == None:
            add_favorite(videoId, videoTitle=videoTitle)
        else:
            flash('Album Already Favorite')
    if stayOrGo == 'go':
        if db.session.query(Favorites).filter_by(videoId=videoId).first() != None:
            delete_favorite(videoId)
        else:
            flash('Album Already Gone')
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

@settings_routes.route('/make_ignore/', methods=['GET', 'POST'])
def make_ignore():
    videoId = request.form['videoId']
    videoTitle = request.form['videoTitle']
    stayOrGo = request.form['stayOrGo']
    if stayOrGo == 'stay':
        if db.session.query(Ignore).filter_by(videoId=videoId).first() == None:
            add_ignore(videoId, videoTitle)
        else:
            flash('Video Already Being Ignored')
    if stayOrGo == 'go':
        if db.session.query(Ignore).filter_by(videoId=videoId).first() != None:
            delete_ignore(videoId)
        else:
            flash('Video Already Deleted From Ignore List')
    dunderRandom = random_genre()
    return render_template('search/dunderbands.html', dunderRandom = dunderRandom) 
