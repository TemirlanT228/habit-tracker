from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.habit import create_habit, get_habit_by_user
from app.schemas.habit import HabitCreate, HabitResponse
from typing import List

async def create_habit_service(db: AsyncSession, habit_data: HabitCreate) -> HabitResponse:
    return await create_habit(db, habit_data)

async def get_habits_by_user_service(db: AsyncSession, user_id: int) -> List[HabitResponse]:
    habits = await get_habit_by_user(db, user_id)
    return habits 

