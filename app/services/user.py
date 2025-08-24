from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import create_user, get_user_by_telegram_id, get_user_by_id 
from app.schemas.user import UserCreate, UserResponse

async def create_user_service(db: AsyncSession, user_data: UserCreate) -> UserResponse:
    existing_user = await get_user_by_telegram_id(db, user_data.telegram_id)
    if existing_user:
        return existing_user
    return await create_user(db, user_data)

async def get_user_service(db: AsyncSession, telegram_id: int) -> UserResponse:
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise ValueError("User not found")
    return user

async def get_user_by_id_service(db: AsyncSession, user_id: int) -> UserResponse:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    return user