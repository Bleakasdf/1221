from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    height_cm: Mapped[int | None] = mapped_column(Integer, default=183)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), default=82)
    target_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), default=89)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    sessions: Mapped[list["WorkoutSession"]] = relationship(back_populates="user")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    workout_type: Mapped[str] = mapped_column(String(100))
    cycle_week: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="active")
    general_feedback: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="sessions")
    exercise_logs: Mapped[list["WorkoutExerciseLog"]] = relationship(back_populates="session")


class WorkoutExerciseLog(Base):
    __tablename__ = "workout_exercise_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id"))
    exercise_name: Mapped[str] = mapped_column(String(255))
    planned_value: Mapped[str] = mapped_column(String(255))
    actual_value: Mapped[str] = mapped_column(Text)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    sets_count: Mapped[int | None] = mapped_column(Integer)
    reps_json: Mapped[str | None] = mapped_column(Text)
    rpe: Mapped[int | None] = mapped_column(Integer)
    feedback_tag: Mapped[str | None] = mapped_column(String(100))
    comment: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped[WorkoutSession] = relationship(back_populates="exercise_logs")


class RecoveryLog(Base):
    __tablename__ = "recovery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    session_id: Mapped[int | None] = mapped_column(ForeignKey("workout_sessions.id"), nullable=True)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    sleep_quality: Mapped[int | None] = mapped_column(Integer)
    energy: Mapped[int | None] = mapped_column(Integer)
    soreness: Mapped[int | None] = mapped_column(Integer)
    stress: Mapped[int | None] = mapped_column(Integer)
    lower_back_state: Mapped[int | None] = mapped_column(Integer)
    resting_pulse: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[date] = mapped_column(Date, default=date.today)
    calories: Mapped[int | None] = mapped_column(Integer)
    protein_g: Mapped[int | None] = mapped_column(Integer)
    fat_g: Mapped[int | None] = mapped_column(Integer)
    carbs_g: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
