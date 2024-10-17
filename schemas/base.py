from marshmallow import fields, Schema

from models.enums import SizeEnum


class UserBaseSchema(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)


class ProductBaseSchema(Schema):
    name = fields.String(required=True)
    ingredients = fields.String(required=True)
    size = fields.Enum(SizeEnum, required=True)
    grammage = fields.Integer(required=True)
    price = fields.Decimal(required=True, places=2, as_string=True)
    photo = fields.String(required=True)
