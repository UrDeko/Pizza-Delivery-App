import uuid

from datetime import datetime, timezone

from decouple import config
from sqlalchemy.exc import NoResultFound
from werkzeug.exceptions import Conflict, InternalServerError, NotFound

from db import db
from managers.pizza import PizzaManager
from models.enums import RolesEnum, StatusEnum
from models.order import OrderModel
from models.order_item import OrderItemModel
from models.pizza import PizzaModel
from models.unpaid_order import UnpaidOrderModel
from models.unpaid_order_item import UnpaidOrderItemModel
from models.user import UserModel
from services.paypal_service import PayPalPayment
from services.twilio_service import twilio_notify


class OrderManager:

    @staticmethod
    def get_orders(user: UserModel):

        if user.role == RolesEnum.customer:
            return user.orders

        return db.session.execute(db.select(OrderModel)).scalars().fetchall()

    @staticmethod
    def delete_orders():

        db.session.execute(db.delete(OrderModel).filter_by(status=StatusEnum.delivered))
        db.session.flush()

    @staticmethod
    def get_order(order_id):

        try:
            order = db.session.execute(
                db.select(OrderModel).filter_by(id=order_id)
            ).scalar_one()
        except NoResultFound:
            raise NotFound("Order not found")

        return order

    # Old stable implementation

    # @staticmethod
    # def create_order(user: UserModel, data):

    #     order_items = []
    #     total_price = 0

    #     for product in data["products"]:
    #         try:
    #             pizza = db.session.execute(
    #                 db.select(PizzaModel).filter_by(name=product["name"])
    #             ).scalar_one()

    #             pizza_size = [p for p in pizza.sizes if p.size.name == product["size"]][
    #                 0
    #             ]
    #         except NoResultFound:
    #             raise NotFound(f"Pizza '{product["name"]}' not found")
    #         except IndexError:
    #             raise NotFound(f"Size '{product["size"]}' for pizza '{product["name"]}' is not available yet")

    #         quantity = int(product["quantity"])
    #         order_item = OrderItemModel(pizza_size_id=pizza_size.id, quantity=quantity)
    #         order_items.append(order_item)

    #         total_price += quantity * pizza_size.price
    #         pizza_size.rating += quantity

    #     order = OrderModel(user_id=user.id, total_price=total_price, items=order_items)

    #     db.session.add(order)
    #     db.session.flush()

    @staticmethod
    def create_order(user: UserModel, data):

        unpaid_order_items = []
        total_price = 0

        for product in data["products"]:
            try:
                pizza = db.session.execute(
                    db.select(PizzaModel).filter_by(name=product["name"])
                ).scalar_one()

                pizza_size = [p for p in pizza.sizes if p.size.name == product["size"]][
                    0
                ]
            except NoResultFound:
                raise NotFound(f"Pizza '{product["name"]}' not found")
            except IndexError:
                raise NotFound(
                    f"Size '{product["size"]}' for pizza '{product["name"]}' is not available yet"
                )

            quantity = int(product["quantity"])
            unpaid_order_item = UnpaidOrderItemModel(
                pizza_size_id=pizza_size.id, quantity=quantity
            )
            unpaid_order_items.append(unpaid_order_item)

            total_price += quantity * pizza_size.price

        unpaid_order = UnpaidOrderModel(
            user_id=user.id, total_price=total_price, items=unpaid_order_items
        )
        db.session.add(unpaid_order)
        db.session.flush()

        payment = PayPalPayment.create_payment(total_price, unpaid_order.id)
        if payment.create():
            return {
                "message": "Order created and payment initiated",
                "approval_url": payment["links"][1]["href"],
            }
        else:
            db.session.rollback()
            db.session.remove()
            raise Conflict("A conflict occurred while creating the order.")

    @staticmethod
    def capture_payment(data):

        payment = PayPalPayment.find_payment(data["payment_id"])
        if payment.execute({"payer_id": data["payer_id"]}):

            try:
                unpaid_order = db.session.execute(
                    db.select(UnpaidOrderModel).filter_by(id=data["unpaid_order_id"])
                ).scalar_one()
            except NoResultFound:
                raise NotFound("No order details available")

            order_items = []
            for product in unpaid_order.items:
                pizza_size = PizzaManager.get_pizza(product.pizza_size_id, size=True)
                pizza_size.rating += product.quantity
                order_item = OrderItemModel(
                    pizza_size_id=product.pizza_size_id, quantity=product.quantity
                )

                order_items.append(order_item)

            order = OrderModel(
                user_id=unpaid_order.user_id,
                total_price=unpaid_order.total_price,
                items=order_items,
            )
            db.session.add(order)
            db.session.delete(unpaid_order)
            db.session.flush()

        else:
            raise InternalServerError(
                f"Error: payment execution failed: {payment.error}"
            )

    @staticmethod
    def cancel_payment(unpaid_order_id):
        try:
            unpaid_order = db.session.execute(
                db.select(UnpaidOrderModel).filter_by(id=unpaid_order_id)
            ).scalar_one()
        except NoResultFound:
            raise NotFound("No order details available")

        db.session.delete(unpaid_order)
        db.session.flush()

    @staticmethod
    def update_order(order_id, status):

        order = OrderManager.get_order(order_id)
        order.status = status
        db.session.flush()

        if status == StatusEnum.in_transition:
            message = f"Order #{order.id} has been submitted for delivery"
            phone = order.user.phone
            # Use verified phone for testing purposes
            twilio_notify.send_notification(config("TWILIO_VERIFIED_NUMBER"), message)

    @staticmethod
    def delete_order(order_id):

        order = OrderManager.get_order(order_id)
        db.session.delete(order)
        db.session.flush()
