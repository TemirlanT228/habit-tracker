from pydantic import BaseModel, ConfigDict, field_validator
from app.models.enums import HabitKindEnum, WeekDayEnum
from typing import List, Optional
from datetime import datetime, time

class HabitCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    kind: HabitKindEnum
    days: Optional[List[WeekDayEnum]] = None
    time: time

    @field_validator("days", mode="before")
    def validate_days(cls, days):
        if days is None:
            return days
        if isinstance(days, list) and days:
            if hasattr(days[0], 'value'):
                return [d.value if hasattr(d, 'value') else d for d in days]
        return days

class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) 
    
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    kind: HabitKindEnum
    days: Optional[List[WeekDayEnum]] = None
    time: time

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    kind: Optional[HabitKindEnum] = None
    days: Optional[List[WeekDayEnum]] = None
    time: Optional[time] = None

class HabitDelete(BaseModel):
    id: int
