from flask import request, jsonify
from app import app
from app.search_module.search_functions import criteria_crunch
import datetime

@app.route('/api/react/endpoint/look', methods=['GET'])
def look():
    if 'dunder_search' in request.args:
        dunder_search = str(request.args['prefix'])
    else:
        dunder_search = 'metal'

    next_token = None
    dunder_anchor = None

    published_before = datetime.datetime(int(request.form['publishedBefore']),12,30).isoformat()+'Z'
    published_after = datetime.datetime(int(request.form['publishedAfter']),12,30).isoformat()+'Z'

    current_band = criteria_crunch(
      dunder_search = dunder_search,
      published_before = published_before,
      published_after = published_after,
      next_token = next_token,
      dunder_anchor = dunder_anchor)

    package = [
      {'videoId': current_band.videoId}
    ]

    return jsonify(package)