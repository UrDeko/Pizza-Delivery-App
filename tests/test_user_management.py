from unittest.mock import patch
from werkzeug.security import generate_password_hash

from db import db
from models.enums import RolesEnum
from models.user import UserModel
from tests.base import BaseTestCase, generate_token
from tests.factories import UserFactory


def mock_exception():
    
    raise Exception("Invalid state")


class TestUserManagement(BaseTestCase):

    @patch("managers.user.ses_email")
    def test_user_register(self, ses_mock):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
            "phone": "+0748592125",
        }

        subject = f"Welcome to our Pizza club, {data["first_name"]}!"
        content = f"We are happy to provide you with a wide selection of delicious pizzas to choose from. Don't be late and order now!\nRegards,\nClub Pizza"

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        response = self.client.post("/register", json=data)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json)
        self.assertEqual(len(users), 1)
        ses_mock.send_email.assert_called_once_with(data["email"], subject, content)

    @patch("managers.user.ses_email")
    def test_user_register_send_email_failure(self, ses_mock):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
            "phone": "+0748592125",
        }

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 0)

        with self.assertRaises(Exception):
            expected_message = "Error: Invalid state"
            response = self.client.post("/register", json=data)
            message = response.json["message"]

            users = db.session.execute(db.select(UserModel)).scalars().fetchall()
            self.assertEqual(len(users), 1)
            self.assertEqual(response.status_code, 500)
            self.assertEqual(expected_message, message)
            

    def test_user_register_existing_email_error(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
            "phone": "+0748592125",
        }

        user = UserFactory(email=data["email"])

        expected_message = "Email 'chushko23@abv.bg' already exists"
        response = self.client.post("/register", json=data)
        message = response.json["message"]

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, message)

    def test_user_login(self):

        data = {
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
        }

        user = UserFactory(email=data["email"], password=data["password"])
        response = self.client.post("/login", json=data)

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        self.assertEqual(users[0].password, user.password)
        self.assertEqual(users[0].email, data["email"])

    def test_user_login_invalid_email(self):

        data = {
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
        }

        user = UserFactory(password=data["password"])
        expected_message = "User not found"
        response = self.client.post("/login", json=data)
        message = response.json["message"]

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)
        self.assertEqual(users[0].password, user.password)
        self.assertNotEqual(users[0].email, data["email"])

    def test_user_login_invalid_password(self):

        data = {
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
        }

        user = UserFactory(email=data["email"])
        expected_message = "User not found"
        response = self.client.post("/login", json=data)
        message = response.json["message"]

        hashed_password = generate_password_hash(
            data["password"], method="pbkdf2:sha256"
        )
        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)
        self.assertEqual(users[0].email, data["email"])
        self.assertNotEqual(users[0].password, hashed_password)

    def test_user_create(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
            "phone": "+0748592125",
            "role": "deliver",
        }

        admin = UserFactory(role=RolesEnum.admin)
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}
        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        expected_message = "User created"
        response = self.client.post("/users", json=data, headers=headers)
        message = response.json["message"]

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(expected_message, message)

    def test_user_create_existing_email_error(self):

        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "chushko23@abv.bg",
            "password": "#@KL0305",
            "phone": "+0748592125",
            "role": "deliver",
        }

        admin = UserFactory(role=RolesEnum.admin, email="chushko23@abv.bg")
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}
        user = UserFactory(password=data["password"])

        expected_message = "Email 'chushko23@abv.bg' already exists"
        response = self.client.post("/users", json=data, headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, message)

    def test_user_delete(self):

        admin = UserFactory(role=RolesEnum.admin)
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}
        user = UserFactory(id=1)
        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 2)

        expected_message = "User with ID 1 deleted"
        response = self.client.delete("/user/1", headers=headers)
        message = response.json["message"]

        users = db.session.execute(db.select(UserModel)).scalars().fetchall()
        self.assertEqual(len(users), 1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_message, message)

    def test_user_delete_invalid_user_id(self):

        admin = UserFactory(role=RolesEnum.admin)
        token = generate_token(admin)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "User with ID 1 not found"
        response = self.client.delete("/user/1", headers=headers)
        message = response.json["message"]

        self.assertEqual(response.status_code, 404)
        self.assertEqual(expected_message, message)

    def test_user_change_password(self):

        data = {
            "old_password": "#@KL0305",
            "new_password": "#@PL0405"
        }

        user = UserFactory(password="#@KL0305")
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.post("/user/change-password", json=data, headers=headers)

        self.assertEqual(response.status_code, 204)

    def test_user_change_password_invalid_password(self):

        data = {
            "old_password": "#@KL0405",
            "new_password": "#@PL0405"
        }

        user = UserFactory(password="#@KL0305")
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        expected_message = "Invalid password"
        response = self.client.post("/user/change-password", json=data, headers=headers)
        expected_message = response.json["message"]

        self.assertEqual(response.status_code, 409)
        self.assertEqual(expected_message, expected_message)
