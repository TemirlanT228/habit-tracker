from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from app.database.base import Base
from datetime import datetime, timezone
from app.models.enums import WeekDayEnum, HabitKindEnum

class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    kind: Mapped[HabitKindEnum] = mapped_column(SQLEnum(HabitKindEnum), nullable=False)
    days: Mapped[list[str]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="habit")
    track = relationship("Track", back_populates="habit")