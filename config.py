import redis
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

redis_server = redis.Redis(os.environ['REDISTOGO_URL'])

# Postgres database link stored in Redis

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
#SQLALCHEMY_DATABASE_URI = redis_server.get('SQL_DATABASE').decode('utf-8')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Look into later
# THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

# Secret key for signing cookies
SECRET_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

# Flask-Mail SMTP server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'withinmyself@gmail.com'
MAIL_PASSWORD = 'ETD0009ED7171'
MAIL_DEFAULT_SENDER = 'withinmyself@gmail.com'

# Flask-User settings
USER_APP_NAME = 'DunderBands'      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = True        # Enable email authentication
USER_ENABLE_USERNAME = False    # Disable username authentication
USER_EMAIL_SENDER_NAME = 'Fatso McGee'
USER_EMAIL_SENDER_EMAIL = 'withinmyself@gmail.com'
