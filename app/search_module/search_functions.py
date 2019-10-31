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
def criteria_crunch (
        dunder_search, 
        published_before=None, 
        published_after=None, 
        next_token=None, 
        dunder_anchor=None):

    x = 0
    while x <= 100:
        x += 1
        search_results = search.search_getter (
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
            no_words_free = search.title_clean(video_title,
                                include_search=dunder_search)

            # Automatically add to ignore list if not correct type or if the title contains misleading information. 
            if no_words_free or is_video == False:
                if db.session.query(Ignore).filter_by(videoId=videoId).first() == None:
                    ignore = Ignore(videoId, video_title)
                    db.session.add(ignore)
                    db.session.commit()

            user_wants = search.preference_check(videoId)
            stats_match = search.stat_checker(videoId=videoId)

            if is_video and no_words_free and user_wants and stats_match:

                try:
                    check_comments = search.comment_word_counter(
                        comments=search.comment_getter(videoId=videoId), 
                        all_yes_words=search.get_yes_words())
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
