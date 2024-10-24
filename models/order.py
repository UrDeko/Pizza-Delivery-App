from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db import db
from models.enums import StatusEnum


class OrderModel(db.Model):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"), nullable=False)
    total_price: Mapped[float] = mapped_column(
        db.Numeric(precision=10, scale=2), default=0, nullable=False
    )
    created_on: Mapped[datetime] = mapped_column(db.DateTime, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[StatusEnum] = mapped_column(
        db.Enum(StatusEnum), default=StatusEnum.pending, nullable=False
    )

    user: Mapped["UserModel"] = db.relationship(
        "UserModel", back_populates="orders", lazy=True
    )
    items: Mapped[list["OrderItemModel"]] = db.relationship(
        cascade="all, delete-orphan", lazy=True
    )
