from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.user import UserManager
from models.enums import RolesEnum
from schemas.request.user import UserCreateRequestSchema
from util.decorators import permission_required, validate_schema


class Users(Resource):

    @auth.login_required
    @permission_required([RolesEnum.admin])
    @validate_schema(UserCreateRequestSchema)
    def post(self):

        data = request.get_json()
        UserManager.create_user(data)
        return {"message": "User created"}, 201


class User(Resource):

    @auth.login_required
    @permission_required([RolesEnum.admin])
    def delete(self, user_id):

        UserManager.delete_user(user_id)
        return {"message": f"User with id {user_id} deleted"}, 200
