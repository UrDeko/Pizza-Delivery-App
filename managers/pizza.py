import os

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError, NoResultFound
from werkzeug.exceptions import Conflict, NotFound

from constants import TEMP_FILE_FOLDER
from db import db
from models.pizza import PizzaModel
from models.pizza_size import PizzaSizeModel
from services.s3_service import s3_store
from util.helper import decode_photo


class PizzaManager:

    @staticmethod
    def get_pizzas():

        pizzas = db.session.execute(db.select(PizzaModel)).scalars().fetchall()
        return pizzas

    @staticmethod
    def create_pizza(data):

        if data["name"] in [p.name for p in PizzaManager.get_pizzas()]:
            raise Conflict("Pizza with the same name already exists")

        data["ingredients"] = [
            ingredient.strip() for ingredient in data["ingredients"].split(", ")
        ]
        encoded_photo = data.pop("photo")
        photo_extension = data.pop("photo_extension")
        photo_name = (
            f"{uuid4()}_{datetime.now(timezone.utc).timestamp()}.{photo_extension}"
        )
        path = os.path.join(TEMP_FILE_FOLDER, f"{photo_name}")
        decode_photo(path, encoded_photo)
        data["photo_url"] = s3_store.upload_photo(path, photo_name, photo_extension)
        pizza = PizzaModel(**data)
        db.session.add(pizza)
        db.session.flush()
        os.remove(path)

    @staticmethod
    def add_pizza_size(data):

        pizza_name = data.pop("name")
        try:
            pizza = db.session.execute(
                db.select(PizzaModel).filter_by(name=pizza_name)
            ).scalar_one()

            pizza_size = PizzaSizeModel(**data)
            pizza.sizes.append(pizza_size)
            db.session.add(pizza)
            db.session.flush()
        except NoResultFound:
            raise NotFound("Pizza not found")
        except IntegrityError:
            raise Conflict(
                f"Size '{data["size"]}' for pizza '{pizza_name}' already exists"
            )

    @staticmethod
    def get_pizza(pizza_id, size=False):

        model = PizzaSizeModel if size else PizzaModel

        try:
            pizza = db.session.execute(
                db.select(model).filter_by(id=pizza_id)
            ).scalar_one()
        except NoResultFound:
            raise NotFound("Pizza not found")

        return pizza

    @staticmethod
    def update_pizza(pizza_id, data, size=False):

        if (not size and "name" in data) and (
            data["name"] in [p.name for p in PizzaManager.get_pizzas()]
        ):
            raise Conflict("Pizza with the same name already exists")

        pizza = PizzaManager.get_pizza(pizza_id, size)

        if "photo" in data:
            encoded_photo = data.pop("photo")
            photo_extension = data.pop("photo_extension")
            photo_name = (
                f"{uuid4()}_{datetime.now(timezone.utc).timestamp()}.{photo_extension}"
            )
            path = os.path.join(TEMP_FILE_FOLDER, f"{photo_name}")
            decode_photo(path, encoded_photo)
            data["photo_url"] = s3_store.upload_photo(path, photo_name, photo_extension)
            os.remove(path)

        for key, value in data.items():
            setattr(pizza, key, value)
        db.session.flush()

    @staticmethod
    def delete_pizza(pizza_id, size=False):

        pizza = PizzaManager.get_pizza(pizza_id, size)
        db.session.delete(pizza)
        db.session.flush()
