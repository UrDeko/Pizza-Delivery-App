from datetime import timedelta

import paypalrestsdk

from decouple import config


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
