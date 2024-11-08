from sqlalchemy.exc import IntegrityError, NoResultFound
from werkzeug.exceptions import Conflict, InternalServerError, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models.enums import RolesEnum
from models.user import UserModel
from services.ses_service import ses_email


class UserManager:

    @staticmethod
    def login(data):

        user = db.session.execute(
            db.select(UserModel).filter_by(email=data["email"])
        ).scalar()

        if user and check_password_hash(user.password, data["password"]):
            return AuthManager.encode_token(user)

        raise NotFound("User not found")

    @staticmethod
    def register(data):

        subject = f"Welcome to our Pizza club, {data["first_name"]}!"
        content = f"We are happy to provide you with a wide selection of delicious pizzas to choose from. Don't be late and order now!\nRegards,\nClub Pizza"

        try:
            data["password"] = generate_password_hash(
                data["password"], method="pbkdf2:sha256"
            )
            data["role"] = RolesEnum.customer.name
            user = UserModel(**data)

            db.session.add(user)
            db.session.flush()

            ses_email.send_email(data["email"], subject, content)
        except IntegrityError:
            raise Conflict(f"Email '{data["email"]}' already exists")
        except Exception as ex:
            db.session.rollback()
            db.session.remove()
            raise InternalServerError(f"Error: {str(ex)}")

        return AuthManager.encode_token(user)

    @staticmethod
    def create_user(data):

        try:
            data["password"] = generate_password_hash(
                data["password"], method="pbkdf2:sha256"
            )
            user = UserModel(**data)

            db.session.add(user)
            db.session.flush()
        except IntegrityError:
            raise Conflict(f"Email '{data["email"]}' already exists")

    @staticmethod
    def delete_user(user_id: int):

        try:
            user = db.session.execute(
                db.select(UserModel).filter_by(id=user_id)
            ).scalar_one()
            db.session.delete(user)
            db.session.flush()
        except NoResultFound:
            raise NotFound(f"User with ID {user_id} not found")

    @staticmethod
    def change_password(user: UserModel, data):

        if not check_password_hash(user.password, data["old_password"]):
            raise Conflict("Invalid password")

        user.password = generate_password_hash(
            data["new_password"], method="pbkdf2:sha256"
        )
        db.session.add(user)
        db.session.flush()
