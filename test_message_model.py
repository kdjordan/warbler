"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from datetime import datetime

from models import db, User, Message, Follows
def echo(name):
    print(f'***********{name}')

from unittest.mock import patch
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        time = datetime.now().astimezone()
        m1 = Message(text="test", timestamp=time, user_id=1111)
        mid1 = 11

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        m1 = Message.query.get(mid1)

        self.u1 = u1
        self.uid1 = uid1

        self.m1 = m1
        self.mid1 = mid1
        # self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_create_mssg_success(self):
        time = datetime.now().astimezone()
        m2 = Message(text="test mssg", timestamp=time, user_id=1111)
        m2.id = 11
        db.session.add(m2)
        db.session.commit()

        mssg = Message.query.get(m2.id)
        self.assertEqual(mssg.id, m2.id)

    def test_fail_user_id(self):
        m2 = Message(text="test mssg", timestamp=None, user_id=3)
        m2.id = 13
        db.session.add(m2)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_fail_mssg(self):
        time = datetime.now().astimezone()
        m2 = Message(text=None, timestamp=time, user_id='1111')
        m2.id = 16
        db.session.add(m2)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


   