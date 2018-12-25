from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from app.users_module.controllers import current_user
from flask_login import login_required

import asyncio


from app import db, redis_server, login_manager
from app.users_module.controllers import load_user
from app.users_module.models import Favorites
from app.search_module.models import Albums
from app.search_module.search_functions import criteria_crunch, \
     string_clean, random_genre, no_word_string

search_routes = Blueprint('search', __name__, url_prefix='/search')

# Routes for our search engine

# Main search page
@search_routes.route('/', methods=['GET'])
def index():
   return redirect('search/dunderbands')

@login_required
@search_routes.route('/dunderbands', methods=['GET', 'POST'])
def dunderbands():
    if request.method == 'GET':
        db.session.query(Albums).delete()
        db.session.query(Favorites).filter_by(videoTitle='Not Given').delete()
        db.session.commit()
        if current_user.is_authenticated:
            redis_server.set('AROUND', 0)
            return render_template('search/dunderbands.html',
                                   current_user=current_user)
        else:
            flash("You Need To Login First - Click Signup If You Don't Have A Username Yet")
            return redirect('users/login')
    else:
        if current_user.is_authenticated:
            try:
                dunderAnchor = request.form['videoId']
            except KeyError:
                dunderAnchor = None
            try:
                prefix           = request.form['prefix']
                subgenre         = request.form['subgenre']
                genre            = request.form['genre']
                country          = request.form['country']
                redis_server.set('PREFIX', len(prefix))
                redis_server.set('SUBGENRE', len(subgenre))
                redis_server.set('COUNTRY', len(country))
                dunderRequest    = '{0:s} {1:s} {2:s} {3:s}'.format(
                                    prefix, subgenre, genre, country)
            except KeyError:
                dunderRequest    = request.form['dunderRequest']
            dunderSearch         = string_clean(dunderRequest, 'stringNeededUpper')
            publishedBefore      = request.form['publishedBefore']
            publishedAfter       = request.form['publishedAfter']
            print('{0} | {1}'.format(publishedBefore, publishedAfter))
            try:
                nextToken        = request.form['nextToken']
            except KeyError:
                nextToken        = None
            db.session.query(Albums).delete()
            db.session.query(Favorites).filter_by(videoTitle='Not Given').delete()
            db.session.commit()
            currentBand          = criteria_crunch(
                dunderSearch     = dunderSearch,
                publishedBefore  = publishedBefore,
                publishedAfter   = publishedAfter,
                nextToken        = nextToken,
                dunderAnchor     = dunderAnchor)
        else:
            return redirect('users/login')
            flash("You Need To Login First - Click Signup If You Don't Have A Username Yet")
        if currentBand == None or currentBand == False:
            flash('Search String Exausted | Double Your Efforts')
            return redirect('search/dunderbands')
        else:
            return render_template (
                'search/results.html',
                 currentBand     = currentBand,
                 publishedBefore = publishedBefore,
                 publishedAfter  = publishedAfter,
                 current_user    = current_user)



