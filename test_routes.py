import os
import unittest

from app import app, db
from app.search_module.search_functions import year_selecter, \
     search_getter, stat_checker, comment_counter, criteria_crunch, \
     title_clean, string_clean, random_genre
from app.settings_module.settings_functions import *
TEST_DB = 'test.db'


class BasicTests(unittest.TestCase):

# Setup and teardown

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

        # Disable sending emails during unit testing
        # mail.init_app(app)
        # self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass



# Search Module Tests


    def test_dunderbands(self):
        response = self.app.get('/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_dunderbands_post(self):
        response = self.app.post('/search', data=dict(videoId='aEiOu',
                   dunderSearch='Post Metal France', publishedBefore=2018,
                   publishedAfter=2015, nextToken=None),follow_redirects=True)
        self.assertIn(b'Change Search', response.data)


    def test_year_selecter(self, year=1987):
        self.assertEqual(year_selecter(year),'1987-12-30T00:00:00Z')


    def test_search_getter(self):
        response = search_getter('Metal')
        self.assertTrue(response != None)
        del response

    def test_stat_checker(self):
        self.assertTrue(stat_checker('aAN9rtgt21w'))

    def test_comment_counter(self):
        response = comment_counter('aAN9rtgt21w')
        self.assertTrue(isinstance(response, str))

    def test_criteria_crunch(self):
        response = criteria_crunch('Post Black Metal', publishedBefore=2018,
                                   publishedAfter=2016)
        self.assertTrue(response != None)

    def test_title_clean_true(self):
        response = title_clean('Pantera Cowboys From Hell')
        self.assertTrue(response)

    def test_title_clean_false(self):
        response = title_clean('Pantera All-time Relaxing Greatest Hits')
        self.assertFalse(response)

    def test_string_clean_lower_list(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='listNeededLower')
        testList = isinstance(response, list)
        testLower = str(response)
        self.assertTrue(testList and testLower)


    def test_string_clean_upper_lower_string(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='stringNeededLower')
        self.assertTrue(response.islower() and isinstance(response, str))

    def test_string_clean_lower_upper_list(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='listNeededUpper')
        testList = isinstance(response, list)
        testUpper = str(response).isupper()
        self.assertTrue(testList and testUpper)


    def test_string_clean_lower_upper_string(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='stringNeededUpper')
        self.assertTrue(response.isupper() and isinstance(response, str))


    def test_string_clean_lower_upper_string(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='listNeeded')
        self.assertTrue(isinstance(response, list))

    def test_string_clean_lower_upper_string(self):
        response = string_clean('TesTiNg oUt StrING cLeAn',
                                listOrString='stringNeeded')
        self.assertTrue(isinstance(response, str))


    def test_string_clean_lower_upper_string(self):
        with self.assertRaises(TypeError):
            string_clean()

    def test_random_genre(self):
        response = random_genre()
        self.assertTrue(isinstance(response, str))





# Settings Module Tests

    def test_change_like_ratio(self):
        change_like_ratio(0.018)
        float_ratio= float(str(redis_server.get('LIKE_RATIO').decode('utf-8')))
        is_float = isinstance(float_ratio, float)
        is_correct = float_ratio == 0.018
        self.assertTrue(is_float and is_correct)

    def test_get_like_ratio(self):
        current_ratio = str(redis_server.get('LIKE_RATIO').decode('utf-8'))
        response = get_like_ratio()
        self.assertEqual(current_ratio, response)

    def test_change_comments_needed(self):
        change_comments_needed(2)
        comments = int(str(redis_server.get('MIN_COUNT').decode('utf-8')))
        is_int = isinstance(comments, int)
        is_correct = comments == 2
        self.assertTrue(is_int and is_correct)

    def test_get_comments_needed(self):
        current_comments = str(redis_server.get('MIN_COUNT').decode('utf-8'))
        response = get_comments_needed()
        self.assertEqual(current_comments, response)

    def test_get_ignore(self):
        response = get_ignore()
        is_list = isinstance(response, list)
        self.assertTrue(is_list)

    def test_add_ignore(self):
        add_ignore('UNIT_TEST', videoTitle='ADD_IGNORE')
        is_there = db.session.query(Ignore).filter_by(videoId='UNIT_TEST').first()
        is_obj = isinstance(is_there, object)
        self.assertTrue(is_obj)

    def test_delete_ignore(self):
        delete_ignore('UNIT_TEST')
        is_there = db.session.query(Ignore).filter_by(videoId='UNIT_TEST').first()
        is_obj = is_there == None
        self.assertTrue(is_obj)

    def test_get_favorites(self):
        response = get_favorites()
        is_list = isinstance(response, list)
        self.assertTrue(is_list)

    def test_add_favorite(self):
        add_favorite('UNIT_TEST', videoTitle='ADD_IGNORE')
        is_there = db.session.query(Favorites).filter_by(videoId='UNIT_TEST').first()
        is_obj = isinstance(is_there, object)
        self.assertTrue(is_obj)

    def test_delete_favorite(self):
        delete_favorite('UNIT_TEST')
        is_there = db.session.query(Favorites).filter_by(videoId='UNIT_TEST').first()
        is_obj = is_there == None
        self.assertTrue(is_obj)

    def test_get_max_views(self):
        current_max_views = str(redis_server.get('MAX_VIEWS').decode('utf-8'))
        self.assertEqual(current_max_views, get_max_views())

    def test_change_max_views(self):
        change_max_views(20000)
        current_max_views = int(str(redis_server.get('MAX_VIEWS').decode('utf-8')))
        self.assertEqual(current_max_views, 20000)









# Helpers


if __name__ == "__main__":
    unittest.main()
