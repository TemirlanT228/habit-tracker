from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.habit import HabitCreate, HabitResponse
from app.services.habit import create_habit_service, get_habits_by_user_service
from app.services.user import get_user_by_id_service

router = APIRouter(prefix='/habits', tags=['habits'])

@router.post('/', response_model=HabitResponse)
async def create_habit(habit: HabitCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_habit_service(db, habit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/', response_model=list[HabitResponse])
async def get_habits_by_user(
    user_id: int = None,
    telegram_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        if user_id is not None:
            user = await get_user_by_id_service(db, user_id)
        elif telegram_id is not None:
            from app.services.user import get_user_service
            user = await get_user_service(db, telegram_id)
        else:
            raise HTTPException(status_code=400, detail="user_id or telegram_id required")
        return await get_habits_by_user_service(db, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))