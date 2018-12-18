import re
import datetime
import random

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from app.search_module.models import Albums
from app.search_module.strings import noWords, genrePrefix, \
     genreMain, countryOfOrigin
from app import db, redis_server


DEVELOPER_KEY = redis_server.get('DEVELOPER_KEY').decode('utf-8')

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

DEBUG = True
SEE_TITLES = False


class ArgumentsMissing(Exception):
# Custom exception missing arguments.

    def __init__(self, code):
        self.code = code
    def __str__(self):
        return repr(self.code)

def year_selecter(year):
# Take four digit year. Return RFC3339 datetime object.

    yearConverted = datetime.datetime(int(year),12,30).isoformat()+'Z'
    return yearConverted


def criteria_alter(value):
# Takes value from the slider to adjust criteria.

    if DEBUG == True:
        print("CRITERIA_ALTER")

    int_value = int(value)
    float_value = float(int_value)

    if int_value != 50:
        redis_server.set('LIKE_RATIO', float_value * 0.0007)
        MAX_VIEWS = int_value * 300
    else:
        MAX_VIEWS = int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))

    LIKE_RATIO = redis_server.get('LIKE_RATIO').decode('utf-8')
    if int_value <= 15:
        MIN_COUNT = 3
    if int_value > 15 and int_value <= 60:
        MIN_COUNT = 2
    if int_value > 60 and int_value <= 85:
        MIN_COUNT = 1
    if int_value > 85:
        MIN_COUNT = 0
    if DEBUG == True:
        print("MAX_VIEWS = {0}, LIKE_RATIO = {1}, MIN_COUNT = {2}, SLIDER: {3}".format(
                                        MAX_VIEWS, LIKE_RATIO, MIN_COUNT, value))

    return "MaxViews: {0} | LikeRatio: {1} | MinCount: {2}".format(MAX_VIEWS, LIKE_RATIO, MIN_COUNT)

def search_getter(q, max_results=1, token=None, location=None,
                  location_radius=None, related_video=None,
                  published_before=None, published_after=None):
# Main API interaction to YouTube.

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



def stat_checker (videoId):
# Pull stats to compare against.

    LIKE_RATIO=float(str(redis_server.get('LIKE_RATIO').decode('utf-8')))
    VIEW_RATIO=float(str(redis_server.get('VIEW_RATIO').decode('utf-8')))
    MAX_VIEWS=int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))

    if DEBUG == True:
        print("STAT_CHECKER")
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
    pass


    try:
        if (float(dislikeCount) / float(totalVotes) <= LIKE_RATIO and
            float(totalVotes) / float(viewCount) >= VIEW_RATIO and
            int(viewCount) <= int(MAX_VIEWS) and
            int(commentCount) != 0 and
            int(viewCount) != 0
            ):
            return True
        else:
            return False
    except ZeroDivisionError:
        print("ZeroDivisionError")
        return False
    pass


def comment_counter (videoId):
# Uses the videoID to retrieve top 100 comments.
# After 'cleaning' the results, we try to find words
# from our list of desirable descriptives.

    MIN_COUNT = int(str(redis_server.get('MIN_COUNT').decode('utf-8')))
    if DEBUG == True:
        print("COMMENT_COUNTER")

    wordsFound = 0
    wordsToFind = ('amazing', 'speechless', 'fantastic',
                   'incredible', 'masterpiece', 'breathtaking',
                   'transcendental')

    comments = YOUTUBE.commentThreads().list (part="snippet",
                                              maxResults=100,
                                              videoId=videoId,
                                              textFormat="plainText"
                                              ).execute()
    try:
        for item in comments["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            cleanTxt = re.sub(r'[.!,;?]', ' ', text).lower()

            for word in wordsToFind:
                wordsFound = wordsFound + cleanTxt.count(word)

        # If MIN_COUNT is met, search through again and
        # return one comment that includes our found words
        if int(wordsFound) >= MIN_COUNT:
            for item in comments["items"]:
                comment = item["snippet"]["topLevelComment"]
                text = comment["snippet"]["textDisplay"]
                cleanTxt = re.sub(r'[.!,;?]', ' ', text).lower()
                for word in wordsToFind:
                    if cleanTxt.count(word) > 0:
                        if len(text) > 500:
                            return text[:450]
                        else:
                            return text
        else:
            print('False Count')
            return False

    except KeyError:
        print("KeyError - Comments Are Disabled")
        return False
    pass



def criteria_crunch (dunderSearch, value=50, nextToken=None,
                     dunderAnchor=None, publishedBefore=None,
                     publishedAfter=None):
# The majority of our logic operators, error checking,
# and YouTube search results.

    if DEBUG == True:
        print("CRITERIA_CRUNCH")
    if publishedBefore != None:
        try:
            publishedBefore = year_selecter(year=publishedBefore)
        except ValueError:
            print("Missing Year For Published Before.  Allowing Default.")
            publishedBefore = year_selecter(year=2018)

    if publishedAfter != None:
        try:
            publishedAfter = year_selecter(year=publishedAfter)
        except ValueError:
            print("Missing Year For Published After.  Allowing Default.")
            publishedAfter = year_selecter(year=2016)
    criteria_alter(value)

    while True:

        if SEE_TITLES == True:
            print("Beat", MAX_VIEWS, MIN_COUNT, VIEW_RATIO, LIKE_RATIO)

        searchResults = search_getter (dunderSearch,
                                       token=nextToken,
                                       related_video=dunderAnchor,
                                       published_before=publishedBefore,
                                       published_after=publishedAfter)

        try:
            nextToken = searchResults['nextPageToken']
        except KeyError:
            print("KeyError with nextToken - breaking loop")
            break
            return False
            # If we reach the last page using current criteria
            # we reset the page token and set the value
            # to 50 using criteria_alter().

            criteria_alter(50)
            nextToken = None

        for video in searchResults.get("items", []):
            try:
                if (video['id']['kind'] == "youtube#video" and
                    title_clean(video['snippet']['title'], includeSearch=dunderSearch) == True):

                    videoId = video['id']['videoId']
                    videoTitle = video['snippet']['title']

                    if SEE_TITLES == True:
                        print(videoTitle)

                    if (db.session.query(Albums).filter_by(videoId=videoId).first() == None and
                        stat_checker(videoId=videoId) == True and
                        comment_counter(videoId=videoId) != False):

                        currentBand = Albums (videoId=videoId,
                                              nextToken=nextToken,
                                              genre=dunderSearch.upper(),
                                              videoTitle=videoTitle,
                                              topComment=comment_counter(videoId=videoId),
                                              isFavorite='')
                        db.session.add(currentBand)
                        db.session.commit()
                        return currentBand

                    else:
                        pass
                else:
                    pass
            except HttpError:
                print("HttpError, Comments are disabled")
                pass

    pass


def title_clean (tubeTitle,
                 includeSearch='search',
                 includeBand='band'):
# Takes current video title and checks against our list
# of no words.  This is to avoid 'mix' videos,
# compilations and 'best of' lists.

    if DEBUG == True:
        print("TITLE_CLEAN")

    titleList = re.sub(r'[.!,;?]', ' ', tubeTitle).lower().split()
    noWords.append("{0}".format(includeSearch))
    noWords.append("{0}".format(includeBand))
    for word in titleList:
        for noWord in noWords:
            if noWord == word:
                return False
    return True


def string_clean(dirtyText, listOrString=None):
# Takes a string and returns either a list or a string
# upper or lower without punctuation marks

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
            raise ArgumentsMissing('Type Needed For Return.')

    except TypeError as e:
        print("Need to provide string or list")
    pass


# Return a string with 1 random genre, 1 random sub-genre and 1 random country
def random_genre (genrePrefix=genrePrefix, genreMain=genreMain,
                               countryOfOrigin=countryOfOrigin):

    randomPrefix = random.choice(genrePrefix)
    randomGenre = random.choice(genreMain)
    randomCountry = random.choice(countryOfOrigin)
    return (str('{}'.format(randomPrefix)) + ' ' +
            str('{}'.format(randomGenre)) +  ' ' +
            str('{}'.format(randomCountry)))
