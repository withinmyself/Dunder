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

DEVELOPER_KEY = redis_server.get('DEVELOPER_KEY').decode('utf-8')

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

settings = Criteria()

# no_words are words associated with compilation videos, fan videos, mixtapes.
# yes_words are words we search for in the comments of found albums.


def word_sort():
    for word in no_words:
        new_word = Comments(word, 'noWord')
        db.session.add(new_word)
        db.session.commit()
        db.session.close()
    for excite in my_exciters:
        new_excite = Comments(excite, 'exciter')
        db.session.add(new_excite)
        db.session.commit()
        db.session.close()

# Take four digit year. Return RFC3339 datetime object.
def year_selecter(year):
    yearConverted = datetime.datetime(int(year),12,30).isoformat()+'Z'
    return yearConverted

# API interaction to YouTube.
def search_getter(
    q, max_results=1, token=None, location=None,
    location_radius=None, related_video=None,
    published_before=None, published_after=None):

    resultsSearch = YOUTUBE.search().list(
      q=q, type="video", pageToken=token,
      order="relevance", videoDuration="long",
      videoDefinition="high", videoEmbeddable="true",
      part="id,snippet",  maxResults=max_results,
      location=location, locationRadius=location_radius,
      relatedToVideoId=related_video,
      publishedBefore=published_before,
      publishedAfter=published_after
      ).execute()

    return resultsSearch

# Pull stats to compare against.
def stat_checker (videoId):

    like_ratio = settings.get_like_ratio()
    view_ratio = settings.get_view_ratio()
    max_views = settings.get_max_views()

    video_stats = YOUTUBE.videos().list(id=videoId, 
        part='snippet, recordingDetails, statistics'
        ).execute()

    try:
        like_count = video_stats['items'][0]['statistics']['likeCount']
        dislike_count = video_stats['items'][0]['statistics']['dislikeCount']
        comment_count = video_stats['items'][0]['statistics']['commentCount']
        view_count = video_stats['items'][0]['statistics']['likeCount']
        total_count = like_count + dislike_count
    except KeyError:
        print("KeyError: A stat is not accessable.")
        return False

    try:
        is_liked = float(dislike_count) / float(total_count) <= like_ratio
        is_viewed = float(total_count) / float(view_count) >= view_ratio
    except ZeroDivisionError:
        print("ZeroDivisionError: Missing a count.")
        return False
    
    is_max = int(view_count) <= max_views
    has_comments = int(comment_count) != 0
    has_views = int(view_count) != 0

    if is_liked and is_max and has_comments and has_views:
        return True
    return False

# We pull the first 100 comments from our criteria passed video.
def comment_getter (videoId):
    try:
        comments = YOUTUBE.commentThreads().list (
                                part="snippet",
                                maxResults=100,
                                videoId=videoId,
                                textFormat="plainText").execute()
    except HttpError:
        print("Comments isabled")
        return False

def get_yes_words(yes_words=yes_words):

    new_yes_words = db.session.query(Comments).filter_by(define='exciter').all()
    for yes_word in new_yes_words:
        yes_words.append('{0}'.format(yes_word.commentWord))
    
    all_yes_words = list(set(yes_words))
    return all_yes_words

def comment_word_counter(comments, all_yes_words):

    try:
        comments=comments
        for item in comments["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
    except TypeError:
        print("Comments disabled")
        return False
        
        clean_text = re.sub(r'[.!,;?]', ' ', text).lower()
        words_found = 0
        x = 0
        all_yes_words=all_yes_words
        for word in all_yes_words:
            print('for word')
            words_found = words_found + clean_text.count(word)
            
            if words_found > 0 and x != 1:
                text = text
                x+=1

        if x > 0:
            return text[50:]
        return False

# Logic operators, error checking and YouTube search results.
def criteria_crunch (dunderSearch, publishedBefore=None, publishedAfter=None,
                     nextToken=None, dunderAnchor=None):


    redis_server.set('LOOP', 0)
    redis_server.set('WHILE', 'GO')
    while True:
        redis_server.incr('LOOP')
        if str(redis_server.get('WHILE').decode('utf-8')) == 'NOGO':
            print('Redis is a NOGO')
            return False

        try:
            published_before = year_selecter(publishedBefore)
        except ValueError:
            print('Default Before')
            publishedBefore = year_selecter(year=2018)

        try:
            published_after = year_selecter(publishedAfter)
        except ValueError:
            print('Default After')
            publishedAfter = year_selecter(year=2016)

        searchResults = search_getter (
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
            isClean = title_clean(video['snippet']['title'],
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
                
                checkStats = stat_checker(videoId=videoId)
                comments = comment_getter(videoId=videoId)
                all_yes_words = get_yes_words()
                check_comments = comment_word_counter(
                    comments=comments, 
                    all_yes_words=all_yes_words) != False


                if isFavorite and doIgnore and checkStats and check_comments:
                    redis_server.set('WHILE', 'NOGO')
                    currentBand = Albums (
                      videoId=videoId, nextToken=nextToken,
                      genre=dunderSearch.upper(), videoTitle=videoTitle,
                      topComment=check_comments)

                    db.session.add(currentBand)
                    db.session.commit()
                    return currentBand

# Takes current video title and checks against our list
# of words that might pull in 'mix' videos,
# compilations and 'best of' lists.
def title_clean (tubeTitle, includeSearch='search', includeBand='band'):

    titleList = re.sub(r'[.!,;?]', ' ', tubeTitle).lower().split()

    # This gives us the option to add extra words or band names.
    # By default it uses the search string itself to further avoid
    # 'lists' or 'compilations' as opposed to actual albums.
    no_words.append('{0}'.format(includeSearch))
    no_words.append('{0}'.format(includeBand))
    extra_no_words = db.session.query(Comments).filter_by(define='noWord').all()

    for word in extra_no_words:
        no_words.append('{0}'.format(word.commentWord))
    best_no_words = list(set(no_words))

    for word in titleList:
        for noWord in best_no_words:
            if noWord == word:
                return False
    return True

# Takes a string and returns either a list or a string
# upper or lower without punctuation marks
def string_clean(dirtyText, listOrString=None):


    try:
        if listOrString == 'listNeededLower':
            return re.sub(r'[.!,;?]', ' ', dirtyText).lower().split()
        if listOrString == 'stringNeededLower':
            return re.sub(r'[.!,;?]', ' ', dirtyText).lower()
        if listOrString == 'listNeededUpper':
            return re.sub(r'[.!,;?]', ' ', dirtyText).upper().split()
        if listOrString == 'stringNeededUpper':
            return re.sub(r'[.!,;?]', ' ', dirtyText).upper()
        if listOrString == 'listNeeded':
            return re.sub(r'[.!,;?]', ' ', dirtyText).split()
        if listOrString == 'stringNeeded':
            return re.sub(r'[.!,;?]', ' ', dirtyText)
        if listOrString == None:
            return 'Arguments Missing'

    except TypeError as e:
        print('Arguments Missing: {0}'.format(e))



