import os

from unittest.mock import MagicMock, patch

from constants import TEMP_FILE_FOLDER
from db import db
from models.enums import RolesEnum, SizeEnum
from models.pizza import PizzaModel
from models.pizza_size import PizzaSizeModel
from tests.base import BaseTestCase, generate_token
from tests.factories import PizzaFactory, PizzaSizeFactory, UserFactory


class TestPizzaManagement(BaseTestCase):

    @patch("managers.pizza.os.remove")
    @patch("managers.pizza.datetime")
    @patch("managers.pizza.uuid4")
    @patch("managers.pizza.decode_photo")
    @patch("managers.pizza.s3_store")
    def test_create_pizza(self, s3_mock, decode_mock, uuid_mock, dt_mock, os_mock):
        s3_mock.upload_photo.return_value = "URL"
        uuid_mock.return_value = "123-456"
        dt_obj = MagicMock()
        dt_obj.timestamp.return_value = "1730"
        dt_mock.now.return_value = dt_obj

        data = {
            "name": "Margherita",
            "ingredients": "cheese, tomatoe, onion, sausage",
            "photo": "test",
            "photo_extension": "png",
        }
        path = os.path.join(TEMP_FILE_FOLDER, f"123-456_1730.{data["photo_extension"]}")

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.post("/pizzas", json=data, headers=headers)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(pizzas[0].photo_url, "URL")
        s3_mock.upload_photo.assert_called_once()
        decode_mock.assert_called_once_with(path, data["photo"])
        os_mock.assert_called_once_with(path)

    def test_pizza_with_conflicting_name(self):

        data = {
            "name": "Margherita",
            "ingredients": "cheese, tomatoe, onion, sausage",
            "photo": "test",
            "photo_extension": "png",
        }

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)

        expected_message = "Pizza with the same name already exists"
        response = self.client.post("/pizzas", json=data, headers=headers)
        message = response.json["message"]

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, message)

    def test_pizza_get(self):

        pizza = PizzaFactory(id=1)

        response = self.client.get("/pizza/1")

        self.assertEqual(response.status_code, 200)

    def test_pizza_update(self):

        data = {
            "name": "Pepperoni",
            "ingredients": "cheese, tomatoe, onion, sausage",
        }

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)

        response = self.client.put("/pizza/1", json=data, headers=headers)

        self.assertEqual(response.status_code, 204)
        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()

        for key, value in data.items():
            self.assertEqual(getattr(pizzas[0], key), value)

    def test_pizza_update_invalid_id(self):

        data = {
            "name": "Pepperoni",
            "ingredients": "cheese, tomatoe, onion, sausage",
        }

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza not found"
        response = self.client.put("/pizza/1", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_pizza_update_with_existing_name(self):

        data = {
            "name": "Pepperoni",
            "ingredients": "cheese, tomatoe, onion, sausage",
        }
        pizza = PizzaFactory(id=1, name=data["name"])

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza with the same name already exists"
        response = self.client.put("/pizza/1", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, message)

    def test_pizza_delete(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)

        expected_message = "Pizza deleted"
        response = self.client.delete("/pizza/1", headers=headers)
        message = response.json["message"]

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_pizza_delete_with_sizes(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size_m = PizzaSizeFactory(id=1, pizza_id=1)
        pizza_size_s = PizzaSizeFactory(id=2, pizza_id=1, size=SizeEnum.s)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)
        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 2)

        expected_message = "Pizza deleted"
        response = self.client.delete("/pizza/1", headers=headers)
        message = response.json["message"]

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)
        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_pizza_delete_invalid_id(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza not found"
        response = self.client.delete("/pizza/1", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)


class TestPizzaSizeManagement(BaseTestCase):

    def test_create_pizza_size(self):

        data = {
            "name": "Margherita",
            "size": "s",
            "price": 4.50,
            "grammage": 450,
        }
        pizza = PizzaFactory(id=1)

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 0)

        expected_message = "Pizza size successfully created"
        response = self.client.post("/pizza-sizes", json=data, headers=headers)
        message = response.json["message"]

        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 1)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected_message, message)

    def test_pizza_size_update(self):

        data = {
            "price": 4.50,
            "grammage": 450,
        }

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size = PizzaSizeFactory(id=1, pizza_id=1)

        response = self.client.put("/pizza-size/1", json=data, headers=headers)

        self.assertEqual(response.status_code, 204)
        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        for key, value in data.items():
            self.assertEqual(getattr(pizza_sizes[0], key), value)

    def test_pizza_size_update_invalid_id(self):

        data = {
            "price": 4.50,
            "grammage": 450,
        }

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza not found"
        response = self.client.put("/pizza-size/1", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_pizza_delete_with_sizes(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size = PizzaSizeFactory(id=1, pizza_id=1)

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 1)
        self.assertEqual(len(pizza_sizes), 1)

        expected_message = "Pizza deleted"
        response = self.client.delete("/pizza/1", headers=headers)
        message = response.json["message"]

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizzas), 0)
        self.assertEqual(len(pizza_sizes), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_pizza_size_delete(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}
        pizza = PizzaFactory(id=1)
        pizza_size = PizzaSizeFactory(id=1, pizza_id=1)

        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 1)

        expected_message = "Pizza size deleted"
        response = self.client.delete("/pizza-size/1", headers=headers)
        message = response.json["message"]

        pizza_sizes = db.session.execute(db.select(PizzaSizeModel)).scalars().fetchall()
        self.assertEqual(len(pizza_sizes), 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_pizza_size_delete_invalid_id(self):

        chef = UserFactory(role=RolesEnum.chef)
        token = generate_token(chef)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Pizza not found"
        response = self.client.delete("/pizza-size/1", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)
