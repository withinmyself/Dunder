from flask_login import UserMixin
from app import db, redis_server

import datetime


class Base(db.Model):

    __abstract__ = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())
class User(Base, UserMixin):

    __tablename__ = 'users'

    # Required
    active        = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    username      = db.Column(db.String(100), nullable=True, unique=True)
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password      = db.Column(db.String(255), nullable=False, \
                    server_default='{0:s}'.format(str(redis_server.get('USER_PASS_DEFAULT').decode('utf-8'))))
    # Optional
    first_name    = db.Column(db.String(100), nullable=True, server_default='')
    last_name     = db.Column(db.String(100), nullable=True, server_default='')
    # Relational databases
    favorites     = db.relationship('Favorites')
    ignore        = db.relationship('Ignore')
    comments      = db.relationship('Comments')

    def __repr__(self):
        return 'Username: {0:s} | Email: {1:s}'.format(self.username, self.email)

class Ignore(Base):
    __tablename__ = 'ignore'


    videoId       = db.Column(db.String(100), unique=True)
    videoTitle    = db.Column(db.String(500))

    # Parent for relational
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, videoId, videoTitle):
        self.videoId = videoId
        self.videoTitle = videoTitle

    def __repr__(self):
        return 'VideoID: {0:s} | VideoTitle: {1:s}'.format(self.videoId, self.videoTitle)


class Favorites(Base):
    __tablename__ = 'favorites'


    videoId       = db.Column(db.String(100), unique=True)
    videoTitle    = db.Column(db.String(500))
    videoComments = db.Column(db.String(500), server_default='No Comments')
    # Parent for relational
    user          = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, videoId, videoTitle):
        self.videoId    = videoId
        self.videoTitle = videoTitle

    def __repr__(self):
        return 'VideoID: {0:s} | VideoTitle: {1:s}'.format(self.videoId, self.videoTitle)


class Comments(Base):
    __tablename__ = 'comments'


    word          = db.Column(db.String(500))

    # noword or exciter
    define        = db.Column(db.String(500))

    # Parent for relational
    user          = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, commentWord, define):
        self.commentWord = commentWord
        self.define      = define

    def __repr__(self):
        return 'Type: {0:s} Word: {1:s}'.format(self.define, self.commentWord)







