import os
import unittest

from app import app, db

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


    def test_found(self):
        response = self.found()
        self.assertEqual(response.status_code, 200)

# Helpers

    def found(self, test_func='True', dunderSearch='Post Black Metal',
              sliderRange=50, nextToken='None'):
        return self.app.post('/search/found_album', data=dict(test_func=test_func,
                             dunderSearch=dunderSearch, sliderRange=sliderRange,
                             nextToken=None), follow_redirects=True)

if __name__ == "__main__":
    unittest.main()
