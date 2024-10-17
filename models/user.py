from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from db import db
from models.enums import RolesEnum


class UserModel(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(13), nullable=False)
    role: Mapped[RolesEnum] = mapped_column(
        db.Enum(RolesEnum), default=RolesEnum.customer, nullable=False
    )
    created_on: Mapped[datetime] = mapped_column(db.DateTime, server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(
        db.DateTime, server_default=func.now(), onupdate=func.now()
    )

    orders: Mapped[list["OrderModel"]] = db.relationship(lazy=True)
