import os
import unittest

from app import app, db
from app.search_module.search_functions import year_selecter, \
     criteria_alter, search_getter, stat_checker, comment_counter

TEST_DB = 'test.db'


class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

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



# Tests


    def test_dunderbands(self):
        response = self.app.get('/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_year_selecter(self, year=1987):
        self.assertEqual(year_selecter(year),'1987-12-30T00:00:00Z')

    def test_criteria_alter(self, value=None):
        if value == None:
            value = 26
        self.assertEqual(str(criteria_alter(value)), 'MaxViews: 7800 | LikeRatio: 0.0182 | MinCount: 2')

    def test_search_getter(self):
        response = search_getter('Metal')
        self.assertTrue(response != None)
        del response

    def test_stat_checker(self):
        self.assertTrue(stat_checker('aAN9rtgt21w'))

    def test_comment_counter(self):
        response = comment_counter('aAN9rtgt21w')
        self.assertTrue(isinstance(response, str))

# Helpers

    def found(self, test_func='True', dunderSearch='Post Black Metal',
              sliderRange=50, nextToken='None'):
        return self.app.post('/search/found_album', data=dict(test_func=test_func,
                             dunderSearch=dunderSearch, sliderRange=sliderRange,
                             nextToken=None), follow_redirects=True)

if __name__ == "__main__":
    unittest.main()
