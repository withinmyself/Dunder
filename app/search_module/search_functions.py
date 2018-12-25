import re
import datetime
import random

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from app.search_module.models import Albums
from app.search_module.strings import no_words, genrePrefix, \
     genreMain, countryOfOrigin, my_exciters
from app.users_module.models import Favorites, Ignore, Comments
from app.users_module.controllers import current_user
from app.settings_module.settings_functions import get_like_ratio, \
     get_comments_needed, get_max_views, get_view_ratio
from app import db, redis_server


DEVELOPER_KEY = redis_server.get('DEVELOPER_KEY').decode('utf-8')

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

DEBUG = True
SEE_TITLES = False

def no_word_string():
    search_no_words = ['-{0}'.format(word) for word in no_words]
    return re.sub(r'[.!,;?]', ' ', str(search_no_words)).upper()

# Add words from lists to database.
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



# Main API interaction to YouTube.
def search_getter(q, max_results=1, token=None, location=None,
                  location_radius=None, related_video=None,
                  published_before=None, published_after=None):

    if DEBUG == True:
        print("SEARCH_GETTER")

    resultsSearch = YOUTUBE.search().list(
        q=q,
        type="video",
        pageToken=token,
        order = "relevance",
        videoDuration="long",
        videoDefinition="high",
        videoEmbeddable="true",
        part="id,snippet",
        maxResults=max_results,
        location=location,
        locationRadius=location_radius,
        relatedToVideoId=related_video,
        publishedBefore=published_before,
        publishedAfter=published_after
        ).execute()

    return resultsSearch



# Pull stats to compare against.
def stat_checker (videoId):

    LIKE_RATIO = get_like_ratio()
    VIEW_RATIO = get_view_ratio()
    MAX_VIEWS  = get_max_views()

    if DEBUG == True:
        print("STAT_CHECKER")
    else:
        pass

    stats = YOUTUBE.videos().list(id=videoId, part='snippet, recordingDetails, statistics'
                                  ).execute()

    try:
        likeCount = stats['items'][0]['statistics']['likeCount']
        dislikeCount = stats['items'][0]['statistics']['dislikeCount']
        commentCount = stats['items'][0]['statistics']['commentCount']
        viewCount = stats['items'][0]['statistics']['likeCount']
        totalVotes = likeCount + dislikeCount
    except KeyError:
        print("KeyError")
        return False

    try:
        isLiked     = float(dislikeCount) / float(totalVotes) <= LIKE_RATIO
        isViewed    = float(totalVotes) / float(viewCount) >= VIEW_RATIO
        isMax       = int(viewCount) <= MAX_VIEWS
        hasComments = int(commentCount) != 0
        hasViews    = int(viewCount) != 0
        if isLiked and isViewed and isMax and hasComments and hasViews:
            return True
        else:
            return False

    except ZeroDivisionError:
        print("ZeroDivisionError")
        return False



# Uses the videoID to retrieve top 100 comments.
# After 'cleaning' the results, we try to find words
# from our list of desirable descriptives.
def comment_counter (videoId):

    MIN_COUNT = get_comments_needed()
    if DEBUG == True:
        print("COMMENT_COUNTER")

    wordsFound = 0

    comments = YOUTUBE.commentThreads().list (
                                part="snippet",
                                maxResults=100,
                                videoId=videoId,
                                textFormat="plainText"
                                ).execute()

    extra_words = db.session.query(Comments).filter_by(define='exciter').all()
    for exciter in extra_words:
        my_exciters.append('{0}'.format(exciter.commentWord))
    my_best_exciters = list(set(my_exciters))

    try:
        for item in comments["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            cleanTxt = re.sub(r'[.!,;?]', ' ', text).lower()
            for word in my_best_exciters:
                wordsFound = wordsFound + cleanTxt.count(word)
    except KeyError:
        print("KeyError - Comments Are Disabled")
        return False

    if int(wordsFound) >= MIN_COUNT:
        for item in comments["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            cleanTxt = re.sub(r'[.!,;?]', ' ', text).lower()
            for word in my_best_exciters:
                if cleanTxt.count(word) > 0:
                    if len(text) > 500:
                        return text[:450]
                    else:
                        return text
    else:
        print('Low Count')
        return False





# The majority of our logic operators, error checking,
# and YouTube search results.
def criteria_crunch (dunderSearch, publishedBefore=None, publishedAfter=None,
                     nextToken=None, dunderAnchor=None):

    if DEBUG == True:
        print("CRITERIA_CRUNCH")
    else:
        pass
    redis_server.set('LOOP', 0)
    redis_server.set('WHILE', 'GO')
    while True:
        redis_server.incr('LOOP')
        if str(redis_server.get('WHILE').decode('utf-8')) == 'NOGO':
            print('Redis is a NOGO')
            return False
        else:
            pass
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
        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 10:
            print('Removing Prefix And Continuing Search')
            dunderSearch = dunderSearch[int(str(redis_server.get('PREFIX').decode('utf-8')))+1:len(dunderSearch)]
            print(dunderSearch)
            nextToken = None
        else:
            pass
        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 20:
            print('Removing Country And Continuing Search')
            dunderSearch = dunderSearch[:-int(str(redis_server.get('COUNTRY').decode('utf-8')))-1]
            print(dunderSearch)
            nextToken = None
        else:
            pass
        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 25:
            print('Removing Prefix And Country - Continuing Search')
            dunderSearch = dunderSearch[int(str(redis_server.get('PREFIX').decode('utf-8')))+1:-int(str(redis_server.get('COUNTRY').decode('utf-8')))-1]
            print(dunderSearch)
            nextToken = None
        else:
            pass
        if int(str(redis_server.get('LOOP').decode('utf-8'))) == 40:
            redis_server.set('LOOP', 0)
            redis_server.set('WHILE', 'NOGO')
            print('No Results Were Found - It Happens')
            return False
        else:
            pass
        for video in searchResults.get('items', []):
            videoId = video['id']['videoId']
            videoTitle = video['snippet']['title']
            isVideo = video['id']['kind'] == 'youtube#video'
            isClean = title_clean(video['snippet']['title'],
                                  includeSearch=dunderSearch)

            if isVideo and isClean:
                isFavorite = True
                doIgnore   = True
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

                checkStats = stat_checker(videoId=videoId)
                try:
                    checkComments = comment_counter(videoId=videoId) != False
                except HttpError:
                    print('Comments Disabled')
                    checkComments = False

                if isFavorite and doIgnore and checkStats and checkComments:
                    redis_server.set('WHILE', 'NOGO')
                    currentBand = Albums (
                      videoId=videoId, nextToken=nextToken,
                      genre=dunderSearch.upper(), videoTitle=videoTitle,
                      topComment=comment_counter(videoId=videoId))

                    db.session.add(currentBand)
                    db.session.commit()
                    return currentBand

                else:
                    pass

            else:
                pass




# Takes current video title and checks against our list
# of no words.  This is to avoid 'mix' videos,
# compilations and 'best of' lists.
def title_clean (tubeTitle, includeSearch='search', includeBand='band'):

    if DEBUG == True:
        print("TITLE_CLEAN")

    titleList = re.sub(r'[.!,;?]', ' ', tubeTitle).lower().split()

    # This gives us the option to add extra words or band names.
    # By default is uses the search string itself to further avoid
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

    if DEBUG == True:
        print("STRING_CLEAN")
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



# Return a string with 1 random genre, 1 random sub-genre and 1 random country
def random_genre (genrePrefix=genrePrefix, genreMain=genreMain,
                  countryOfOrigin=countryOfOrigin):

    randomPrefix = random.choice(genrePrefix)
    randomGenre = random.choice(genreMain)
    randomCountry = random.choice(countryOfOrigin)
    return (str('{}'.format(randomPrefix)) + ' ' +
            str('{}'.format(randomGenre)) +  ' ' +
            str('{}'.format(randomCountry)))
