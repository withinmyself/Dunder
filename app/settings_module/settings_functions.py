from app import redis_server

# change and get functions for LIKE_RATIO, MIN_COUNT, MAX_VIEWS, VIEW_RATIO
def change_like_ratio(ratio):
    redis_server.set('LIKE_RATIO', ratio)

def get_like_ratio():
    return float(str(redis_server.get('LIKE_RATIO').decode('utf-8')))

def change_comments_needed(amount):
    redis_server.set('MIN_COUNT', amount)

def get_comments_needed():
    return int(str(redis_server.get('MIN_COUNT').decode('utf-8')))

def change_max_views(amount):
    redis_server.set('MAX_VIEWS', amount)

def get_max_views():
    return int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))

def change_view_ratio(amount):
    redis_server.set('VIEW_RATIO', amount)

def get_view_ratio():
    return float(str(redis_server.get('VIEW_RATIO').decode('utf-8')))




