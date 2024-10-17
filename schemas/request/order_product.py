from marshmallow import fields, Schema

from models.enums import SizeEnum


class OrderProductRequestSchema(Schema):
    name = fields.String(required=True)
    size = fields.Enum(SizeEnum, required=True)
    quantity = fields.Integer(required=True)
