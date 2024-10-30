from marshmallow import fields, Schema, validates, ValidationError

from models.enums import SizeEnum


class OrderItemRequestSchema(Schema):
    name = fields.String(required=True)
    size = fields.Enum(SizeEnum, required=True)
    quantity = fields.Integer(required=True)


class OrderRequestSchema(Schema):
    products = fields.List(
        fields.Nested(OrderItemRequestSchema, required=True), required=True
    )

    @validates("products")
    def validate_products(self, products):

        if not products:
            raise ValidationError("Empty product list")

        try:
            pizzas = [(p["name"], p["size"]) for p in products]

            for pizza in pizzas:
                if pizzas.count(pizza) > 1:
                    raise ValidationError(
                        f"Product '{pizza[0]}' with size '{pizza[1].name}' specified more than once"
                    )
        except KeyError:
            pass
