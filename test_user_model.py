"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows
def echo(name):
    print(f'***********{name}')

from unittest.mock import patch
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        """Does follow another user work ?"""
        self.u1.following.append(self.u2)
        db.session.commit()
        # User u1 sould be following 1
        # User u2 should have 1 followers
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.following), 0)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_valid_signup(self):
        u_test = User.signup("test9", "email9@email.com", "password", None)
        uid = 12
        u_test.id = uid

        db.session.add(u_test)
        db.session.commit()

        u_res = User.query.get(uid)
        self.assertEqual(u_res.id, uid)
        self.assertEqual(u_res.username, "test9")
        self.assertEqual(u_res.email, "email9@email.com")
        self.assertEqual(u_res.image_url, "/static/images/default-pic.png")
        self.assertNotEqual(u_res.password, "password")
        
    def test_email_fail(self):
        u_test = User.signup("testering", None, "password", None)
        uid = 12555
        u_test.id = uid
        db.session.add(u_test)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_username_fail(self):
        u_test = User.signup(None, "email9@email.com", "password", None)
        uid = 1253
        u_test.id = uid
        db.session.add(u_test)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_password_fail(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)

    def test_auth_success(self):
        user = User.authenticate(self.u1.username, "password")
        self.assertEqual(user.id, self.u1.id)

    def test_bad_auth_username(self):
        user = User.authenticate("badusername", "password")
        self.assertFalse(user)

    def test_bad_auth_password(self):
        user = User.authenticate(self.u1.username, "notpass")
        self.assertFalse(user)

    