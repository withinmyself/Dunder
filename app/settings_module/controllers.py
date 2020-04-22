from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify
from app import db, redis_server, login_manager
from app.users_module.models import Ignore, Favorites
from app.users_module.controllers import current_user
from app.settings_module.settings_functions import Criteria
from app.search_module.models import Albums

settings_routes = Blueprint('settings', __name__, url_prefix='/settings')
settings = Criteria()

@settings_routes.route('/', methods=['GET'])
def settings():
    if current_user.is_authenticated:
        return render_template('settings/settings.html', redis_server=redis_server)
    else:
        flash("You Still Need To Login First")
        return redirect('users/login')

@settings_routes.route('/criteria', methods=['GET', 'POST'])
def criteria():
    if current_user.is_authenticated:
        if current_user.username == str(redis_server.get('USERNAME').decode('utf-8')):
            settings.change_max_views(request.form['views'])
            settings.change_comments_needed(request.form['comments'])
            settings.change_like_ratio(request.form['likeratio'])
            settings.change_view_ratio(request.form['view_ratio'])
            return redirect('search/dunderbands')
        else:
            flash("Admin Access Only")
            return redirect('users/login')
    else:
        flash("Admin Access Only")
        return redirect('users/login')


@settings_routes.route('/make_favorite/', methods=['POST'])
def make_favorite():
    if current_user.is_authenticated:
        stayOrGo = request.form['stayOrGo']
        videoId = request.form['videoId']
        videoTitle = request.form['videoTitle']
        currentBand = db.session.query(Albums).filter_by(videoId=videoId).first()

        # Decide to add or delete
        if stayOrGo == 'stay':
            if db.session.query(Favorites).filter_by(videoId=videoId).first() == None:
                fav = Favorites(videoId, videoTitle=videoTitle)
                fav.videoComments = request.form['topComment']
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

            fav = db.session.query(Favorites).filter_by(videoId=videoId).first()
            current_user.favorites.append(fav)
            db.session.commit()
        else:
            pass
    else:
        flash("You Need To Login First")
        return redirect('users/login')

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
    if current_user.is_authenticated:
        videoId = request.form['videoId']
        videoTitle = request.form['videoTitle']
        stayOrGo = request.form['stayOrGo']
        if stayOrGo == 'stay':
            if db.session.query(Ignore).filter_by(videoId=videoId).first() == None:
                ignore = Ignore(videoId, videoTitle)
                db.session.add(ignore)
            else:
                for ignore in current_user.ignore:
                    if ignore.videoId == videoId:
                        flash('Video Already Being Ignored')
                        return redirect('search/dunderbands')

            ignore = db.session.query(Ignore).filter_by(videoId=videoId).first()
            current_user.ignore.append(ignore)
            db.session.commit()
    else:
        flash("You Need To Login First")
        return redirect('users/login')
    if stayOrGo == 'go':
        for nore in current_user.ignore:
            if nore.videoId == videoId:
                current_user.ignore.remove(nore)
                db.session.commit()
                return redirect('search/dunderbands')
        flash('Video Already Deleted From Ignore List')

    return redirect('search/dunderbands')

@settings_routes.route('/about/', methods=['GET', 'POST'])
def about():
    return render_template('info/about.html')

@settings_routes.route('/faq/', methods=['GET'])
def faq():
    return render_template('info/faq.html')

@settings_routes.route('/favorites/', methods=['GET', 'POST'])
def favorites():
    if current_user.is_authenticated and request.method == 'GET':
        for favorite in current_user.favorites:
            first_video   = favorite.videoId
            first_comment = favorite.videoComments
            return render_template('info/favorites.html',
                first_video   = first_video,
                first_comment = first_comment,
                current_user = current_user)
    
    if current_user.is_authenticated and request.method == 'POST':
        first_video   = request.form['videoId']
        first_comment = request.form['videoComments']
        return render_template('info/favorites.html',
            first_video   = first_video,
            first_comment = first_comment,
            current_user  = current_user)
    flash("You Need To Login First")
    return redirect('users/login')
