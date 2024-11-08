from tests.base import BaseTestCase, generate_token
from tests.factories import UserFactory

from db import db
from models.enums import RolesEnum
from models.order import OrderModel
from models.pizza import PizzaModel
from models.pizza_size import PizzaSizeModel
from models.user import UserModel


class TestUserLoginSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        for field in ("email", "password"):
            self.assertIn(field, error_message)


class TestUserRegisterSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        for field in ("first_name", "last_name", "email", "password", "phone"):
            self.assertIn(field, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

    def test_invalid_password(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "some@mail.com",
            "password": "abc",
            "phone": "+0748592125",
        }

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        expected_message = "Invalid payload: {'password': ['Password length should be between 8 and 12 characters long']}"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        data["password"] = "abcdefgh"
        expected_message = "Invalid payload: {'password': ['Invalid password. Use 2 of the following: uppercase, numbers, special, nonletters']}"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

    def test_invalid_first_name(self):

        data = {
            "first_name": "J",
            "last_name": "Doe",
            "email": "some@mail.com",
            "password": "#@KL0305",
            "phone": "+0748592125",
        }

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        expected_message = "Invalid payload: {'first_name': ['First name should consist of 2 or more characters']}"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

    def test_invalid_last_name(self):

        data = {
            "first_name": "John",
            "last_name": "D",
            "email": "some@mail.com",
            "password": "#@KL0305",
            "phone": "+0748592125",
        }

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        expected_message = "Invalid payload: {'last_name': ['Last name should consist of 2 or more characters']}"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

    def test_invalid_phone_number(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "some@mail.com",
            "password": "#@KL0305",
            "phone": "0748592125",
        }

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        expected_message = "Invalid payload: {'phone': ['Invalid phone number']}"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        data["phone"] = "+02"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        data["phone"] = "+029178327956237943"
        response = self.client.post("/register", json=data)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)


class TestUserCreateSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        user = UserFactory(role=RolesEnum.admin)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        response = self.client.post("/users", json=data, headers=headers)
        error_message = response.json["message"]

        for field in ("password", "first_name", "last_name", "phone", "role"):
            self.assertIn(field, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

    def test_invalid_role(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "some@mail.com",
            "password": "#@KL0305",
            "phone": "+0748592125",
            "role": "supplier",
        }

        user = UserFactory(role=RolesEnum.admin)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        expected_message = (
            "Invalid payload: {'role': ['Must be one of: admin, chef, deliver.']}"
        )
        response = self.client.post("/users", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)


class TestPasswordChangeSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        user = UserFactory()
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        response = self.client.post("/user/change-password", json=data, headers=headers)
        error_message = response.json["message"]

        for field in ("old_password", "new_password"):
            self.assertIn(field, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

    def test_new_password_same_as_old(self):

        data = {"old_password": "#@KL0305", "new_password": "#@KL0305"}

        user = UserFactory()
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        expected_message = "Invalid payload: {'_schema': ['New password cannot be the same as the old password']}"
        response = self.client.post("/user/change-password", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)


class TestPizzaRequestSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

        response = self.client.post("/pizzas", json=data, headers=headers)
        error_message = response.json["message"]

        for field in ("name", "ingredients", "photo", "photo_extension"):
            self.assertIn(field, error_message)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

    def test_insufficient_number_ingredients(self):

        data = {
            "name": "Margherita",
            "ingredients": "tomatoes",
            "photo": "test",
            "photo_extension": "png",
        }

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Invalid payload: {'ingredients': ['Pizza should contain more than 2 ingredients']}"
        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

        response = self.client.post("/pizzas", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertIn(expected_message, error_message)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

    def test_invalid_photo_extension(self):

        data = {
            "name": "Margherita",
            "ingredients": "tomatoes, cheese, onion",
            "photo": "test",
            "photo_extension": "test",
        }

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = (
            "Invalid payload: {'photo_extension': ['Must be one of: png, jpg.']}"
        )
        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

        response = self.client.post("/pizzas", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertIn(expected_message, error_message)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)


class TestPizzaUpdateRequestSchema(BaseTestCase):

    def test_insufficient_image_data(self):

        data = {"photo_extension": "png"}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Invalid payload: {'_schema': ['Insufficient image data']}"
        response = self.client.put("/pizza/1", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        data = {"photo": "test"}

        response = self.client.put("/pizza/1", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)


class TestPizzaSizeRequestSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

        response = self.client.post("/pizza-sizes", json=data, headers=headers)
        error_message = response.json["message"]

        for field in ("name", "size", "grammage", "price"):
            self.assertIn(field, error_message)

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

    def test_invalid_size(self):

        data = {"name": "Margherita", "size": "test", "grammage": 100, "price": 5.5}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

        expected_message = "Invalid payload: {'size': ['Must be one of: s, m, l, j.']}"
        response = self.client.post("/pizza-sizes", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

    def test_invalid_grammage(self):

        data = {"name": "Margherita", "size": "m", "grammage": 0, "price": 5.5}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

        expected_message = (
            "Invalid payload: {'grammage': ['Grammage should be above 0g']}"
        )
        response = self.client.post("/pizza-sizes", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

    def test_invalid_price(self):

        data = {"name": "Margherita", "size": "m", "grammage": 100, "price": 0}

        user = UserFactory(role=RolesEnum.chef)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)

        expected_message = "Invalid payload: {'price': ['Price should be above 0 BGN']}"
        response = self.client.post("/pizza-sizes", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        pizza_size = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_size), 0)


class TestOrderRequestSchema(BaseTestCase):

    def test_missing_fields(self):

        data = {}

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

        response = self.client.post("/orders", json=data, headers=headers)
        error_message = response.json["message"]

        for field in "products":
            self.assertIn(field, error_message)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

    def test_missing_products_fields(self):

        data = {"products": [{}]}

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

        response = self.client.post("/orders", json=data, headers=headers)
        error_message = response.json["message"]

        for field in ("name", "size", "quantity"):
            self.assertIn(field, error_message)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

    def test_duplicate_products(self):

        data = {
            "products": [
                {"name": "Margherita", "size": "m", "quantity": 2},
                {"name": "Margherita", "size": "m", "quantity": 2},
            ]
        }

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

        expected_message = "Invalid payload: {'products': [\"Product 'Margherita' with size 'm' specified more than once\"]}"
        response = self.client.post("/orders", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

    def test_invalid_quantity(self):

        data = {"products": [{"name": "Margherita", "size": "m", "quantity": 0}]}

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)

        expected_message = "Invalid payload: {'products': {0: {'quantity': ['Quantity should be greater than 0']}}}"
        response = self.client.post("/orders", json=data, headers=headers)
        error_message = response.json["message"]

        self.assertEqual(expected_message, error_message)

        orders = db.session.execute(db.select(OrderModel)).scalars().fetchall()
        self.assertEqual(len(orders), 0)
