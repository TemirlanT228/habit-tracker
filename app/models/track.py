from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Date, Boolean
from app.database.base import Base
from datetime import date as datetime_date
class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey("habits.id"), nullable=False)
    date: Mapped[datetime_date] = mapped_column(Date, nullable=False, default=datetime_date.today)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="tracks")
    habit = relationship("Habit", back_populates="tracks")