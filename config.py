import redis
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if os.getenv('REDISTOGO_URL') == None:
    redis_server = redis.Redis(host='0.0.0.0', port='6379')
else:
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    redis_server = redis.from_url(redis_url)
# Postgres database link stored in Redis
if os.environ['DATABASE_URL'] == None:
    SQLALCHEMY_DATABASE_URI = redis_server.get('SQL_DATABASE').decode('utf-8')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
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
