from resources.auth import UserLogin, UserRegister, Password
from resources.order import (
    Orders,
    Order,
    OrderPending,
    OrderInTransition,
    OrderDelivered,
)
from resources.product import Products, Product
from resources.user import Users, User


routes = (
    (UserLogin, "/login"),
    (UserRegister, "/register"),
    (Users, "/users"),
    (User, "/user/<int:user_id>"),
    (Password, "/user/change-password"),
    (Orders, "/orders"),
    (Order, "/order/<int:order_id>"),
    (OrderPending, "/order/<int:order_id>/pending"),
    (OrderInTransition, "/order/<int:order_id>/in-transition"),
    (OrderDelivered, "/order/<int:order_id>/delivered"),
    (Products, "/products"),
    (Product, "/product/<int:product_id>"),
)
