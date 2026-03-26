from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    income: Mapped[float | None] = mapped_column(Float, nullable=True)
    expenses: Mapped[float | None] = mapped_column(Float, nullable=True)
    investments: Mapped[str] = mapped_column(Text, default="[]")
    goals: Mapped[str] = mapped_column(Text, default="[]")
    risk_profile: Mapped[str | None] = mapped_column(String(32), nullable=True)

    user: Mapped[User] = relationship(back_populates="profile")


class TaxData(Base):
    __tablename__ = "tax_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    form16_data: Mapped[str] = mapped_column(Text, default="{}")
    deductions: Mapped[str] = mapped_column(Text, default="{}")
    regime_choice: Mapped[str] = mapped_column(String(16), default="new")


class Portfolio(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    holdings: Mapped[str] = mapped_column(Text, default="[]")
    xirr: Mapped[float | None] = mapped_column(Float, nullable=True)
    overlap: Mapped[float | None] = mapped_column(Float, nullable=True)
    expense_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)
    benchmark: Mapped[str] = mapped_column(Text, default="{}")
