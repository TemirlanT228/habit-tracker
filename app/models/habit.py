from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from app.database.base import Base
from datetime import datetime, timezone
from app.models.enums import WeekDayEnum, HabitKindEnum

class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    kind: Mapped[HabitKindEnum] = mapped_column(SQLEnum(HabitKindEnum), nullable=False)
    days: Mapped[list[WeekDayEnum]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="habits")
    tracks = relationship("Track", back_populates="habit", lazy="dynamic")