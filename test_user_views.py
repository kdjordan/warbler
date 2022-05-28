"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
def echo(element):
    print(f'***********  {element}')

class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_index(self):
        """Are we getting the correct user when logging in ?"""
        with self.client as c:
            res = c.get('/users')
            self.assertIn('778', str(res.data))
            self.assertIn('884', str(res.data))
            self.assertIn('@abc', str(res.data))
            self.assertIn('@hij', str(res.data))

    def test_user_search(self):
        """Are we getting the correct user index searching ?"""
        with self.client as c:
            res = c.get(f'/users?q={self.u1.username}', follow_redirects=True)
            res2 = c.get(f'/users?q={self.u2.username}', follow_redirects=True)
            
            self.assertIn('@abc', str(res.data))
            self.assertIn('@efg', str(res2.data))
            self.assertNotIn('@efg', str(res.data))
            self.assertNotIn('@abc', str(res2.data))

    def test_user_show(self):
        """Are we getting the correct user index searching ?"""
        with self.client as c:
            res = c.get(f'/users/{self.testuser_id}')
            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', str(res.data))

    def setup_likes(self):
        """Setup likes for the following tests"""
        m1 = Message(text='New Mssg', user_id=f'{self.testuser.id}')
        m2 = Message(text='New Mssg2', user_id=f'{self.testuser.id}')
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1,m2,m3])
        db.session.commit()

        l1 = Likes(user_id=self.testuser_id, message_id=9876)

        db.session.add(l1)
        db.session.commit()

    def test_user_show_with_likes(self):
        """Can we see likes when logging in ?"""
        self.setup_likes()

        with self.client as c:
            res = c.get(f'/users/{self.testuser_id}')
            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', str(res.data))
            self.assertIn('likes', str(res.data))
            self.assertIn("@testuser", str(res.data))
            soup = BeautifulSoup(str(res.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)


    def test_add_like(self):
        m = Message(id=1234, text="New test mssg", user_id=f'{self.u1_id}')
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post('/users/add_like/1234', follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==1234).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

        
    def test_remove_like(self):
        self.setup_likes()

        m = Message(id=109, text="New test mssg", user_id=f'{self.u1_id}')
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # remove like
            res = c.post('/users/add_like/9876', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==9876).all()
            self.assertEqual(len(likes), 0)

    def test_unauth_like(self):
        self.setup_likes()

        with self.client as c:
            # remove like
            res = c.post('/users/add_like/9876', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized", str(res.data))
            likes = Likes.query.filter(Likes.message_id==9876).all()
            self.assertEqual(len(likes), 1)
            
    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_user_with_follows(self):
        self.setup_followers()

        with self.client as c:
            res = c.get(f'/users/{self.testuser_id}', follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', str(res.data))
            
            soup = BeautifulSoup(str(res.data), 'html.parser')
            found = soup.find_all('li', {'class':'stat'})
            self.assertEqual(len(found), 4)
            # test for a count of 0 messages
            self.assertIn("0", found[0].text)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)

            # Test for a count of 0 likes
            self.assertIn("0", found[3].text)

    def test_show_following(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@abc", str(resp.data))
            self.assertIn("@efg", str(resp.data))
            self.assertNotIn("@hij", str(resp.data))
            self.assertNotIn("@testing", str(resp.data))

    def test_show_followers(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@abc", str(resp.data))
            self.assertNotIn("@efg", str(resp.data))
            self.assertNotIn("@hij", str(resp.data))
            self.assertNotIn("@testing", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))



            