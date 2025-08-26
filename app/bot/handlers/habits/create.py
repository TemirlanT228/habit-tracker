from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.bot.services.api_client import ApiClient
from app.bot.schemas.habit import HabitCreate
from app.models.enums import HabitKindEnum, WeekDayEnum
from .common import cancel_habit, HabitStates

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
    kind_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Good"), KeyboardButton(text="Bad")], [KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите тип привычки:", reply_markup=kind_kb)

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
    days_en = [e.value for e in WeekDayEnum]
    keyboard = [[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]]
    days_kb = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=days_kb)

@router.message(HabitStates.days)
async def process_days(message: Message, state: FSMContext, api_client: ApiClient = None):
    data = await state.get_data()
    days = data.get("days", [])
    if message.text.lower() == "done":
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        if not user:
            main_kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Create Habit")],
                    [KeyboardButton(text="List Habits")],
                    [KeyboardButton(text="Edit Habit")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
            await message.answer(
                "Ошибка: пользователь не найден. Пожалуйста, используйте /start для регистрации.",
                reply_markup=main_kb
            )
            await state.clear()
            return
        habit_data = HabitCreate(
            user_id=user.id,
            name=data["name"],
            description=data["description"],
            kind=data["kind"],
            days=days
        )
        await api_client.create_habit(habit_data)
        await state.clear()
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")],
                [KeyboardButton(text="Edit Habit")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer(
            "Привычка успешно создана! 🎉\n\nЧтобы отредактировать привычку, нажмите 'Edit Habit' в меню.",
            reply_markup=main_kb
        )
    elif message.text == "Отмена":
        await cancel_habit(message, state)
    else:
        days.append(message.text)
        await state.update_data(days=days)
        days_en = [e.value for e in WeekDayEnum]
        keyboard = [[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]]
        days_kb = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Добавьте ещё день или нажмите 'Done':", reply_markup=days_kb)
