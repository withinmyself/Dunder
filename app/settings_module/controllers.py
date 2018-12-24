from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify
from flask_login import login_required

from app import db, redis_server
from app.users_module.models import Ignore, Favorites
from app.users_module.controllers import login_manager, current_user
from app.settings_module.settings_functions import *
from app.search_module.search_functions import random_genre
from app.search_module.models import Albums

settings_routes = Blueprint('settings', __name__, url_prefix='/settings')

# Routes for our search engine

# Main search page
@login_required
@settings_routes.route('/', methods=['GET', 'POST'])
def settings():
    if request.method == 'GET':
        return render_template('settings/settings.html', redis=redis_server)
    else:
        pass

@login_required
@settings_routes.route('/criteria', methods=['GET', 'POST'])
def criteria():
    change_max_views(request.form['views'])
    change_comments_needed(request.form['comments'])
    change_like_ratio(request.form['likeratio'])
    change_view_ratio(request.form['view_ratio'])
    return render_template('search/dunderbands.html')


@login_required
@settings_routes.route('/make_favorite/', methods=['POST'])
def make_favorite():
    # Declare all variables
    stayOrGo = request.form['stayOrGo']
    videoId = request.form['videoId']
    videoTitle = request.form['videoTitle']
    currentBand = db.session.query(Albums).filter_by(videoId=videoId).first()

    # Decide to add or delete
    if stayOrGo == 'stay':
        if db.session.query(Favorites).filter_by(videoId=videoId).first() == None:
            fav = Favorites(videoId, videoTitle=videoTitle)
            db.session.add(fav)
        else:
            # Check the current users relationship favorites for album
            for favorite in current_user.favorites:
                if favorite.videoId == videoId:
                    flash('Album Already Favorite')
                    return render_template('search/results.html',
                            currentBand      = currentBand,
                            publishedBefore  = request.form['publishedBefore'],
                            publishedAfter   = request.form['publishedAfter'])
                else:
                    continue
        # Need to append a new Favorite object
        # to the current_user's favorites
        fav = db.session.query(Favorites).filter_by(videoId=videoId).first()
        current_user.favorites.append(fav)
        db.session.commit()

    else:
        pass

    # This will only delete the relational data.  Not the database data.
    if stayOrGo == 'go':
        for favorite in current_user.favorites:
            if favorite.videoId == videoId:
                current_user.favorites.remove(favorite)
                db.session.commit()
                return redirect('search/results.html',
                    currentBand     = currentBand,
                    publishedBefore = request.form['publishedBefore'],
                    publishedAfter  = request.form['publishedAfter'])
            else:
                pass
        flash("Album Does Not Exist In Your Favorites")
    else:
        pass

    return render_template('search/results.html',
                    currentBand     = currentBand,
                    publishedBefore = request.form['publishedBefore'],
                    publishedAfter  = request.form['publishedAfter'])

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

@settings_routes.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('info/about.html')

@login_required
@settings_routes.route('/favorites/', methods=['GET', 'POST'])
def favorites():
    if request.method == 'GET':
        for favorite in current_user.favorites:
            first_video = favorite.videoId
            return render_template('info/favorites.html',
                              first_video  = first_video,
                              current_user = current_user)
    if request.method == 'POST':
        first_video = request.form['videoId']
        return render_template('info/favorites.html',
                                first_video  = first_video,
                                current_user = current_user)
    return render_template('info/favorites.html',
                           current_user = current_user)

