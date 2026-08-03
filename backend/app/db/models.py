from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Fighter(Base):
    __tablename__ = "fighters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    weight_class: Mapped[str | None] = mapped_column(String)
    gender: Mapped[str | None] = mapped_column(String)
    stance: Mapped[str | None] = mapped_column(String)
    height_cms: Mapped[float | None] = mapped_column(Float)
    reach_cms: Mapped[float | None] = mapped_column(Float)
    weight_lbs: Mapped[float | None] = mapped_column(Float)
    age: Mapped[int | None] = mapped_column(Integer)
    current_win_streak: Mapped[float | None] = mapped_column(Float)
    current_lose_streak: Mapped[float | None] = mapped_column(Float)
    wins: Mapped[float | None] = mapped_column(Float)
    losses: Mapped[float | None] = mapped_column(Float)
    wins_by_ko: Mapped[float | None] = mapped_column(Float)
    wins_by_submission: Mapped[float | None] = mapped_column(Float)
    wins_by_decision_majority: Mapped[float | None] = mapped_column(Float)
    wins_by_decision_split: Mapped[float | None] = mapped_column(Float)
    wins_by_decision_unanimous: Mapped[float | None] = mapped_column(Float)
    avg_odds: Mapped[float | None] = mapped_column(Float)
    avg_expected_value: Mapped[float | None] = mapped_column(Float)
    total_fights: Mapped[int | None] = mapped_column(Integer)
    last_fight_date: Mapped[date | None] = mapped_column(Date)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    saved_comparisons: Mapped[list["SavedComparison"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SavedComparison(Base):
    __tablename__ = "saved_comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    fighter1_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    fighter2_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    predicted_winner_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    fighter1_win_probability: Mapped[float] = mapped_column(Float, nullable=False)
    fighter2_win_probability: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="saved_comparisons")
    fighter1: Mapped["Fighter"] = relationship(foreign_keys=[fighter1_id])
    fighter2: Mapped["Fighter"] = relationship(foreign_keys=[fighter2_id])
    predicted_winner: Mapped["Fighter"] = relationship(foreign_keys=[predicted_winner_id])
