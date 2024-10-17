from werkzeug.exceptions import BadRequest, NotFound

from db import db
from models.enums import RolesEnum
from models.order import OrderModel
from models.order_product import OrderProductModel
from models.product import ProductModel
from models.user import UserModel


class OrderManager:

    @staticmethod
    def get_orders(user: UserModel):

        if user.role == RolesEnum.customer:
            return user.orders

        return db.session.execute(db.select(OrderModel)).scalars().fetchall()

    @staticmethod
    def delete_orders():

        db.session.execute(db.delete(OrderModel).filter_by(is_delivered=True))
        db.session.flush()

    @staticmethod
    def get_order(order_id):

        try:
            order = db.session.execute(
                db.select(OrderModel).filter_by(id=order_id)
            ).scalar_one()
        except Exception:
            raise NotFound("Order not found")

        return order

    @staticmethod
    def create_order(user: UserModel, data):

        order = OrderModel(customer_id=user.id)
        db.session.add(order)
        db.session.flush()

        for product in data["products"]:
            try:
                product_obj = db.session.execute(
                    db.select(ProductModel).filter_by(
                        name=product["name"], size=product["size"]
                    )
                ).scalar_one()
            except Exception:
                db.session.rollback()
                db.session.remove()
                raise BadRequest(f'Product "{product['name']}" not found')

            quantity = int(product["quantity"])
            association_object = OrderProductModel(
                order_id=order.id, product_id=product_obj.id, quantity=quantity
            )
            db.session.add(association_object)

            order.total_price += quantity * product_obj.price
            product_obj.rating += quantity

        db.session.flush()

    @staticmethod
    def update_order(order_id, status):

        order = OrderManager.get_order(order_id)
        order.status = status
        db.session.flush()

    @staticmethod
    def delete_order(order_id):

        order = OrderManager.get_order(order_id)
        db.session.delete(order)
        db.session.flush()
