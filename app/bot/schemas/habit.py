from pydantic import BaseModel
from typing import List, Optional

class HabitCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    kind: str
    days: Optional[List[str]] = None
    time: Optional[str] = None

class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    kind: str
    days: Optional[List[str]]
    created_at: str
    updated_at: str
    time: Optional[str] = None
