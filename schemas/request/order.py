from marshmallow import fields, Schema, validates, ValidationError

from schemas.request.order_product import OrderProductRequestSchema


class OrderRequestSchema(Schema):
    products = fields.List(
        fields.Nested(OrderProductRequestSchema, required=True), required=True
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
