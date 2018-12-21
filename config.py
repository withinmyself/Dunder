import redis
redis_server = redis.Redis(host='127.0.0.1', port='6379')
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Postgres database link stored in Redis
SQLALCHEMY_DATABASE_URI = redis_server.get('SQL_DATABASE').decode('utf-8')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Look into later
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

# Secret key for signing cookies
SECRET_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

# Flask-Mail SMTP server settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USE_TLS = False
MAIL_USERNAME = redis_server.get('USERNAME').decode('utf-8')
MAIL_PASSWORD = redis_server.get('PASSWORD').decode('utf-8')
MAIL_DEFAULT_SENDER = redis_server.get('DEFAULT_SENDER').decode('utf-8')

# Flask-User settings
USER_APP_NAME = 'DunderBands'      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = True        # Enable email authentication
USER_ENABLE_USERNAME = False    # Disable username authentication
USER_EMAIL_SENDER_NAME = USER_APP_NAME
USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
