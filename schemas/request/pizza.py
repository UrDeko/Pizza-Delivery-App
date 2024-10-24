from marshmallow import fields, validates, ValidationError
from marshmallow.validate import OneOf

from schemas.base import PizzaBaseSchema, PizzaSizeBaseSchema


class PizzaRequestSchema(PizzaBaseSchema):
    photo = fields.String(required=True)
    photo_extension = fields.String(required=True, validate=OneOf(["png", "jpg"]))

    @validates("ingredients")
    def validate_ingredients(self, value: int):

        ingredients = [ingredient.strip() for ingredient in value.split(", ")]

        if len(ingredients) < 3:
            raise ValidationError("Pizza should contain more than 3 ingredients")


class PizzaSizeRequestSchema(PizzaSizeBaseSchema):

    @validates("price")
    def validate_price(self, value: int):

        if value <= 0:
            raise ValidationError("Price should be above 0 BGN")

    @validates("grammage")
    def validate_grammage(self, value: int):

        if value <= 0:
            raise ValidationError("Grammage should be above 0g")
