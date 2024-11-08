import paypalrestsdk

from decouple import config
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from resources.routes import routes


paypalrestsdk.configure(
    {
        "mode": "sandbox",
        "client_id": config("PAYPAL_CLIENT_ID"),
        "client_secret": config("PAYPAL_CLIENT_SECRET"),
    }
)


class ProductionEnvironment:
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASS')}@"
        f"{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )


class DevelopmentEnvironment:
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASS')}@"
        f"{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )


class TestingEnvironment:
    FLASK_ENV = "testing"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASS')}@"
        f"{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME_TESTING')}"
    )


def create_app(environment):

    app = Flask(__name__)
    app.config.from_object(environment)

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    [api.add_resource(*route) for route in routes]

    return app
