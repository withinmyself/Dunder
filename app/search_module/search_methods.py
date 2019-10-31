import re

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

from app.search_module.models import Albums
from app.users_module.models import Favorites, Ignore, Comments
from app.users_module.controllers import current_user
from app.settings_module.redis_access import RedisAccess
from app import db, redis_server

DEVELOPER_KEY = redis_server.get('DEVELOPER_KEY').decode('utf-8')

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

redis = RedisAccess()

class Search:

    def __init__(self):
        pass

    # API interaction to YouTube.
    def _search_getter(self,
        q, max_results=1, video_duration='long', 
        token=None, location=None,
        location_radius=None, related_video=None,
        published_before=None, published_after=None):

        if redis.get_video_length() == 'short':
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
    def _stat_checker (self, videoId):

        like_ratio = redis.get_like_ratio()
        view_ratio = redis.get_view_ratio()
        max_views = redis.get_max_views()

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

    def _preference_check(self, videoId): 
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
    def _comment_getter (self, videoId):
        try:
            comments = YOUTUBE.commentThreads().list (
                                    part="snippet",
                                    maxResults=100,
                                    videoId=videoId,
                                    textFormat="plainText").execute()
            return comments
        except HttpError:
            print("Comments disabled")
            return False

    def _comment_word_counter(self, comments, all_yes_words):

        redis_server.set('TOTAL_WORDS', 0)
        words_needed = redis.get_comments_needed()

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

    # Check list of words that might pull in 'mix' videos,
    # compilations and 'best of' lists.
    def _title_clean (self, tube_title, include_search='search', include_band='band'):

        title_list = re.sub(r'[.!,;?]', ' ', tube_title).lower().split()

        # This gives us the option to add extra words or band names.
        no_words = redis.get_no_words()
        no_words.append('{0}'.format(include_search))
        no_words.append('{0}'.format(include_band))

        for word in title_list:
            for no in no_words:
                if no == word:
                    return False
        return True


    # Main search method.  Bring everything together.
    def criteria_crunch (
            self,
            dunder_search=None, 
            published_before=None, 
            published_after=None, 
            next_token=None, 
            dunder_anchor=None):

        x = 0
        cycle = redis.get_how_long()
        while x <= cycle:
            x += 1
            search_results = self._search_getter (
                            dunder_search,
                            token=next_token,
                            related_video=dunder_anchor,
                            published_before=published_before,
                            published_after=published_after)
            print(x)
            try:
                next_token = search_results['nextPageToken']
            except KeyError:
                print("End of pages.")
                next_token = None

            for video in search_results.get('items', []):
                videoId = video['id']['videoId']
                video_title = video['snippet']['title']
                is_video = video['id']['kind'] == 'youtube#video'
                no_words_free = self._title_clean(video_title,
                                    include_search=dunder_search)

                # Automatically add to ignore list if not correct type or 
                # if the title contains misleading information. 
                if no_words_free or is_video == False:
                    if db.session.query(Ignore).filter_by(videoId=videoId).first() == None:
                        ignore = Ignore(videoId, video_title)
                        db.session.add(ignore)
                        db.session.commit()

                user_wants = self._preference_check(videoId)
                stats_match = self._stat_checker(videoId=videoId)

                if is_video and no_words_free and user_wants and stats_match:

                    try:
                        check_comments = self._comment_word_counter(
                            comments=self._comment_getter(videoId=videoId), 
                            all_yes_words=redis.get_yes_words())
                    except TypeError:
                        print("Comments unavailable")
                        check_comments = False

                    if check_comments != False:
                        current_band = Albums (
                            videoId=videoId, nextToken=next_token,
                            genre=dunder_search.upper(), videoTitle=video_title,
                            topComment=check_comments)

                        db.session.add(current_band)
                        db.session.commit()
                        return current_band
