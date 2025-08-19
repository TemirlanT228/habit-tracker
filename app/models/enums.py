from enum import Enum

class WeekDayEnum(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"

class HabitKindEnum(str, Enum):
    good = "good"
    bad = "bad"