from sqlalchemy.orm import Mapped, mapped_column

from db import db


class OrderItemModel(db.Model):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(
        db.ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )
    pizza_size_id: Mapped[int] = mapped_column(
        db.ForeignKey("pizza_sizes.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)

    pizza_size: Mapped["PizzaSizeModel"] = db.relationship(lazy=True)
