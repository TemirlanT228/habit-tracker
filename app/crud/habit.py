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
    result = await db.execute(select(Habit).filter(Habit.user_id == user_id).order_by(Habit.id))
    return result.scalars().all()

async def update_habit(db: AsyncSession, habit_id: int, user_id: int, updates: dict):
    result = await db.execute(select(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id))
    habit = result.scalars().first()
    if not habit:
        return None
    if hasattr(updates, 'model_dump'):
        updates = updates.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(habit, key, value)
    await db.commit()
    await db.refresh(habit)
    return habit

async def delete_habit(db: AsyncSession, habit_id: int, user_id: int):
    result = await db.execute(select(Habit).filter(Habit.id == habit_id, Habit.user_id == user_id))
    habit = result.scalars().first()
    if not habit:
        return False
    await db.delete(habit)
    await db.commit()
    return True