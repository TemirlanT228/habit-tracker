from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

# --- FSM состояния ---
class HabitStates(StatesGroup):
    name = State()
    description = State()
    kind = State()
    days = State()
    time = State()
    edit_select = State()
    edit_field = State()
    edit_value = State()
    list_select = State()

async def cancel_habit(message: Message, state: FSMContext):
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
    await message.answer("Действие отменено.", reply_markup=main_kb)

@router.message()
async def unknown_message(message: Message):
    await message.answer("Пожалуйста, используйте команды /start, /create_habit, /list_habits, /cancel.")
