from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from flask_login import login_required, logout_user, current_user

import asyncio


from app import db, redis_server
from app.settings_module.models import Favorites
from app.search_module.models import Albums
from app.search_module.search_functions import criteria_crunch, \
     string_clean, random_genre

search_routes = Blueprint('search', __name__, url_prefix='/search')

# Routes for our search engine

# Main search page
@search_routes.route('/', methods=['GET', 'POST'])
@login_required
def dunderbands():
    db.session.query(Albums).delete()
    db.session.query(Favorites).filter_by(videoTitle='Not Given').delete()
    db.session.commit()
    db.session.close()
    if request.method == 'GET':
        return render_template('search/dunderbands.html')
        redis_server.set('AROUND', 0)
    else:
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
        dunderSearch     = string_clean(dunderRequest, 'stringNeededUpper')
        publishedBefore  = request.form['publishedBefore']
        publishedAfter   = request.form['publishedAfter']
        try:
            nextToken = request.form['nextToken']
        except KeyError:
            nextToken = None
        currentBand = criteria_crunch(
            dunderSearch=dunderSearch,
            publishedBefore=publishedBefore,
            publishedAfter=publishedAfter,
            nextToken=nextToken, dunderAnchor=dunderAnchor)

        if currentBand == None or currentBand == False:
            flash('Search String Exausted | Double Your Efforts')
            return render_template('search/dunderbands.html')
        else:
            return render_template ('search/results.html',
                                    videoId=currentBand.videoId,
                                    nextToken = currentBand.nextToken,
                                    genre=currentBand.genre,
                                    videoTitle=currentBand.videoTitle,
                                    commentPlug=currentBand.topComment,
                                    isFavorite=currentBand.isFavorite,
                                    publishedBefore=publishedBefore,
                                    publishedAfter=publishedAfter)



