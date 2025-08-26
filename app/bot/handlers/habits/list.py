from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from app.models.enums import WeekDayEnum
from app.bot.services.api_client import ApiClient

router = Router()

@router.message(lambda m: m.text == "List Habits")
async def list_habits(message: Message, api_client: ApiClient = None):
    habits = await api_client.get_habits(message.from_user.id)
    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Create Habit")],
            [KeyboardButton(text="List Habits")],
            [KeyboardButton(text="Edit Habit")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    if not habits:
        await message.answer("У вас нет привычек.", reply_markup=main_kb)
        return
    week_order = [e.value for e in WeekDayEnum]
    def sort_days(days):
        return sorted(days, key=lambda d: week_order.index(d))
    response = (
        "Твои привычки:\n" + "\n".join(
            f"{idx}. {h.name} ({h.kind}), дни: {', '.join(sort_days(h.days))}, описание: {h.description or 'нет'}"
            for idx, h in enumerate(habits, 1)
        ) +
        "\n\nЧтобы отредактировать привычку, нажмите 'Edit Habit' в меню."
    )
    await message.answer(response, reply_markup=main_kb)
