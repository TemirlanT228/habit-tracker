from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.services.api_client import ApiClient
from app.schemas.habit import HabitCreate

router = Router()

class HabitStates(StatesGroup):
    name = State()
    description = State()
    kind = State()
    days = State()

@router.message(Command("cancel"))
async def cancel_habit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=None)


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
        await state.clear()
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Создание привычки отменено.", reply_markup=main_kb)
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
        await state.clear()
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Создание привычки отменено.", reply_markup=main_kb)
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
        await state.clear()
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Создание привычки отменено.", reply_markup=main_kb)
        return
    if message.text.lower() not in ["good", "bad"]:
        await message.answer("Пожалуйста, выберите 'Good' или 'Bad'.")
        return
    await state.update_data(kind=message.text.lower())
    await state.set_state(HabitStates.days)
    days_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
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
        # Получить user_id по telegram_id
        user = await api_client.get_user_by_telegram_id(message.from_user.id)
        habit_data = HabitCreate(
            user_id=user.id,
            name=data["name"],
            description=data["description"],
            kind=data["kind"],
            days=days
        )
        await api_client.create_habit(habit_data)
        await state.clear()
        # Вернуть пользователя в главное меню
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Привычка успешно создана! 🎉", reply_markup=main_kb)
    elif message.text == "Отмена":
        await state.clear()
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Start")],
                [KeyboardButton(text="Add Habit")],
                [KeyboardButton(text="List Habits")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Создание привычки отменено.", reply_markup=main_kb)
    else:
        days.append(message.text)
        await state.update_data(days=days)
        days_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        keyboard = [[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]]
        days_kb = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Добавьте ещё день или нажмите 'Done':", reply_markup=days_kb)

@router.message(lambda m: m.text == "List Habits")
async def list_habits(message: Message, api_client: ApiClient = None):
    habits = await api_client.get_habits(message.from_user.id)
    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Habit")],
            [KeyboardButton(text="List Habits")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    if not habits:
        await message.answer("У вас нет привычек.", reply_markup=main_kb)
        return
    response = "Твои привычки:\n" + "\n".join(
        f"- {h.name} ({h.kind}), дни: {', '.join(h.days)}, описание: {h.description or 'нет'}"
        for h in habits
    )
    await message.answer(response, reply_markup=main_kb)

@router.message()
async def unknown_message(message: Message):
    await message.answer("Пожалуйста, используйте команды /start, /add_habit, /list_habits, /cancel.")