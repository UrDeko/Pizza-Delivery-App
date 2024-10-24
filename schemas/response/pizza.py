from marshmallow import fields

from schemas.base import PizzaBaseSchema, PizzaSizeBaseSchema


class PizzaSizeResponseSchema(PizzaSizeBaseSchema):
    id = fields.Integer(required=True)
    rating = fields.String(required=True)


class PizzaResponseSchema(PizzaBaseSchema):
    id = fields.Integer(required=True)
    photo_url = fields.String(required=True)
    sizes = fields.List(fields.Nested(PizzaSizeResponseSchema))
