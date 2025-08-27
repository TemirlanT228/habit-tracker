from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.models.enums import WeekDayEnum

def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Habit")],
            [KeyboardButton(text="List Habits")],
            [KeyboardButton(text="Edit Habit")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_days_kb():
    days_en = [e.value for e in WeekDayEnum]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_kind_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="good"), KeyboardButton(text="bad")], [KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_hours_kb(prefix="hour_"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{h:02d}", callback_data=f"{prefix}{h:02d}") for h in range(i, i+6)]
            for i in range(0, 24, 6)
        ]
    )

def get_minutes_kb(prefix="minute_"):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{m:02d}", callback_data=f"{prefix}{m:02d}") for m in range(0, 60, 10)]
        ]
    )
