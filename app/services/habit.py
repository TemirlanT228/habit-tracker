from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.habit import create_habit, get_habit_by_user, update_habit, delete_habit
from app.schemas.habit import HabitCreate, HabitResponse, HabitUpdate, HabitDelete
from typing import List

async def create_habit_service(db: AsyncSession, habit_data: HabitCreate) -> HabitResponse:
    return await create_habit(db, habit_data)

async def get_habits_by_user_service(db: AsyncSession, user_id: int) -> List[HabitResponse]:
    habits = await get_habit_by_user(db, user_id)
    return habits 

async def update_habit_service(db: AsyncSession, habit_id: int, user_id: int, habit_update: HabitUpdate) -> HabitResponse | None:
    habit = await update_habit(db, habit_id, user_id, habit_update)
    if not habit:
        return None
    return HabitResponse.model_validate(habit)

async def delete_habit_service(db: AsyncSession, habit_id: int, user_id: int) -> bool:
    result = await delete_habit(db, habit_id, user_id)
    return result