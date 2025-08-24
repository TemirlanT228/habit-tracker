from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.bot.services.api_client import ApiClient

router = Router()

@router.message(CommandStart())
async def start_command(message: Message, state, api_client: ApiClient):
    telegram_id = message.from_user.id
    user_name = message.from_user.username
    await api_client.create_user(telegram_id=telegram_id, username=user_name)

    # Проверяем, есть ли активное состояние FSM (то есть пользователь уже начал сценарий)
    current_state = await state.get_state()
    if current_state:
        # Если пользователь уже в сценарии, не показываем меню
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Habit")],
            [KeyboardButton(text="List Habits")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(
        "Привет! Я бот для отслеживания привычек.\n\nНажми 'Create Habit', чтобы добавить новую привычку, или 'List Habits', чтобы посмотреть свои привычки.",
        reply_markup=keyboard
    )