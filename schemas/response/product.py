from marshmallow import fields

from schemas.base import ProductBaseSchema


class ProductResponseSchema(ProductBaseSchema):
    id = fields.Integer(required=True)
    rating = fields.String(required=True)
