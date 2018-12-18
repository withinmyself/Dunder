import redis
redis_server = redis.Redis(host='127.0.0.1', port='6379')
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = redis_server.get('SQL_DATABASE').decode('utf-8')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

# Secret key for signing cookies
SECRET_KEY = redis_server.get('SECRET_KEY').decode('utf-8')
