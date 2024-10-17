from marshmallow import fields, Schema

from schemas.response.order_product import OrderProductResponseSchema


class OrderResponseSchema(Schema):
    id = fields.Integer(required=True)
    total_price = fields.Decimal(required=True, places=2, as_string=True)
    created_on = fields.DateTime(required=True)
    products = fields.List(fields.Nested(OrderProductResponseSchema), required=True)
