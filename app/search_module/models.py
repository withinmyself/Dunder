from app import db



# Base model for all other database classes to inherit
class Base(db.Model):

    __abstract__ = True

    id            = db.Column(db.Integer, primary_key=True)
    # date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    # date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
    #                                        onupdate=db.func.current_timestamp())

class Albums(Base):
    __tablename__ = 'albums'

    videoId = db.Column(db.String(100), unique=True)
    nextToken = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    videoTitle = db.Column(db.String(500))
    topComment = db.Column(db.String(10000))
    isFavorite = db.Column(db.String(100))

    def __init__(self, videoId, nextToken, genre, videoTitle, topComment, isFavorite):
        self.videoId = videoId
        self.nextToken = nextToken
        self.genre = genre
        self.videoTitle = videoTitle
        self.topComment = topComment
        self.isFavorite = isFavorite
        super(Albums, self).__init__

    def __repr__(self):
        return 'VideoID: {0:s}, Genre: {1:s}'.format(self.videoId, self.genre)

db.create_all()

