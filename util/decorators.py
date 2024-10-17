import functools

from flask import request
from marshmallow import Schema
from werkzeug.exceptions import BadRequest, Unauthorized

from managers.auth import auth
from models.enums import RolesEnum


def permission_required(roles: list[RolesEnum]):
    def decorator(func):
        functools.wraps(func)

        def wrapper(*args, **kwargs):

            user = auth.current_user()
            if not user.role in roles:
                raise Unauthorized()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_schema(schema: Schema):
    def decorator(func):
        functools.wraps(func)

        def wrapper(*args, **kwargs):

            data = request.get_json()
            schema_obj = schema()
            errors = schema_obj.validate(data)

            if errors:
                raise BadRequest(f"Invalid payload: {errors}")

            return func(*args, **kwargs)

        return wrapper

    return decorator
