import re
import datetime
import random

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from app.search_module.models import Albums
from app.search_module.strings import no_words, genrePrefix, \
     genreMain, countryOfOrigin, yes_words
from app.users_module.models import Favorites, Ignore, Comments
from app.users_module.controllers import current_user
from app.settings_module.settings_functions import Criteria
from app import db, redis_server

from app.search_module.search_methods import Search

settings = Criteria()
search = Search()

# no_words are words associated with compilation videos, fan videos, mixtapes.
# yes_words are words we search for in the comments of found albums.




# Logic operators, error checking and YouTube search results.
def criteria_crunch (dunderSearch, published_before=None, published_after=None,
                     nextToken=None, dunderAnchor=None):


    redis_server.set('LOOP', 0)
    redis_server.set('WHILE', 'GO')
    while True:
        redis_server.incr('LOOP')
        if str(redis_server.get('WHILE').decode('utf-8')) == 'NOGO':
            print('Redis is a NOGO')
            return False
        print(published_after, published_before)
        published_before = search.year_selecter(year=2018)
        published_after = search.year_selecter(year=2016)


        searchResults = search.search_getter (
                        dunderSearch,
                        token=nextToken,
                        related_video=dunderAnchor,
                        published_before=published_before,
                        published_after=published_after)
        try:
            nextToken = searchResults['nextPageToken']
        except KeyError:
            nextToken = None
        
        # At 10 iterations we start removing words from the search 
        # to increase the chance of receiving a result.
        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 10:
            print('Removing Prefix And Continuing Search')
            dunderSearch = dunderSearch[int(str(redis_server.get('PREFIX').decode('utf-8')))+1:len(dunderSearch)]
            print(dunderSearch)
            nextToken = None

        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 20:
            print('Removing Country And Continuing Search')
            dunderSearch = dunderSearch[:-int(str(redis_server.get('COUNTRY').decode('utf-8')))-1]
            print(dunderSearch)
            nextToken = None

        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 25:
            print('Removing Prefix And Country - Continuing Search')
            dunderSearch = dunderSearch[int(str(redis_server.get('PREFIX').decode('utf-8')))+1:-int(str(redis_server.get('COUNTRY').decode('utf-8')))-1]
            print(dunderSearch)
            nextToken = None

        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 35:
            redis_server.set('LOOP', 0)
            redis_server.set('WHILE', 'NOGO')
            print('No Results Were Found - It Happens')
            return False

        for video in searchResults.get('items', []):
            videoId = video['id']['videoId']
            videoTitle = video['snippet']['title']
            isVideo = video['id']['kind'] == 'youtube#video'
            isClean = search.title_clean(video['snippet']['title'],
                                  includeSearch=dunderSearch)

            if isVideo and isClean:
                isFavorite = True
                doIgnore   = True
                try:
                    for favorite in current_user.favorites:
                        if favorite.videoId == videoId:
                            isFavorite = False
                        else:
                            continue
                    for ignore in current_user.ignore:
                        if ignore.videoId == videoId:
                            doIgnore = False
                        else:
                            continue
                except AttributeError:
                    print('Unit Test - Current User Is Fraudulent')
                
                checkStats = search.stat_checker(videoId=videoId)
                comments = search.comment_getter(videoId=videoId)
                all_yes_words = search.get_yes_words()
                if comments != False:
                    try:
                        check_comments = search.comment_word_counter(
                            comments=comments, 
                            all_yes_words=all_yes_words)
                    except KeyError:
                        print('KeyError: Comments disabled.')
                        check_comments = False
                else:
                    check_comments = False

                if check_comments != False:
                    if isFavorite and doIgnore and checkStats:
                        redis_server.set('WHILE', 'NOGO')
                        currentBand = Albums (
                            videoId=videoId, nextToken=nextToken,
                            genre=dunderSearch.upper(), videoTitle=videoTitle,
                            topComment=check_comments)

                        db.session.add(currentBand)
                        db.session.commit()
                        return currentBand
