from app import redis_server

class Criteria:
    """All functions for altering and obtaining criteria"""
    
    def __init__(self):
      pass

    def change_like_ratio(self, ratio):
        redis_server.set('LIKE_RATIO', ratio)

    def get_like_ratio(self):
        return float(str(redis_server.get('LIKE_RATIO').decode('utf-8')))

    def change_comments_needed(self, amount):
        redis_server.set('MIN_COUNT', amount)

    def get_comments_needed(self):
        return int(str(redis_server.get('MIN_COUNT').decode('utf-8')))

    def change_max_views(self, amount):
        redis_server.set('MAX_VIEWS', amount)

    def get_max_views(self):
        return int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))

    def change_view_ratio(self, amount):
        redis_server.set('VIEW_RATIO', amount)

    def get_view_ratio(self):
        return float(str(redis_server.get('VIEW_RATIO').decode('utf-8')))
