from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.base import Base
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Date, Boolean
from sqlalchemy import Enum as SQLEnum
from app.models.enums import WeekDayEnum, HabitKindEnum

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="tracks")
    habit = relationship("Habit", back_populates="tracks")
