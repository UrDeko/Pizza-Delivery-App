from marshmallow import fields, Schema

from schemas.response.product import ProductResponseSchema


class OrderProductResponseSchema(Schema):
    quantity = fields.Integer(required=True)
    product_info = fields.Nested(ProductResponseSchema, only=["name", "size", "price"])
