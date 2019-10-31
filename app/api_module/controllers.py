from flask import request, jsonify
from app import app
from app.search_module.search_methods import Search
import datetime

from flask import Blueprint, request, jsonify
from app import db, redis_server, login_manager
from app.users_module.models import Ignore, Favorites
from app.users_module.controllers import current_user
from app.settings_module.redis_access import RedisAccess
from app.search_module.models import Albums

search = Search()
redis = RedisAccess()

api_routes = Blueprint('api', __name__, url_prefix='/api')

@api_routes.route('/search', methods=['GET'])
def api_search():

    dunder_search = str(request.args['dunder_search'])
    full_album = request.args['full_album']
    new_release = request.args['new_release']

    next_token = None
    dunder_anchor = None

    if full_album:
        redis.change_video_length('long')
    else:
        redis.change_video_length('short')

    if new_release:
        published_before = datetime.datetime(2019,1,30).isoformat()+'Z'
        published_after = datetime.datetime(2017,12,30).isoformat()+'Z'

    current_band = search.criteria_crunch(
      dunder_search = dunder_search,
      published_before = published_before,
      published_after = published_after,
      next_token = next_token,
      dunder_anchor = dunder_anchor)

    package = [
      {'videoId': current_band.videoId,
      'top_comment': current_band.topComment}
    ]

    return jsonify(package)


@api_routes.route('/continue', methods=['GET'])
def api_continue():


    next_token = redis.get_token()
    current_band = search.criteria_crunch(
      dunder_search = dunder_search,
      published_before = published_before,
      published_after = published_after,
      next_token = next_token,
      dunder_anchor = dunder_anchor)

@api_routes.route('/anchor_pivot', methods=['GET'])
def api_search():

@api_routes.route('/ignore', methods=['GET'])
def api_search():

@api_routes.route('/make_favorite', methods=['GET'])
def api_search():

@api_routes.route('/favorites', methods=['GET'])
def api_search():