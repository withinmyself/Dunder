from app import db



# Base model for all other database classes to inherit
class Base(db.Model):

    __abstract__ = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())

class Ignore(Base):
    __tablename__ = 'ignore'

    videoId = db.Column(db.String(100), unique=True)
    videoTitle = db.Column(db.String(500))

    def __init__(self, videoId, videoTitle):
        self.videoId = videoId
        self.videoTitle = videoTitle

    def __repr__(self):
        return 'VideoID: {0:s} | VideoTitle: {1:s}'.format(self.videoId, self.videoTitle)


class Favorites(Base):
    __tablename__ = 'favorites'


    videoId = db.Column(db.String(100), unique=True)
    videoTitle = db.Column(db.String(500))

    def __init__(self, videoId, videoTitle):
        self.videoId = videoId
        self.videoTitle = videoTitle

    def __repr__(self):
        return 'VideoID: {0:s} | VideoTitle: {1:s}'.format(self.videoId, self.videoTitle)


class Comments(Base):
    __tablename__ = 'comments'


    commentWord = db.Column(db.String(500))
    define = db.Column(db.String(500))

    def __init__(self, commentWord, define):
        self.commentWord = commentWord
        self.define = define

    def __repr__(self):
        return 'Desirable Comment: {0}'.format(self.commentWord)





















db.create_all()

