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
    def validate_products(self, product_list):

        if not product_list:
            raise ValidationError("Empty product list")

        for i in range(len(product_list) - 1):
            for j in range(i + 1, len(product_list)):

                if product_list[i].get("name") == product_list[j].get(
                    "name"
                ) and product_list[i].get("size") == product_list[j].get("size"):
                    raise ValidationError("Same product specified more than once")
