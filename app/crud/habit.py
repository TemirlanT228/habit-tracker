from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.habit import Habit
from app.schemas.habit import HabitCreate


async def create_habit(db: AsyncSession, habit: HabitCreate):
    db_habit = Habit(**habit.model_dump())
    db.add(db_habit)
    await db.commit()
    await db.refresh(db_habit)
    return db_habit

async def get_habit_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Habit).filter(Habit.user_id == user_id))
    return result.scalars().all()