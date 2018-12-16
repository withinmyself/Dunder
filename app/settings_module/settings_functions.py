from app import db, redis_server
from app.settings_module.models import Ignore, Favorites

def change_like_ratio(ratio):
    float_ratio = float(ratio)
    redis_server.set('LIKE_RATIO', float_ratio)

def get_like_ratio():
    like_ratio = redis_server.get('LIKE_RATIO').decode('utf-8')
    return str(like_ratio)

def change_comments_needed(amount):
    int_amount = int(amount)
    redis_server.set('MIN_COUNT', int_amount)

def get_comments_needed():
    comments_needed = redis_server.get('MIN_COUNT').decode('utf-8')
    return str(comments_needed)

def get_ignore():
    ignore_list = db.session.query(Ignore).all()
    for ignore in ignore_list:
        print(ignore)

def add_ignore(videoId, videoTitle='Not Given'):
    ignore = Ignore(videoId, videoTitle)
    db.session.add(ignore)
    db.session.commit()
    db.session.close()

def delete_ignore(videoId):
    str_videoId = str(videoId)
    db.session.query(Ignore).filter_by(videoId=str_videoId).delete()
    db.session.commit()
    db.session.close()

def get_favorites():
    favorites_list = db.session.query(Ignore).all()
    for favorite in favorites_list:
        print(favorite)


def add_favorite(videoId, videoTitle='Not Given'):
    str_videoId = str(videoId)
    favorite = Favorites(str_videoId, videoTitle)
    db.session.add(favorite)
    db.session.commit()
    db.session.close()


def delete_favorite(videoId):
    str_videoId = str(videoId)
    db.session.query(Favorites).filter_by(videoId=str_videoId).delete()
    db.session.commit()
    db.session.close()




