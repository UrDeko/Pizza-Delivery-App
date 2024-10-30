from sqlalchemy.orm import Mapped, mapped_column

from db import db


class UnpaidOrderItemModel(db.Model):
    __tablename__ = "unpaid_order_items"

    unpaid_order_id: Mapped[int] = mapped_column(
        db.ForeignKey("unpaid_orders.id", ondelete="CASCADE"), primary_key=True
    )
    pizza_size_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
