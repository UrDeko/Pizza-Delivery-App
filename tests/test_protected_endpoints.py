from tests.base import BaseTestCase, generate_token
from tests.factories import UserFactory

from models.enums import RolesEnum


class TestProtectedEndpoints(BaseTestCase):

    endpoints = (
        ("POST", "/users"),
        ("DELETE", "/user/1"),
        ("POST", "/user/change-password"),
        ("GET", "/orders"),
        ("POST", "/orders"),
        ("DELETE", "/orders"),
        ("GET", "/order/1"),
        ("DELETE", "/order/1"),
        ("PUT", "/order/1/pending"),
        ("PUT", "/order/1/in-transition"),
        ("PUT", "/order/1/delivered"),
        ("POST", "/pizzas"),
        ("PUT", "/pizza/1"),
        ("DELETE", "/pizza/1"),
        ("POST", "/pizza-sizes"),
        ("PUT", "/pizza-size/1"),
        ("DELETE", "/pizza-size/1"),
    )

    def make_request(self, method, url, headers=None):

        match method:
            case "GET":
                response = self.client.get(url, headers=headers)
            case "POST":
                response = self.client.post(url, headers=headers)
            case "PUT":
                response = self.client.put(url, headers=headers)
            case "DELETE":
                response = self.client.delete(url, headers=headers)

        return response

    def test_endpoints_missing_token(self):

        message = {"message": "Invalid or missing token"}

        for method, url in self.endpoints:
            response = self.make_request(method, url)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, message)

    def test_endpoints_invalid_token(self):

        message = {"message": "Invalid or missing token"}
        headers = {"Authorization": "Bearer invalid"}

        for method, url in self.endpoints:
            response = self.make_request(method, url, headers)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, message)

    def test_permission_denied_admin(self):

        user = UserFactory()
        token = generate_token(user)
        endpoints = self.endpoints[:2] + self.endpoints[5:]
        message = {"message": "Permission denied"}
        headers = {"Authorization": f"Bearer {token}"}

        for method, url in endpoints:
            response = self.make_request(method, url, headers)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, message)

        user = UserFactory(role=RolesEnum.deliver)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.make_request(*self.endpoints[4], headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, message)

    def test_permission_denied_chef(self):

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        message = {"message": "Permission denied"}
        headers = {"Authorization": f"Bearer {token}"}

        for method, url in self.endpoints[-6:]:
            response = self.make_request(method, url, headers)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, message)

    def test_permission_denied_deliver(self):

        user = UserFactory(role=RolesEnum.customer)
        token = generate_token(user)
        message = {"message": "Permission denied"}
        headers = {"Authorization": f"Bearer {token}"}

        for method, url in self.endpoints[5:8]:
            response = self.make_request(method, url, headers)

            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, message)

    def test_permission_denied_customer(self):

        user = UserFactory(role=RolesEnum.deliver)
        token = generate_token(user)
        message = {"message": "Permission denied"}
        headers = {"Authorization": f"Bearer {token}"}

        response = self.make_request(*self.endpoints[4], headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, message)
