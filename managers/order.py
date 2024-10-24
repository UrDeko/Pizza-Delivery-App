from decouple import config
from sqlalchemy.exc import NoResultFound
from werkzeug.exceptions import NotFound

from db import db
from models.enums import RolesEnum, StatusEnum
from models.order import OrderModel
from models.order_item import OrderItemModel
from models.pizza import PizzaModel
from models.user import UserModel
from services.twilio_sms import twilio_notify


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

    @staticmethod
    def create_order(user: UserModel, data):

        order_items = []
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
                raise NotFound(f"Size {product["size"]} not available")

            quantity = int(product["quantity"])
            order_item = OrderItemModel(pizza_size_id=pizza_size.id, quantity=quantity)
            order_items.append(order_item)

            total_price += quantity * pizza_size.price
            pizza_size.rating += quantity

        order = OrderModel(user_id=user.id, total_price=total_price, items=order_items)

        db.session.add(order)
        db.session.flush()

    # @staticmethod
    # def create_order(user: UserModel, data):

    #     order_products = []
    #     total_price = 0

    #     for product in data["products"]:
    #         try:
    #             product_obj = db.session.execute(
    #                 db.select(ProductModel).filter_by(
    #                     name=product["name"], size=product["size"]
    #                 )
    #             ).scalar_one()
    #         except NoResultFound:
    #             raise BadRequest(f"Product '{product["name"]}' not found")

    #         quantity = int(product["quantity"])
    #         order_product = OrderProductModel(
    #             product_id=product_obj.id, quantity=quantity
    #         )
    #         order_products.append(order_product)

    #         total_price += quantity * product_obj.price
    #         product_obj.rating += quantity

    #     order = OrderModel(
    #         customer_id=user.id, total_price=total_price, products=order_products
    #     )

    #     db.session.add(order)
    #     db.session.flush()

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
