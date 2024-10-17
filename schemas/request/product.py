from marshmallow import validates, ValidationError

from schemas.base import ProductBaseSchema


class ProductRequestSchema(ProductBaseSchema):
    pass

    @validates("ingredients")
    def validate_ingredients(self, value: int):

        ingredients = value.strip().split(", ")

        if len(ingredients) < 3:
            raise ValidationError("Pizza should contain more than 3 ingredients")

    @validates("price")
    def validate_price(self, value: int):

        if value <= 0:
            raise ValidationError("Price should be above 0 BGN")

    @validates("grammage")
    def validate_grammage(self, value: int):

        if value <= 0:
            raise ValidationError("Grammage should be above 0g")
