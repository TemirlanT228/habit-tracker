from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    created_at: str
    streak: int
