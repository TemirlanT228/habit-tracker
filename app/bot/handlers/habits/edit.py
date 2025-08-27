from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.models.enums import HabitKindEnum, WeekDayEnum
from app.bot.services.api_client import ApiClient
from .common import HabitStates
from .keyboards import get_main_kb, get_days_kb, get_kind_kb
import re

router = Router()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

@router.message(lambda m: m.text == "Edit Habit")
async def edit_habit(message: Message, state: FSMContext, api_client: ApiClient = None):
    habits = await api_client.get_habits(message.from_user.id)
    if not habits:
        await message.answer("У вас нет привычек для редактирования.")
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{idx+1}. {h.name}")] for idx, h in enumerate(habits)] + [[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(HabitStates.edit_select)
    await state.update_data(habits=[h.model_dump() for h in habits])
    await message.answer("Выберите привычку для редактирования:", reply_markup=kb)

@router.message(HabitStates.edit_select)
async def select_habit_to_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    habits = data["habits"]
    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer("Главное меню", reply_markup=get_main_kb())
        return
    import re
    match = re.match(r"(\d+)\. ", message.text)
    if not match:
        await message.answer("Пожалуйста, выберите привычку кнопкой.")
        return
    idx = int(match.group(1)) - 1
    if idx < 0 or idx >= len(habits):
        await message.answer("Пожалуйста, выберите привычку кнопкой.")
        return
    habit = habits[idx]
    await state.update_data(edit_habit=habit)
    await state.set_state(HabitStates.edit_field)
    await message.answer(
        "Что хотите изменить? (name, description, kind, days, time)\nМожно указать несколько через запятую:",
        reply_markup=None
    )

@router.message(HabitStates.edit_field)
async def edit_habit_field(message: Message, state: FSMContext):
    fields = [f.strip().lower() for f in message.text.split(',')]
    allowed = {'name', 'description', 'kind', 'days', 'time'}
    if not all(f in allowed for f in fields):
        await message.answer("Можно изменить только: name, description, kind, days. Перечислите нужные через запятую.", reply_markup=get_main_kb())
        return
    await state.update_data(edit_fields=fields, edit_field_idx=0, edit_updates={})
    await state.set_state(HabitStates.edit_value)
    first_field = fields[0]
    if first_field == "kind":
        await message.answer("Выберите тип привычки:", reply_markup=get_kind_kb())
    elif first_field == "days":
        await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=get_days_kb())
    elif first_field == "time":
        await message.answer("Введите новое время в формате ЧЧ:ММ (например, 08:30):")
    else:
        await message.answer(f"Введите новое значение для {first_field}:")



@router.message(HabitStates.edit_value)
async def edit_habit_value(message: Message, state: FSMContext, api_client: ApiClient = None):
    data = await state.get_data()
    habit = data["edit_habit"]
    fields = data["edit_fields"]
    idx = data["edit_field_idx"]
    updates = data.get("edit_updates", {})
    field = fields[idx]

    # Обработка выбора значения
    if field == "kind":
        kind_values = [e.value for e in HabitKindEnum]
        if message.text.lower() not in kind_values:
            await message.answer("Пожалуйста, выберите тип привычки:", reply_markup=get_kind_kb())
            return
        value = message.text.lower()
    elif field == "days":
        days_en = [e.value for e in WeekDayEnum]
        selected_days = updates.get("days", [])
        if message.text in days_en:
            if message.text not in selected_days:
                selected_days.append(message.text)
            updates["days"] = selected_days
            await state.update_data(edit_updates=updates)
            await message.answer("Добавьте ещё день или нажмите 'Done':", reply_markup=get_days_kb())
            return
        elif message.text == "Done":
            value = updates.get("days", [])
            if not value:
                await message.answer("Выберите хотя бы один день.", reply_markup=get_main_kb())
                return
        elif message.text == "Отмена":
            from .common import cancel_habit
            await cancel_habit(message, state)
            return
        else:
            await message.answer("Пожалуйста, выберите день недели из списка:", reply_markup=get_days_kb())
            return
    elif field == "time":
        time_pattern = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
        if not re.match(time_pattern, message.text):
            await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, 08:30)")
            return
        value = message.text
    else:
        value = message.text

    updates[field] = value
    idx += 1
    if idx < len(fields):
        next_field = fields[idx]
        await state.update_data(edit_field_idx=idx, edit_updates=updates)
        if next_field == "kind":
            await message.answer("Выберите тип привычки:", reply_markup=get_kind_kb())
        elif next_field == "days":
            await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=get_days_kb())
        elif next_field == "time":
            await message.answer("Введите новое время в формате ЧЧ:ММ (например, 08:30):")
        else:
            await message.answer(f"Введите новое значение для {next_field}:")
    else:
        await api_client.update_habit(habit_id=habit["id"], user_id=habit["user_id"], updates=updates)
        await state.clear()
        await message.answer("Привычка успешно обновлена!", reply_markup=get_main_kb())
