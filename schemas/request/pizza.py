from marshmallow import fields, Schema, validates, validates_schema, ValidationError
from marshmallow.validate import OneOf

from schemas.base import PizzaBaseSchema, PizzaSizeBaseSchema


class PizzaRequestSchema(PizzaBaseSchema):
    photo = fields.String(required=True)
    photo_extension = fields.String(required=True, validate=OneOf(["png", "jpg"]))

    @validates("ingredients")
    def validate_ingredients(self, value: int):

        ingredients = [ingredient.strip() for ingredient in value.split(", ")]

        if len(ingredients) < 3:
            raise ValidationError("Pizza should contain more than 2 ingredients")


class PizzaUpdateRequestSchema(PizzaRequestSchema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False

    @validates_schema
    def validate_photo(self, data, **kwargs):

        if ("photo" in data and "photo_extension" not in data) or (
            "photo" not in data and "photo_extension" in data
        ):
            raise ValidationError("Insufficient image data")


class PizzaSizeRequestSchema(PizzaSizeBaseSchema):
    name = fields.String(required=True)

    @validates("price")
    def validate_price(self, value: int):

        if value <= 0:
            raise ValidationError("Price should be above 0 BGN")

    @validates("grammage")
    def validate_grammage(self, value: int):

        if value <= 0:
            raise ValidationError("Grammage should be above 0g")


class PizzaSizeUpdateRequestSchema(PizzaSizeRequestSchema):

    class Meta:
        fields = ("price", "grammage")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False
