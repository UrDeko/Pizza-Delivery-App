from sqlalchemy.orm import Mapped, mapped_column

from db import db


class UnpaidOrderModel(db.Model):
    __tablename__ = "unpaid_orders"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(
        db.Numeric(precision=10, scale=2), default=0, nullable=False
    )

    items: Mapped[list["UnpaidOrderItemModel"]] = db.relationship(
        cascade="all, delete-orphan", lazy=True
    )
