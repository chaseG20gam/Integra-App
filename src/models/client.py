from __future__ import annotations

from typing import Optional

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Client(Base):
    # represents a therapy client

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    therapy_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    sports: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    background: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    observations: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
