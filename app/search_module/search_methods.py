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
class Search:

    def __init__(self):
        pass

    # API interaction to YouTube.
    def search_getter(self,
        q, max_results=50, video_duration='long', 
        token=None, location=None,
        location_radius=None, related_video=None,
        published_before=None, published_after=None):

        if redis_server.get('FULL_ALBUM').decode('utf-8') == False:
            video_duration = 'short'

        results_search = YOUTUBE.search().list(
          q=q, type="video", pageToken=token,
          order="relevance", videoDuration=video_duration,
          videoDefinition="high", videoEmbeddable="true",
          part="id,snippet",  maxResults=max_results,
          location=location, locationRadius=location_radius,
          relatedToVideoId=related_video,
          publishedBefore=published_before,
          publishedAfter=published_after
          ).execute()

        return results_search

    # Pull stats to compare against.
    def stat_checker (self, videoId):

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

    def preference_check(self, videoId): 
        not_favorite = True
        dont_ignore = True
                
        for favorite in current_user.favorites:
            if favorite.videoId == videoId:
                not_favorite = False

        for ignore in current_user.ignore:
            if ignore.videoId == videoId:
                dont_ignore = False

        if not_favorite and dont_ignore:
            return True
        return False

    # We pull the first 100 comments from our criteria passed video.
    def comment_getter (self, videoId):
        try:
            comments = YOUTUBE.commentThreads().list (
                                    part="snippet",
                                    maxResults=100,
                                    videoId=videoId,
                                    textFormat="plainText").execute()
            return comments
        except HttpError:
            print("Comments isabled")
            return False


    def get_yes_words(self, yes_words=yes_words):

        new_yes_words = db.session.query(Comments).filter_by(define='exciter').all()
        for yes_word in new_yes_words:
            yes_words.append('{0}'.format(yes_word.commentWord))
        
        all_yes_words = list(set(yes_words))
        return all_yes_words

    def comment_word_counter(self, comments, all_yes_words):


        redis_server.set('TOTAL_WORDS', 0)
        words_needed = settings.get_comments_needed()

        for item in comments["items"]:
            comment = item["snippet"]["topLevelComment"]
            text = comment["snippet"]["textDisplay"]
            
            words_found = 0
            clean_text = re.sub(r'[.!,;?]', ' ', text).lower()
            
            for word in all_yes_words:
                words_found = words_found + clean_text.count(word)
                if words_found > 0:
                    redis_server.set('COMMENT', text[:300])
                    redis_server.incr('TOTAL_WORDS')
                    break

        if int(str(redis_server.get('TOTAL_WORDS').decode('utf-8'))) >= words_needed:
            saved_comment = str(redis_server.get('COMMENT').decode('utf-8'))
            return saved_comment
        
        return False



        # Takes current video title and checks against our list
    # of words that might pull in 'mix' videos,
    # compilations and 'best of' lists.
    def title_clean (self, tubeTitle, include_search='search', include_band='band'):

        title_list = re.sub(r'[.!,;?]', ' ', tubeTitle).lower().split()

        # This gives us the option to add extra words or band names.
        # By default it uses the search string itself to further avoid
        # 'lists' or 'compilations' as opposed to actual albums.
        no_words.append('{0}'.format(include_search))
        no_words.append('{0}'.format(include_band))
        extra_no_words = db.session.query(Comments).filter_by(define='noWord').all()

        for word in extra_no_words:
            no_words.append('{0}'.format(word.commentWord))
        best_no_words = list(set(no_words))

        for word in title_list:
            for noWord in best_no_words:
                if noWord == word:
                    return False
        return True

    # Takes a string and returns either a list or a string
    # upper or lower without punctuation marks
    def string_clean(self, dirtyText, listOrString=None):


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



