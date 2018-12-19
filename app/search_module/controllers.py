from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from app import db
from app.search_module.models import Albums
from app.search_module.search_functions import criteria_crunch, \
     string_clean, random_genre

search_routes = Blueprint('search', __name__, url_prefix='/search')

# Routes for our search engine

# Main search page
@search_routes.route('/', methods=['GET', 'POST'])
def dunderbands():
    dunderRandom = random_genre()
    if request.method == 'GET':
        db.session.query(Albums).delete()
        return render_template('search/dunderbands.html',
                               dunderRandom=dunderRandom)
    else:
        try:
            dunderAnchor = request.form['videoId']
        except KeyError:
            dunderAnchor = None
        dunderRequest    = request.form['dunderSearch']
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

        if currentBand == None:
            flash("Try expanding your search with sub-genres and/or countries")
            return render_template('search/dunderbands.html',
                                   dunderRandom=dunderRandom)
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



