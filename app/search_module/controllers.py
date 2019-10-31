import datetime
import re

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify
from flask_login import login_required

from app.users_module.controllers import current_user
from app import db, redis_server, login_manager
from app.users_module.controllers import load_user
from app.users_module.models import Favorites
from app.search_module.models import Albums
from app.search_module.search_methods import Search

search = Search()
search_routes = Blueprint('search', __name__, url_prefix='/')

@search_routes.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return render_template(
                'search/dunderbands.html',
                current_user=current_user)
        else:
            flash("You Need To Login Or Signup First.")
            return redirect('users/login')
    else:
        if current_user.is_authenticated:
            try:
                dunder_anchor = request.form['videoId']
            except KeyError:
                dunder_anchor = None
            try:
                prefix           = request.form['prefix']
                subgenre         = request.form['subgenre']
                genre            = request.form['genre']
                country          = request.form['country']
                redis_server.set('PREFIX', len(prefix))
                redis_server.set('SUBGENRE', len(subgenre))
                redis_server.set('COUNTRY', len(country))
                dunder_request    = '{0:s} {1:s} {2:s} {3:s}'.format(
                                    prefix, subgenre, genre, country)
            except KeyError:
                dunder_request    = request.form['dunderRequest']
            dunder_search = re.sub(r'[.!,;?]', ' ', dunder_request).upper()

            published_before = datetime.datetime(int(request.form['publishedBefore']),12,30).isoformat()+'Z'
            published_after = datetime.datetime(int(request.form['publishedAfter']),12,30).isoformat()+'Z'

            try:
                next_token        = request.form['nextToken']
            except KeyError:
                next_token        = None
            db.session.query(Albums).delete()
            db.session.query(Favorites).filter_by(videoTitle='Not Given').delete()
            db.session.commit()
            current_band          = search.criteria_crunch(
                dunder_search     = dunder_search,
                published_before  = published_before,
                published_after   = published_after,
                next_token        = next_token,
                dunder_anchor     = dunder_anchor)
        else:
            return redirect('users/login')
            flash("You Need To Login First - Click Signup If You Don't Have A Username Yet")
        if current_band == None or current_band == False:
            flash('Search String Exausted | Double Your Efforts')
            return redirect('/')
        else:
            return render_template (
                'search/results.html',
                 currentBand     = current_band,
                 published_before = published_before,
                 published_after  = published_after,
                 current_user    = current_user)

#@search_routes.route('/look', methods=['GET'])
#def look():

#    dunder_search = 'METAL DOOM'

#    next_token = None
#    dunder_anchor = None

#    published_before = datetime.datetime(2018,12,30).isoformat()+'Z'
#    published_after = datetime.datetime(2018,12,30).isoformat()+'Z'

#    current_band = search.criteria_crunch(
#      dunder_search = dunder_search,
#      published_before = published_before,
#      published_after = published_after,
#      next_token = next_token,
#      dunder_anchor = dunder_anchor)

#    package = [
#      {'videoId': current_band.videoId}
#    ]

#    return jsonify(package)
