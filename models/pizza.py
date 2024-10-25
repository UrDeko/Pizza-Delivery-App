from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class PizzaModel(db.Model):
    __tablename__ = "pizzas"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
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
