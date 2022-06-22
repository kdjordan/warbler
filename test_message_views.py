"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"
def echo(name):
    print(f'***********{name}')

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


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

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_show_homepage(self):
        """Do we see non logged in view on intitial render ?"""

        with self.client as c:
            res = c.get("/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('What\'s Happening', html)

    def test_show_login(self):
        """Do we see our login form ?"""

        with self.client as c:
            res = c.get("/login")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Welcome back', html)

    def test_show_profile_page_on_login(self):
        """Do we see our handle after we login successfully"""

        with self.client as c:
            res = c.post("/login", data={'username':'testuser', 'password':'testuser'}, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', html)

    def test_show_fail_protected(self):
        """Can we not see profile if not logged in - redirect to splash page """

        with self.client as c:
            res = c.get("/users/111", follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('What\'s Happening', html)

    def test_show_fail_add_mssg(self):
        """Are we unable to add mssg since we are not logged in ? """

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Access unauthorized.', html)

    def test_mssg_show(self):
        """Are we able to add message with valid info ?"""
        mssg = Message(
            id=1222,
            text= 'test text',
            user_id= self.testuser.id
        )
        db.session.add(mssg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            rec_mssg = Message.query.get(1222)
            res = c.get(f'/messages/{rec_mssg.id}')

            self.assertEqual(res.status_code, 200)
            self.assertIn(rec_mssg.text, str(res.data))

    def test_invalid_message_show(self):
        """Do we get rejected if our mssg ID does not exist ?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        resp = c.get('/messages/99999999')

        self.assertEqual(resp.status_code, 302)

    def test_mssg_delete(self):
        """Can we delete mssg with auth ?"""
        mssg = Message(
            id=1234,
            text= 'test text',
            user_id= self.testuser.id
        )
        db.session.add(mssg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/1234/delete', follow_redirects=True)
            m = Message.query.get(1234)
            self.assertEqual(resp.status_code, 200)
            self.assertIsNone(m)

    def test_unauth_mssg_delete_no_auth(self):
        """Can we not delete mssg with no auth ?"""
        mssg = Message(
            id=1234,
            text= 'test text',
            user_id= self.testuser.id
        )
        db.session.add(mssg)
        db.session.commit()

        with self.client as c:
            resp = c.post('/messages/1234/delete', follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
            m = Message.query.get(1234)
            self.assertIsNotNone(m)