
from aiogram import Router
from aiogram.types import Message
from app.models.enums import WeekDayEnum
from app.bot.services.api_client import ApiClient

router = Router()

@router.message(lambda m: m.text == "List Habits")
async def list_habits(message: Message, api_client: ApiClient = None):
    habits = await api_client.get_habits(message.from_user.id)
    if not habits:
        await message.answer("У вас нет привычек.")
        return
    week_order = [e.value for e in WeekDayEnum]
    def sort_days(days):
        return sorted(days, key=lambda d: week_order.index(d))
    def format_time(t):
        if not t:
            return 'не указано'
        return t[:5] if len(t) >= 5 else t
    day_map = {
        'monday': 'Пн', 'tuesday': 'Вт', 'wednesday': 'Ср', 'thursday': 'Чт',
        'friday': 'Пт', 'saturday': 'Сб', 'sunday': 'Вс'
    }
    response = (
        "Твои привычки:\n" + "\n".join(
            f"{idx+1}. {h.name} ({h.kind}), дни: {', '.join(day_map.get(d, d) for d in sort_days(h.days))}, время: {format_time(h.time)}, описание: {h.description or 'нет'}"
            for idx, h in enumerate(habits)
        )
    )
    await message.answer(response)

