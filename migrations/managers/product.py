from werkzeug.exceptions import NotFound

from db import db
from models.product import ProductModel


class ProductManager:

    @staticmethod
    def get_products():

        products = db.session.execute(db.select(ProductModel)).scalars().fetchall()
        return products

    @staticmethod
    def create_product(data):

        product = ProductModel(**data)
        db.session.add(product)
        db.session.flush()

    @staticmethod
    def get_product(product_id):

        try:
            product = db.session.execute(
                db.select(ProductModel).filter_by(id=product_id)
            ).scalar_one()
        except Exception:
            raise NotFound("Product not found")

        return product

    @staticmethod
    def update_product(product_id, data):

        product = ProductManager.get_product(product_id)
        for key, value in data.items():
            setattr(product, key, value)
        db.session.flush()

    @staticmethod
    def delete_product(product_id):

        product = ProductManager.get_product(product_id)
        db.session.delete(product)
        db.session.flush()
