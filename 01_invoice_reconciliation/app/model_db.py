from .database import Base

from sqlalchemy import DateTime, String, Text, ForeignKey, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customer.id"))
    currency: Mapped[str] = mapped_column(String(3))
    total_amount: Mapped[int] = mapped_column(Integer)
    missing_amount: Mapped[int] = mapped_column(Integer)


class Transfer(Base):
    __tablename__ = "transfer"

    id: Mapped[str] = mapped_column(primary_key=True)
    received_at: Mapped[datetime] = mapped_column(DateTime)
    customer_id: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String(3))
    amount: Mapped[Integer] = mapped_column(Integer)
    status: Mapped[bool] = mapped_column(Boolean)