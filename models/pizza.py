from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class PizzaModel(db.Model):
    __tablename__ = "pizzas"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    ingredients: Mapped[str] = mapped_column(db.Text, nullable=False)
    photo_url: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(db.DateTime, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    sizes: Mapped[list["PizzaSizeModel"]] = db.relationship(
        "PizzaSizeModel",
        back_populates="pizza",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # size: Mapped[SizeEnum] = mapped_column(
    #     db.Enum(SizeEnum), default=SizeEnum.m, nullable=False
    # )
    # grammage: Mapped[int] = mapped_column(db.Integer, nullable=False)
    # price: Mapped[float] = mapped_column(
    #     db.Numeric(precision=5, scale=2), default=0, nullable=False
    # )
    # rating: Mapped[int] = mapped_column(db.Integer, default=0, nullable=False)

    # db.UniqueConstraint(name, size)
