from resources.auth import UserLogin, UserRegister, Password
from resources.order import (
    Orders,
    Order,
    OrderPending,
    OrderInTransition,
    OrderDelivered,
    CapturePayment,
    CancelPayment,
)
from resources.pizza import Pizza, Pizzas, PizzaSize, PizzaSizes
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
    (CapturePayment, "/payment/execute"),
    (CancelPayment, "/payment/cancel"),
    (Pizzas, "/pizzas"),
    (Pizza, "/pizza/<int:pizza_id>"),
    (PizzaSizes, "/pizza-sizes"),
    (PizzaSize, "/pizza-size/<int:pizza_id>"),
)
