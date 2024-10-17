from sqlalchemy.orm import Mapped, mapped_column

from db import db


class OrderProductModel(db.Model):
    __tablename__ = "order_product"

    order_id: Mapped[int] = mapped_column(
        db.ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        db.ForeignKey("products.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)

    db.UniqueConstraint(order_id, product_id)
    product_info: Mapped["ProductModel"] = db.relationship(lazy=True)
