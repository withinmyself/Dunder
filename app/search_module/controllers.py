from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from app import db
from app.search_module.models import Albums
from app.search_module.search_functions import criteria_crunch, \
     string_clean, random_genre
from app.settings_module.settings_functions import *

search_blueprint = Blueprint('search', __name__, url_prefix='/search')

# Routes for our search engine

# Main search page
@search_blueprint.route('/', methods=['GET', 'POST'])
def dunderbands():
    if request.method == 'GET':
        dunderRandom = random_genre()
        return render_template('search/dunderbands.html',
                               dunderRandom=dunderRandom)
    else:
        dunderRequest = request.form['dunderSearch']
        dunderSearch = string_clean(dunderRequest, 'stringNeededUpper')
        publishedBefore = request.form['publishedBefore']
        publishedAfter = request.form['publishedAfter']
        if request.form['nextToken'] == 'None':
            nextToken = None
        else:
            nextToken = request.form['nextToken']
        currentBand = criteria_crunch (dunderSearch=dunderSearch,
                                       value=50,
                                       nextToken=nextToken,
                                       publishedBefore=publishedBefore,
                                       publishedAfter=publishedAfter)
        if currentBand == False:
            flash("Try expanding your search with sub-genres and/or countries")
            return render_template('search')
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

# Keep searching with same user given criteria
@search_blueprint.route('/keep_searching/', methods=['POST'])
def keep_searching():
    dunderSearch = request.form['genre']
    nextToken = request.form['nextToken']
    publishedBefore = request.form['publishedBefore']
    publishedAfter = request.form['publishedAfter']

    currentBand = criteria_crunch (dunderSearch=dunderSearch,
                                   value=50,
                                   nextToken=nextToken,
                                   publishedBefore=publishedBefore,
                                   publishedAfter=publishedAfter)

    return render_template ('search/results.html',
                            videoId=currentBand.videoId,
                            nextToken = currentBand.nextToken,
                            genre=currentBand.genre,
                            videoTitle=currentBand.videoTitle,
                            commentPlug=currentBand.topComment,
                            isFavorite=currentBand.isFavorite,
                            publishedBefore=publishedBefore,
                            publishedAfter=publishedAfter)

# Use random genre generator to search
@search_blueprint.route('/random/', methods=['POST'])
def random():
    dunderSearch = random_genre()
    print(dunderSearch)
    nextToken = None
    publishedBefore = request.form['publishedBefore']
    publishedAfter = request.form['publishedAfter']
    currentBand = criteria_crunch (dunderSearch=dunderSearch,
                                   value=50,
                                   nextToken=nextToken,
                                   publishedBefore=publishedBefore,
                                   publishedAfter=publishedAfter)


    return render_template ('search/results.html',
                            videoId=currentBand.videoId,
                            nextToken = currentBand.nextToken,
                            genre=currentBand.genre,
                            videoTitle=currentBand.videoTitle,
                            commentPlug=currentBand.topComment,
                            isFavorite=currentBand.isFavorite,
                            publishedBefore=publishedBefore,
                            publishedAfter=publishedAfter)

# Next search is directly associated with the current found album
@search_blueprint.route('/anchor_pivot/', methods=['POST'])
def anchor_pivot():
    dunderSearch = request.form['genre']
    dunderAnchor = request.form['videoId']
    publishedBefore = request.form['publishedBefore']
    publishedAfter = request.form['publishedAfter']
    nextToken = None

    currentBand = criteria_crunch (dunderSearch=dunderSearch,
                                   value=50,
                                   nextToken=nextToken,
                                   dunderAnchor=dunderAnchor,
                                   publishedBefore=publishedBefore,
                                   publishedAfter=publishedAfter)

    return render_template ('search/results.html',
                            videoId=currentBand.videoId,
                            nextToken = currentBand.nextToken,
                            genre=currentBand.genre,
                            videoTitle=currentBand.videoTitle,
                            commentPlug=currentBand.topComment,
                            isFavorite=currentBand.isFavorite,
                            publishedBefore=publishedBefore,
                            publishedAfter=publishedAfter)


@search_blueprint.route('/make_favorite/', methods=['POST'])
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


