from pydantic import BaseModel
from datetime import date

class TrackCreate(BaseModel):
    habit_id: int
    user_id: int
    date: date
    is_completed: bool = False

class TrackResponse(TrackCreate):
    id: int