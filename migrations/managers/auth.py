from datetime import datetime, timedelta, timezone

import jwt

from decouple import config
from flask_httpauth import HTTPTokenAuth

from db import db
from models.user import UserModel


class Authenticate:

    @staticmethod
    def encode_token(user: type[UserModel]):

        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=2),
            "sub": user.id,
        }

        token = jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")

        return token

    @staticmethod
    def decode_token(token):

        try:
            payload = jwt.decode(token, config("SECRET_KEY"), algorithms=["HS256"])
        except Exception as ex:
            raise ex

        return payload["sub"]


auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    try:
        user_id = Authenticate.decode_token(token)
        user = db.session.execute(
            db.select(UserModel).filter_by(id=user_id)
        ).scalar_one()
    except Exception as ex:
        raise ex

    return user
