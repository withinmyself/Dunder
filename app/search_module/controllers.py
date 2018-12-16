from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

from app import db
from app.search_module.models import Albums
from app.search_module.search_functions import criteria_crunch, \
     string_clean, random_genre

search_blueprint = Blueprint('search', __name__, url_prefix='/search')

# Routes for our search engine

# Main search page
@search_blueprint.route('/', methods=['GET', 'POST'])
def dunderbands():
    dunderRandom = random_genre()
    return render_template('search/dunderbands.html',
                           dunderRandom=dunderRandom)

# After search finds
@search_blueprint.route('/found_album/', methods=['POST'])
def found_album():
    dunderRequest = request.form['dunderSearch']
    dunderSearch = string_clean(dunderRequest, 'stringNeededUpper')
    publishedBefore = request.form['publishedBefore']
    publishedAfter = request.form['publishedAfter']
    nextToken = None

    currentBand = criteria_crunch (dunderSearch=dunderSearch,
                                   value=50,
                                   nextToken=nextToken,
                                   publishedBefore=publishedBefore,
                                   publishedAfter=publishedAfter) 
    return render_template ('search/found_album.html',
                            videoId=currentBand.videoId,
                            nextToken = currentBand.nextToken,
                            genre=currentBand.genre,
                            videoTitle=currentBand.videoTitle,
                            commentPlug=currentBand.topComment,
                            isFavorite=currentBand.isFavorite,
                            publishedBefore=publishedBefore,
                            publishedAfter=publishedAfter,
                            currentRareValue=sliderRange)

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

    return render_template ('search/found_album.html',
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


    return render_template ('search/found_album.html',
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

    return render_template ('search/found_album.html',
                            videoId=currentBand.videoId,
                            nextToken = currentBand.nextToken,
                            genre=currentBand.genre,
                            videoTitle=currentBand.videoTitle,
                            commentPlug=currentBand.topComment,
                            isFavorite=currentBand.isFavorite,
                            publishedBefore=publishedBefore,
                            publishedAfter=publishedAfter)
