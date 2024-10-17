from werkzeug.exceptions import Conflict, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import Authenticate
from models.enums import RolesEnum
from models.user import UserModel


class UserManager:

    @staticmethod
    def login(data):

        user = db.session.execute(
            db.select(UserModel).filter_by(email=data["email"])
        ).scalar()

        if user and check_password_hash(user.password, data["password"]):
            return Authenticate.encode_token(user)

        raise NotFound("User not found")

    @staticmethod
    def register(data):

        data["password"] = generate_password_hash(
            data["password"], method="pbkdf2:sha256"
        )
        data["role"] = RolesEnum.customer.name
        user = UserModel(**data)

        db.session.add(user)
        db.session.flush()

        return Authenticate.encode_token(user)

    @staticmethod
    def create_user(data):

        data["password"] = generate_password_hash(
            data["password"], method="pbkdf2:sha256"
        )
        user = UserModel(**data)

        db.session.add(user)
        db.session.flush()

    @staticmethod
    def delete_user(user_id: int):

        user = UserManager.get_user(user_id)
        db.session.delete(user)
        db.session.flush()

    @staticmethod
    def change_password(user: UserModel, data):

        if not check_password_hash(user.password, data["old_password"]):
            raise Conflict("Invalid password")

        user.password = generate_password_hash(
            data["new_password"], method="pbkdf2:sha256"
        )
        db.session.add(user)
        db.session.flush()
