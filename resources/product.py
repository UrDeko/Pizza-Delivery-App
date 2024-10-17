from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.product import ProductManager
from models.enums import RolesEnum
from schemas.response.product import ProductResponseSchema
from schemas.request.product import ProductRequestSchema
from util.decorators import permission_required, validate_schema


class Products(Resource):

    def get(self):

        products = ProductManager.get_products()
        return ProductResponseSchema().dump(products, many=True)

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(ProductRequestSchema)
    def post(self):

        data = request.get_json()
        ProductManager.create_product(data)
        return {"message": "Product successfully created"}, 201


class Product(Resource):

    def get(self, product_id):

        product = ProductManager.get_product(product_id)
        return ProductResponseSchema().dump(product)

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(ProductRequestSchema)
    def put(self, product_id):

        data = request.get_json()
        ProductManager.update_product(product_id, data)
        return {"message": "Product updated"}, 201

    @auth.login_required
    @permission_required([RolesEnum.chef])
    def delete(self, product_id):

        ProductManager.delete_product(product_id)
        return {"message": "Product deleted"}, 201
