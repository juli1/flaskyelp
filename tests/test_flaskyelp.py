"""
Test for flaskyelp

:copyright: (c) Julien Delange
"""

import os
import unittest
import tempfile

import flaskyelp

class FlaskYelpTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskyelp.app.config['DATABASE'] = tempfile.mkstemp()
        flaskyelp.app.config['TESTING'] = True
        self.app = flaskyelp.app.test_client()

        with flaskyelp.app.app_context():
            flaskyelp.flaskyelp.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskyelp.app.config['DATABASE'])




    def register(self, username, password, email):
        return self.app.post('/register', data=dict(username=username, password=password,password2=password,email=email), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def test_empty_db (self):
        """Test the basic messages we have when the database is empty"""
        rv = self.app.get('/')
        assert b'come back later' in rv.data
        assert b'no place' in rv.data

    def test_register_and_login (self):
        """Test to register and login succesfully"""
        rv = self.register ("julien", "test","toto@toto.fr")
        assert b'You were successfully registered and can login now' in rv.data
        rv = self.login ("julien", "test")
        assert b'sign out' in rv.data

    def test_register_twice (self):
        """Test to register somebody twice with the same username.
        should obviously fail"""
        rv = self.register ("julien", "test","toto@toto.fr")
        rv = self.register ("julien", "test","toto@toto.fr")
        assert b'The username is already taken' in rv.data

    def test_add_restaurant (self):
        """Try to add a restaurant. Check the restaurant is in the
           front page and that the default text is no longer there
        """
        self.register ("julien", "test","toto@toto.fr")
        self.login ("julien", "test")
        self.app.post('/place/new', data=dict(name="very good place", address="downtown place", city="pittsburgh", zipcode="15101"), follow_redirects=True)
        rv = self.app.get('/')
        assert b'very good place' in rv.data
        assert (b'no place' in rv.data) == False

    def test_post_review (self):
        "Try to test that a valid review"
        self.register ("julien", "test","toto@toto.fr")
        self.login ("julien", "test")
        self.app.post('/place/new', data=dict(name="very good place", address="downtown place", city="pittsburgh", zipcode="15101"), follow_redirects=True)
        self.app.post('/place/1/comment/new', data=dict(title="mytitle1", content="amazing place", rating="2"), follow_redirects=True)
        rv = self.app.get('/')
        assert b'very good place' in rv.data
        assert b'mytitle1' in rv.data

    def test_rating_average (self):
        "Test the average of review. We post one review with 4, one review with 2 and check that the average is 3."
        self.register ("julien", "test","toto@toto.fr")
        self.login ("julien", "test")
        self.app.post('/place/new', data=dict(name="very good place", address="downtown place", city="pittsburgh", zipcode="15101"), follow_redirects=True)
        self.app.post('/place/1/comment/new', data=dict(title="mytitle1", content="amazing place", rating="2"), follow_redirects=True)
        self.app.post('/place/1/comment/new', data=dict(title="mytitle2", content="amazing place", rating="4"), follow_redirects=True)
        rv = self.app.get('/place/1')
        assert b'(3.0)' in rv.data

    def test_logout (self):
        """Test to login and logout """
        rv = self.register ("julien", "test","toto@toto.fr")
        assert b'You were successfully registered and can login now' in rv.data
        rv = self.login ("julien", "test")
        assert b'sign out' in rv.data
        self.app.get('/logout')
        rv = self.app.get('/')
        assert b'register' in rv.data

if __name__ == '__main__':
    unittest.main()
