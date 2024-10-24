from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.pizza import PizzaManager
from models.enums import RolesEnum
from schemas.response.pizza import PizzaResponseSchema
from schemas.request.pizza import PizzaRequestSchema, PizzaSizeRequestSchema
from util.decorators import permission_required, validate_schema


class Pizzas(Resource):

    def get(self):

        pizzas = PizzaManager.get_pizzas()
        return PizzaResponseSchema().dump(pizzas, many=True)

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(PizzaRequestSchema)
    def post(self):

        data = request.get_json()
        PizzaManager.create_pizza(data)
        return {"message": "Pizza successfully created"}, 201


class Pizza(Resource):

    def get(self, pizza_id):

        pizza = PizzaManager.get_pizza(pizza_id)
        return PizzaResponseSchema().dump(pizza)

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(PizzaRequestSchema)
    def put(self, pizza_id):

        data = request.get_json()
        PizzaManager.update_pizza(pizza_id, data)
        return "", 204

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    def delete(self, pizza_id):

        PizzaManager.delete_pizza(pizza_id)
        return {"message": "Pizza deleted"}, 200


class PizzaSizes(Resource):

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(PizzaSizeRequestSchema)
    def post(self):

        data = request.get_json()
        PizzaManager.add_pizza_size(data)
        return {"message": "Pizza size successfully created"}, 201


class PizzaSize(Resource):

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    @validate_schema(PizzaSizeRequestSchema)
    def put(self, pizza_id):

        data = request.get_json()
        PizzaManager.update_pizza(pizza_id, data, size=True)
        return "", 204

    @auth.login_required
    # @permission_required([RolesEnum.chef])
    def delete(self, pizza_id):

        PizzaManager.delete_pizza(pizza_id, size=True)
        return {"message": "Pizza size deleted"}, 200
