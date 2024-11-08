import factory

from werkzeug.security import generate_password_hash

from db import db
from models.enums import RolesEnum, SizeEnum, StatusEnum
from models.order import OrderModel
from models.order_item import OrderItemModel
from models.unpaid_order import UnpaidOrderModel
from models.unpaid_order_item import UnpaidOrderItemModel
from models.pizza import PizzaModel
from models.pizza_size import PizzaSizeModel
from models.user import UserModel


class BaseFactory(factory.Factory):

    @classmethod
    def create(cls, **kwargs):

        obj = super().create(**kwargs)
        if hasattr(obj, "password"):
            obj.password = generate_password_hash(obj.password, method="pbkdf2:sha256")
        db.session.add(obj)
        db.session.commit()
        # db.session.flush()
        return obj


class UserFactory(BaseFactory):

    class Meta:
        model = UserModel

    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    phone = "+0748592125"
    role = RolesEnum.customer


class PizzaFactory(BaseFactory):

    class Meta:
        model = PizzaModel

    id = factory.Sequence(lambda n: n)
    name = "Margherita"
    ingredients = "cheese, tomatoes, onion, sausage"
    photo_url = "test"


class PizzaSizeFactory(BaseFactory):

    class Meta:
        model = PizzaSizeModel

    id = factory.Sequence(lambda n: n)
    pizza_id = 0
    size = SizeEnum.m
    grammage = 750
    price = 7.50
    rating = 0


class OrderFactory(BaseFactory):

    class Meta:
        model = OrderModel

    id = factory.Sequence(lambda n: n)
    user_id = 0
    total_price = 24
    status = StatusEnum.pending


class OrderItemFactory(BaseFactory):

    class Meta:
        model = OrderItemModel

    order_id = 0
    pizza_size_id = 0
    quantity = 1

class UnpaidOrderFactory(BaseFactory):

    class Meta:
        model = UnpaidOrderModel

    id = factory.Sequence(lambda n: n)
    user_id = 0
    total_price = 24


class UnpaidOrderItemFactory(BaseFactory):

    class Meta:
        model = UnpaidOrderItemModel

    unpaid_order_id = 0
    pizza_size_id = 0
    quantity = 1
