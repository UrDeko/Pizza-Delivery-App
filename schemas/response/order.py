from marshmallow import fields, Schema

from models.enums import SizeEnum, StatusEnum


class OrderItemResponseSchema(Schema):
    quantity = fields.Integer(required=True)
    name = fields.String(attribute="pizza_size.pizza.name")
    size = fields.Enum(SizeEnum, attribute="pizza_size.size")
    price = fields.Decimal(places=2, as_string=True, attribute="pizza_size.price")


class OrderResponseSchema(Schema):
    id = fields.Integer(required=True)
    total_price = fields.Decimal(required=True, places=2, as_string=True)
    created_on = fields.DateTime(required=True)
    status = fields.Enum(StatusEnum, required=True)
    items = fields.List(fields.Nested(OrderItemResponseSchema), required=True)
