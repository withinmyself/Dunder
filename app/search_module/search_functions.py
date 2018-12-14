
import re
import datetime

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from app.search_module.models import Albums
from app import db




DEVELOPER_KEY = "AIzaSyBQEcuLzY9DirijZ_Vx9QCKMstDvl8Zi6Y"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

MAX_VIEWS = 15000
LIKE_RATIO = 0.015
VIEW_RATIO = 0.035
MIN_COUNT = 2
DEBUG = False
SEE_TITLES = False

class ArgumentsMissing(Exception):
    """
    Custom exception for 
    missing arguments.
    """
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return repr(self.code)

def year_selecter(year):
    """
    Take four digit year. 
    Return RFC3339 datetime object.
    """
    yearConverted = datetime.datetime(int(year),12,30).isoformat()+'Z'
    return yearConverted


def criteria_alter(value):
    """
    Takes value from the slider
    on the main page and adjusts
    our criteria.
    """
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE59 - CRITERIA_ALTER")  
    global MAX_VIEWS
    global LIKE_RATIO
    global MIN_COUNT

    MAX_VIEWS = int(value) * 300
    LIKE_RATIO = float(value) * 0.0007

    if int(value) <= 10:
        MIN_COUNT = 3
    if int(value) > 10 and int(value) <= 40:
        MIN_COUNT = 2
    if int(value) > 40 and (value) <= 70:
        MIN_COUNT = 1
    if int(value) > 70:
        MIN_COUNT = 0
    if DEBUG == True:
        print("MAX_VIEWS = {0}, LIKE_RATIO = {1}, MIN_COUNT = {2}".format(MAX_VIEWS, LIKE_RATIO, MIN_COUNT))


def search_getter(q, max_results=1, token=None, location=None,
               location_radius=None, related_video=None,
               published_before=None, published_after=None):
    """
    Main API interaction to YouTube.
    Returns only one video per search
    in order to sort with our
    custom criteria.
    """
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE89 - SEARCH_GETTER")

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
    """
    Pull stats to compare against
    our adjustable ratio variables.
    Check for ZeroDivisionError
    and KeyError in search results.
    """
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE120 - STAT_CHECKER")
    stats = YOUTUBE.videos().list(
                                  id=videoId,
                                  part='snippet, recordingDetails, statistics'
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
        if (
            float(dislikeCount) / float(totalVotes) <= LIKE_RATIO and
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
    """
    Uses the videoID to
    retrieve top 100 comments.
    After 'cleaning' the results,
    we try to find words from our 
    list of desirable descriptives.
    """    
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE163 - COMMENT_COUNTER")

    wordsFound = 0
    wordsToFind = (
                   'amazing', 'speechless', 'fantastic',
                   'incredible', 'masterpiece', 'breathtaking',
                   'transcendental'
                   )

    comments = YOUTUBE.commentThreads().list (
                                               part="snippet",
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
        print("KeyError, Comments Are Disabled")
        return False
    pass



def criteria_crunch (
                     dunderSearch, value=50,
                     nextToken=None, dunderAnchor=None,
                     publishedBefore=None, publishedAfter=None
                     ):
    """
    The majority of our logic 
    operators, error checking,
    and YouTube search results.
    """    
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE217 - CRITERIA_CRUNCH")   
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

    try:
        criteria_alter(int(value))
    except (TypeError, ValueError) as e:
        print("Failed Inside criteria_alter().  {0!r}".format(e))
        pass

    while True:

        if SEE_TITLES == True:
            print("Beat", MAX_VIEWS, MIN_COUNT, VIEW_RATIO, LIKE_RATIO)

        searchResults = search_getter ( 
                                       dunderSearch, 
                                       token=nextToken,
                                       related_video=dunderAnchor,
                                       published_before=publishedBefore,
                                       published_after=publishedAfter
                                       )

        try:
            nextToken = searchResults['nextPageToken']
        except KeyError:
            print("KeyError. Last Page. Adjusting Criteria")
            # If we reach the last page using current criteria
            # we reset the page token and set the value
            # to 50 using criteria_alter().

            criteria_alter(50)
            nextToken = None
            pass

        for video in searchResults.get("items", []):
            try:
                if ( 
                    video['id']['kind'] == "youtube#video" and
                    title_clean(video['snippet']['title'], includeSearch=dunderSearch) == True
                    ):
                    videoId = video['id']['videoId']
                    videoTitle = video['snippet']['title']

                    if SEE_TITLES == True:
                        print(videoTitle)

                    if (
                        db.session.query(Albums).filter_by(videoId=videoId).first() == None and
                        stat_checker(videoId=videoId) == True and
                        comment_counter(videoId=videoId) != False
                        ):
                        currentBand = Albums (
                                              videoId=videoId,
                                              nextToken=nextToken,
                                              genre=dunderSearch.upper(),
                                              videoTitle=videoTitle,
                                              topComment=comment_counter(videoId=videoId),
                                              isFavorite=''
                                              )
                        db.session.add(currentBand)
                        db.session.commit()
                        return currentBand

                    else:
                        pass
                else:
                    pass
            except HttpError:
                print("HttpError, Comments Disables")
                pass

    pass


def title_clean (
                 tubeTitle,
                 includeSearch='search',
                 includeBand='band'
                 ):
    """
    Takes current video title
    and checks against our list 
    of no words.  This is to avoid
    'mix' videos, compilations and
    'best of' lists.
    """
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE310 - TITLE_CLEAN")

    titleList = re.sub(r'[.!,;?]', ' ', tubeTitle).lower().split()
    noWords = (
               '{}'.format(includeSearch),'{}'.format(includeBand),
               'best','for','list', 'top','overall','show','all time','greatest',
               'number', 'vol', 'compilation', 'volume', 'mix', 'part',
               'all-time', 'aniversary', 'promo', 'disco',
               'relaxing', 'soothing', 'playlist',
               'recordings', 'live', 'aniversary',
               'guest', 'popular', 'talented',
               'vocals', 'mixing', 'recording',
               'rock', 'metal', 'documentary',
               'extreme', 'mixtape', 'mix)', '(',
               ')', '90s', '80s', '70s', '60s', '50s',
               'band', 'debate', 'blackgaze',
               'tutorial','guide', 'year','level',
               'workshop', 'design', 'food', 'tour',
               'classics', 'modern', 'hours', 'minutes',
               'piano', 'explained', 'theories', 'endings',
               'improvise', 'solo', 'freestyle', 'saxaphone',
               'session', 'sessions', 'what', '#podsessions',
               'podcast',
               )

    for word in titleList:
        for noWord in noWords:
            if noWord == word:
                return False
    return True


def string_clean(dirtyText, listOrString=None):
    """
    Takes a string and returns
    either a list or a string, upper or
    lower without punctuation marks
    """
    if DEBUG == True:
        print("TUBEYOUSEARCH.PY - LINE332 - STRING_CLEAN")
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

    except ArgumentsMissing as e:
        print(e.code)
    pass




