from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict, InternalServerError, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import Authenticate
from models.enums import RolesEnum
from models.user import UserModel
from services.ses_email import ses


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

            ses.send_email(data["email"], subject, content)
        except IntegrityError:
            raise Conflict()
        except Exception as ex:
            db.session.rollback()
            db.session.remove()
            raise InternalServerError(f"Error: {str(ex)}")

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
