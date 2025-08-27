from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.bot.services.api_client import ApiClient
from app.bot.schemas.habit import HabitCreate
from app.models.enums import HabitKindEnum, WeekDayEnum
from .common import cancel_habit, HabitStates
from .keyboards import get_main_kb, get_days_kb, get_kind_kb
import re

router = Router()

@router.message(lambda m: m.text == "Create Habit")
async def start_habit_scenario(message: Message, state: FSMContext):
    await state.set_state(HabitStates.name)
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Введите название привычки:", reply_markup=cancel_kb)

@router.message(HabitStates.name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await cancel_habit(message, state)
        return
    await state.update_data(name=message.text)
    await state.set_state(HabitStates.description)
    desc_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="нет")], [KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Введите описание (или выберите 'нет' для пропуска):", reply_markup=desc_kb)

@router.message(HabitStates.description)
async def process_description(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await cancel_habit(message, state)
        return
    description = message.text if message.text != "нет" else None
    await state.update_data(description=description)
    await state.set_state(HabitStates.kind)
    await message.answer("Выберите тип привычки:", reply_markup=get_kind_kb())

@router.message(HabitStates.kind)
async def process_kind(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await cancel_habit(message, state)
        return
    kind_values = [e.value for e in HabitKindEnum]
    if message.text.lower() not in kind_values:
        await message.answer(f"Пожалуйста, выберите: {', '.join(kind_values)}.")
        return
    await state.update_data(kind=message.text.lower())
    await state.set_state(HabitStates.days)
    await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=get_days_kb())

@router.message(HabitStates.days)
async def process_days(message: Message, state: FSMContext, api_client: ApiClient = None):
    data = await state.get_data()
    days = data.get("days", [])
    if message.text.lower() == "done":
        # Переход к ручному вводу времени
        await state.update_data(days=days)
        await state.set_state(HabitStates.time)
        await message.answer("Введите время в формате ЧЧ:ММ (например, 08:30):")
        return
    elif message.text == "Отмена":
        await cancel_habit(message, state)
    else:
        valid_days = [e.value for e in WeekDayEnum]
        if message.text not in valid_days:
            await message.answer(f"Пожалуйста, выберите день недели из списка: {', '.join(valid_days)}")
        elif message.text in days:
            await message.answer("Этот день уже добавлен. Выберите другой или нажмите 'Done'.")
        else:
            days.append(message.text)
            await state.update_data(days=days)
    await message.answer("Добавьте ещё день или нажмите 'Done':", reply_markup=get_days_kb())


@router.message(HabitStates.time)
async def process_time(message: Message, state: FSMContext, api_client: ApiClient = None):
    time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    if not re.match(time_pattern, message.text):
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30)")
        return
    await state.update_data(time=message.text)
    data = await state.get_data()
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "Ошибка: пользователь не найден. Пожалуйста, используйте /start для регистрации.",
            reply_markup=get_main_kb()
        )
        await state.clear()
        return
    habit_data = HabitCreate(
        user_id=user.id,
        name=data["name"],
        description=data["description"],
        kind=data["kind"],
        days=data["days"],
        time=message.text
    )
    await api_client.create_habit(habit_data)
    await state.clear()
    await message.answer(
        f"Привычка успешно создана на {message.text}! 🎉\n\nЧтобы отредактировать привычку, нажмите 'Edit Habit' в меню.",
        reply_markup=get_main_kb()
    )
