import os
import redis

TEST_DB = 'dunder_unit_test.db'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Flask DEBUG - Updates live development server as changes come in.
DEBUG = True

redis_server = redis.Redis(host='127.0.0.1', port='6379')

SECRET_KEY = redis_server.get('SECRET_KEY').decode('utf-8')
CSRF_SESSION_KEY = redis_server.get('SECRET_KEY').decode('utf-8')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(TEST_DB) # redis_server.get('SQL_DATABASE').decode('utf-8')
SQLALCHEMY_TRACK_MODIFICATIONS = False
