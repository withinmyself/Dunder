from app import redis_server

class RedisAccess():
    """Access lists, keys and passwords through Redis."""

    def __init__(self):
        pass

    def get_no_words(self):
        no_words_bytes = redis_server.lrange('NO_WORDS', 1, -1)
        no_words = []
        for word in no_words_bytes:
            no_words.append(word.decode('utf-8'))
        return no_words

    def add_no_word(self, no_word):
        redis_server.lpush('NO_WORD', no_word)
        return True

    def remove_no_word(self, no_word):
        no_word_bytes = bytes(no_word, encoding="ascii")
        redis_server.lrem('NO_WORD', no_word_bytes)
        return True

    def get_yes_words(self):
        yes_words_bytes = redis_server.lrange('YES_WORDS', 1, -1)
        yes_words = []
        for word in yes_words_bytes:
            yes_words.append(word.decode('utf-8'))
        return yes_words

    def add_yes_word(self, yes_word):
        redis_server.lpush('YES_WORD', yes_word)
        return True

    def remove_yes_word(self, yes_word):
        yes_word_bytes = bytes(yes_word, encoding="ascii")
        redis_server.lrem('YES_WORD', yes_word_bytes)
        return True

    # Access or change custom criteria
    def change_like_ratio(self, ratio):
        redis_server.set('LIKE_RATIO', ratio)
        return True

    def get_like_ratio(self):
        return float(str(redis_server.get('LIKE_RATIO').decode('utf-8')))

    def change_comments_needed(self, amount):
        redis_server.set('COMMENTS_REQUESTED', amount)
        return True

    def get_comments_needed(self):
        return int(str(redis_server.get('COMMENTS_REQUESTED').decode('utf-8')))

    def change_max_views(self, amount):
        redis_server.set('MAX_VIEWS', amount)
        return True

    def get_max_views(self):
        return int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))

    def change_view_ratio(self, amount):
        redis_server.set('VIEW_RATIO', amount)
        return True

    def get_view_ratio(self):
        return float(str(redis_server.get('VIEW_RATIO').decode('utf-8')))

    def is_full_album(self):
        return redis_server.get('FULL_ALBUM').decode('utf-8')

    def change_how_long(self, cycle):
        redis_server.set('CYCLE', cycle)
        return True

    def get_how_long(self):
        return int(str(redis_server.get('CYCLE').decode('utf-8')))

    def change_video_length(self, length):
        redis_server.set('VIDEO_LENGTH', length)
        return True

    def get_video_length(self):
        return str(redis_server.get('VIDEO_LENGTH').decode('utf-8'))

    def change_token(self, token):
        redis_server.set('PAGE_TOKEN', token)
        return True

    def get_token(self):
        return str(redis_server.get('PAGE_TOKEN').decode('utf-8')) 