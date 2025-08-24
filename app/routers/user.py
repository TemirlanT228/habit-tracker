


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user_service, get_user_service

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/', response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_user_service(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/', response_model=List[UserResponse])
async def get_users(telegram_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    if telegram_id is not None:
        try:
            user = await get_user_service(db, telegram_id)
            return [user]
        except ValueError:
            return []
    return []

@router.get('/{telegram_id}', response_model=UserResponse)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await get_user_service(db, telegram_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))