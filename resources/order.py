from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from managers.auth import auth
from managers.order import OrderManager
from models.enums import RolesEnum, StatusEnum
from schemas.response.order import OrderResponseSchema
from schemas.request.order import OrderRequestSchema
from util.decorators import permission_required, validate_schema


class Orders(Resource):

    @auth.login_required
    def get(self):

        user = auth.current_user()
        orders = OrderManager.get_orders(user)
        return {"orders": OrderResponseSchema().dump(orders, many=True)}, 200

    @auth.login_required
    @permission_required(RolesEnum.customer)
    @validate_schema(OrderRequestSchema)
    def post(self):
        user = auth.current_user()
        data = request.get_json()
        response = OrderManager.create_order(user, data)
        return response, 200

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def delete(self):

        OrderManager.delete_orders()
        return {"message": "Delivered orders deleted"}, 200


class Order(Resource):

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def get(self, order_id):

        order = OrderManager.get_order(order_id)
        return {"order": OrderResponseSchema().dump(order)}, 200

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def delete(self, order_id):

        OrderManager.delete_order(order_id)
        return {"message": "Order deleted"}, 200


class OrderPending(Resource):

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def put(self, order_id):

        OrderManager.update_order(order_id, StatusEnum.pending)
        return {"message": "Pending order processing"}, 200


class OrderInTransition(Resource):

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def put(self, order_id):

        OrderManager.update_order(order_id, StatusEnum.in_transition)
        return {"message": "Order in transition"}, 200


class OrderDelivered(Resource):

    @auth.login_required
    @permission_required([RolesEnum.deliver, RolesEnum.admin])
    def put(self, order_id):

        OrderManager.update_order(order_id, StatusEnum.delivered)
        return {"message": "Order successfully delivered"}, 200


class CapturePayment(Resource):

    def get(self):

        try:
            data = {
                "unpaid_order_id": request.args["unpaid_order_id"],
                "payment_id": request.args["paymentId"],
                "payer_id": request.args["PayerID"],
            }
        except KeyError:
            raise BadRequest("Insufficient payload data")

        OrderManager.capture_payment(data)
        return {"message": "Order successfully created"}, 201


class CancelPayment(Resource):

    def get(self):

        try:
            unpaid_order_id = request.args["unpaid_order_id"]
        except KeyError:
            raise BadRequest("Invalid payload data")

        OrderManager.cancel_payment(unpaid_order_id)
        return {"message": "Payment cancelled"}, 200
