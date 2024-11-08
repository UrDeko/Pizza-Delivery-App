from decouple import config
from unittest.mock import MagicMock, patch

from db import db
from models.enums import RolesEnum, SizeEnum, StatusEnum
from models.order import OrderModel
from models.order_item import OrderItemModel
from models.unpaid_order import UnpaidOrderModel
from models.unpaid_order_item import UnpaidOrderItemModel
from models.user import UserModel
from tests.base import BaseTestCase, generate_token
from tests.factories import (
    OrderFactory,
    OrderItemFactory,
    PizzaFactory,
    PizzaSizeFactory,
    UnpaidOrderFactory,
    UnpaidOrderItemFactory,
    UserFactory,
)


class TestOrderManagement(BaseTestCase):

    @patch("managers.order.PayPalPayment")
    def test_create_order(self, paypal_mock):

        payment = MagicMock()
        payment.create.return_value = True
        payment_data = {"links": [{}, {"href": "URL"}]}
        payment.__getitem__.side_effect = payment_data.__getitem__
        paypal_mock.create_payment.return_value = payment

        data = {
            "products": [
                {"name": "Margherita", "size": "m", "quantity": 2},
                {"name": "Margherita", "size": "s", "quantity": 2},
            ]
        }

        customer = UserFactory(role=RolesEnum.customer)
        token = generate_token(customer)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size_m = PizzaSizeFactory(id=1, pizza_id=1)
        pizza_size_s = PizzaSizeFactory(id=2, pizza_id=1, size=SizeEnum.s)

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 0)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 0)

        expected_message = "Order created and payment initiated"
        response = self.client.post("/orders", json=data, headers=headers)
        message = response.json["message"]

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 1)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_create_order_pizza_not_found(self):

        data = {
            "products": [
                {"name": "Margherita", "size": "m", "quantity": 2},
                {"name": "Margherita", "size": "s", "quantity": 2},
            ]
        }

        customer = UserFactory(role=RolesEnum.customer)
        token = generate_token(customer)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza 'Margherita' not found"
        response = self.client.post("/orders", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_create_order_pizza_size_not_found(self):

        data = {
            "products": [
                {"name": "Margherita", "size": "m", "quantity": 2},
                {"name": "Margherita", "size": "s", "quantity": 2},
            ]
        }

        customer = UserFactory(role=RolesEnum.customer)
        token = generate_token(customer)
        headers = {"Authorization": f"Bearer {token}"}

        pizza = PizzaFactory(id=1)
        expected_message = "Size 'm' for pizza 'Margherita' is not available yet"
        response = self.client.post("/orders", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    @patch("managers.order.PayPalPayment")
    def test_create_order_conflict_payment(self, paypal_mock):

        payment = MagicMock()
        payment.create.return_value = False
        paypal_mock.create_payment.return_value = payment

        data = {
            "products": [
                {"name": "Margherita", "size": "m", "quantity": 2},
                {"name": "Margherita", "size": "s", "quantity": 2},
            ]
        }

        customer = UserFactory(role=RolesEnum.customer)
        token = generate_token(customer)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size_m = PizzaSizeFactory(id=1, pizza_id=1)
        pizza_size_s = PizzaSizeFactory(id=2, pizza_id=1, size=SizeEnum.s)

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 0)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 0)

        expected_message = "A conflict occurred while creating the order"
        response = self.client.post("/orders", json=data, headers=headers)
        message = response.json["message"]

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 0)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 0)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, message)

    @patch("managers.order.PayPalPayment")
    def test_capture_payment(self, paypal_mock):

        payment = MagicMock()
        payment.execute.return_value = True
        paypal_mock.create_payment.return_value = payment

        user = UserFactory(id=1)
        pizza = PizzaFactory(id=1)
        pizza_size_m = PizzaSizeFactory(id=1, pizza_id=1)
        unpaid_order = UnpaidOrderFactory(id=1, user_id=1, total_price=7.50)
        unpaid_order_item = UnpaidOrderItemFactory(unpaid_order_id=1, pizza_size_id=1)

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 1)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 1)
        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)
        order_items = db.session.execute(db.select(OrderItemModel)).scalars().fetchall()
        self.assertEqual(len(order_items), 0)

        expected_message = "Order successfully created"
        response = self.client.get(
            "/payment/execute?unpaid_order_id=1&paymentId=1&PayerID=1"
        )
        message = response.json["message"]

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 0)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 0)
        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 1)
        order_items = db.session.execute(db.select(OrderItemModel)).scalars().fetchall()
        self.assertEqual(len(order_items), 1)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected_message, message)

    @patch("managers.order.PayPalPayment")
    def test_capture_payment_fail(self, paypal_mock):

        payment = MagicMock()
        payment.execute.return_value = False
        payment.error = "Maintenance underway"
        paypal_mock.find_payment.return_value = payment

        expected_message = f"Error: payment execution failed: {payment.error}"
        response = self.client.get(
            "/payment/execute?unpaid_order_id=1&paymentId=1&PayerID=1"
        )
        message = response.json["message"]

        self.assertEqual(response.status_code, 500)
        self.assertEqual(expected_message, message)

    def test_capture_payment_insufficient_payload_data(self):

        expected_message = "Insufficient payload data"
        response = self.client.get("/payment/execute?unpaid_order_id=1")
        message = response.json["message"]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_message, message)

    def test_cancel_payment(self):

        unpaid_order = UnpaidOrderFactory(id=1, user_id=1, total_price=7.50)
        unpaid_order_item = UnpaidOrderItemFactory(unpaid_order_id=1, pizza_size_id=1)

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 1)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 1)

        expected_message = f"Payment cancelled"
        response = self.client.get("/payment/cancel?unpaid_order_id=1")
        message = response.json["message"]

        unpaid_orders = (
            db.session.execute(db.select(UnpaidOrderModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_orders), 0)
        unpaid_order_items = (
            db.session.execute(db.select(UnpaidOrderItemModel)).scalars().fetchall()
        )
        self.assertEqual(len(unpaid_order_items), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_cancel_payment_invalid_payload_data(self):

        expected_message = "Invalid payload data"
        response = self.client.get("/payment/cancel")
        message = response.json["message"]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_message, message)

    def test_get_orders(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        user_2 = UserFactory(id=2)
        order = OrderFactory(id=1, user_id=1)
        order_2 = OrderFactory(id=2, user_id=2)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 2)

        response = self.client.get("/orders", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["orders"]), 2)

    def test_get_orders_customer(self):

        customer = UserFactory(id=1)
        token = generate_token(customer)
        headers = {"Authorization": f"Bearer {token}"}

        customer_2 = UserFactory(id=2)
        order = OrderFactory(id=1, user_id=1)
        order_2 = OrderFactory(id=2, user_id=2)
        order_3 = OrderFactory(id=3, user_id=1)
        order_4 = OrderFactory(id=4, user_id=1)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 4)

        response = self.client.get("/orders", headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["orders"]), 3)

    def test_get_order(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order = OrderFactory(id=1, user_id=1)

        response = self.client.get("/order/1", headers=headers)

        self.assertEqual(response.status_code, 200)

    def test_get_order_invalid_id(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Order not found"
        response = self.client.get("/order/1", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_delete_user_with_orders(self):

        admin = UserFactory(role=RolesEnum.admin)
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order_1 = OrderFactory(id=1, user_id=1, status=StatusEnum.delivered)
        order_2 = OrderFactory(id=2, user_id=1, status=StatusEnum.delivered)
        order_3 = OrderFactory(id=3, user_id=1, status=StatusEnum.pending)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 2)
        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 3)

        expected_message = "User with ID 1 deleted"
        response = self.client.delete("/user/1", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)
        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

    def test_delete_order_with_items(self):

        admin = UserFactory(role=RolesEnum.admin)
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        pizza = PizzaFactory(id=1)
        pizza_size_m = PizzaSizeFactory(id=1, pizza_id=1)
        pizza_size_s = PizzaSizeFactory(id=2, pizza_id=1, size=SizeEnum.s)
        order = OrderFactory(id=1, user_id=1, status=StatusEnum.delivered)
        order_item_1 = OrderItemFactory(order_id=1, pizza_size_id=1, quantity=2)
        order_item_2 = OrderItemFactory(order_id=1, pizza_size_id=2, quantity=2)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 1)
        order_items = db.session.execute(db.select(OrderItemModel)).scalars().fetchall()
        self.assertEqual(len(order_items), 2)

        expected_message = "Order deleted"
        response = self.client.delete("/order/1", headers=headers)
        message = response.json["message"]

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)
        order_items = db.session.execute(db.select(OrderItemModel)).scalars().fetchall()
        self.assertEqual(len(order_items), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_delete_delivered_orders(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order_1 = OrderFactory(id=1, user_id=1, status=StatusEnum.delivered)
        order_2 = OrderFactory(id=2, user_id=1, status=StatusEnum.delivered)
        order_3 = OrderFactory(id=3, user_id=1, status=StatusEnum.pending)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 3)

        expected_message = "Delivered orders deleted"
        response = self.client.delete("/orders", headers=headers)
        message = response.json["message"]

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_delete_order(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order = OrderFactory(id=1, user_id=1)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 1)

        expected_message = "Order deleted"
        response = self.client.delete("/order/1", headers=headers)
        message = response.json["message"]

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_update_order_status_delivered(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order = OrderFactory(id=1, user_id=1)

        expected_message = "Order successfully delivered"
        response = self.client.put("/order/1/delivered", headers=headers)
        message = response.json["message"]

        order = db.session.execute(db.select(OrderModel)).scalars().fetchall()[0]
        self.assertEqual(order.status, StatusEnum.delivered)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_update_order_status_delivered_invalid_id(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Order not found"
        response = self.client.put("/order/1/delivered", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    @patch("managers.order.twilio_notify")
    def test_update_order_status_in_transition(self, twilio_mock):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order = OrderFactory(id=1, user_id=1)

        sms_message = f"Order #{order.id} has been submitted for delivery"
        expected_message = "Order in transition"
        response = self.client.put("/order/1/in-transition", headers=headers)
        message = response.json["message"]

        order = db.session.execute(db.select(OrderModel)).scalars().fetchall()[0]
        self.assertEqual(order.status, StatusEnum.in_transition)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)
        twilio_mock.send_notification.assert_called_once_with(
            config("TWILIO_VERIFIED_NUMBER"), sms_message
        )

    def test_update_order_status_in_transition_invalid_id(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Order not found"
        response = self.client.put("/order/1/in-transition", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_update_order_status_pending(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        user = UserFactory(id=1)
        order = OrderFactory(id=1, user_id=1, status=StatusEnum.in_transition)

        expected_message = "Pending order processing"
        response = self.client.put("/order/1/pending", headers=headers)
        message = response.json["message"]

        order = db.session.execute(db.select(OrderModel)).scalars().fetchall()[0]
        self.assertEqual(order.status, StatusEnum.pending)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_update_order_status_pending_invalid_id(self):

        deliver = UserFactory(role=RolesEnum.deliver)
        token = generate_token(deliver)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Order not found"
        response = self.client.put("/order/1/pending", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)
