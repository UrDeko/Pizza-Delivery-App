from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.user import UserManager
from schemas.request.user import (
    UserLoginSchema,
    UserRegisterSchema,
    PasswordChangeSchema,
)
from util.decorators import validate_schema


class UserLogin(Resource):

    @validate_schema(UserLoginSchema)
    def post(self):

        data = request.get_json()
        token = UserManager.login(data)
        return {"token": token}, 200


class UserRegister(Resource):

    @validate_schema(UserRegisterSchema)
    def post(self):

        data = request.get_json()
        token = UserManager.register(data)
        return {"token": token}, 201


class Password(Resource):

    @auth.login_required
    @validate_schema(PasswordChangeSchema)
    def post(self):

        user = auth.current_user()
        data = request.get_json()
        UserManager.change_password(user, data)
        return "", 204
