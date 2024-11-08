from decouple import config
from flask_testing import TestCase

from config import create_app
from db import db
from managers.auth import AuthManager


def generate_token(user):

    return AuthManager.encode_token(user)


class BaseTestCase(TestCase):

    def create_app(self):

        environment = config("TEST_ENVIRONMENT")
        return create_app(environment)

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()
