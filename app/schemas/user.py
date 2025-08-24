from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  
    id: int
    telegram_id: int
    username: str | None = None
    created_at: datetime
    streak: int = 0