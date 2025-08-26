from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from app.models.enums import HabitKindEnum, WeekDayEnum
from app.bot.services.api_client import ApiClient
from .common import HabitStates

router = Router()

@router.message(lambda m: m.text == "Edit Habit")
async def edit_habit(message: Message, state: FSMContext, api_client: ApiClient = None):
    habits = await api_client.get_habits(message.from_user.id)
    if not habits:
        await message.answer("У вас нет привычек для редактирования.")
        return
    text = "Выберите привычку для редактирования:\n" + "\n".join(
        f"{idx}. {h.name}" for idx, h in enumerate(habits, 1)
    )
    await state.set_state(HabitStates.edit_select)
    await state.update_data(habits=habits)
    await message.answer(text)

@router.message(HabitStates.edit_select)
async def select_habit_to_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    habits = data["habits"]
    try:
        idx = int(message.text) - 1
        habit = habits[idx]
    except (ValueError, IndexError):
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")],
                [KeyboardButton(text="Edit Habit")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Пожалуйста, выберите корректный номер привычки.", reply_markup=main_kb)
        return
    await state.update_data(edit_habit=habit)
    await state.set_state(HabitStates.edit_field)
    await message.answer(
        "Что хотите изменить? (name, description, kind, days)\nМожно указать несколько через запятую:"
    )

@router.message(HabitStates.edit_field)
async def edit_habit_field(message: Message, state: FSMContext):
    fields = [f.strip().lower() for f in message.text.split(',')]
    allowed = {'name', 'description', 'kind', 'days'}
    if not all(f in allowed for f in fields):
        main_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Create Habit")],
                [KeyboardButton(text="List Habits")],
                [KeyboardButton(text="Edit Habit")]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        await message.answer("Можно изменить только: name, description, kind, days. Перечислите нужные через запятую.", reply_markup=main_kb)
        return
    await state.update_data(edit_fields=fields, edit_field_idx=0, edit_updates={})
    await state.set_state(HabitStates.edit_value)
    first_field = fields[0]
    if first_field == "kind":
        kind_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="good"), KeyboardButton(text="bad")], [KeyboardButton(text="Отмена")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Выберите тип привычки:", reply_markup=kind_kb)
    elif first_field == "days":
        days_en = [e.value for e in WeekDayEnum]
        days_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=days_kb)
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
            kind_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="good"), KeyboardButton(text="bad")], [KeyboardButton(text="Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            main_kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Create Habit")],
                    [KeyboardButton(text="List Habits")],
                    [KeyboardButton(text="Edit Habit")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
            await message.answer("Пожалуйста, выберите тип привычки:", reply_markup=kind_kb)
            return
        value = message.text.lower()
    elif field == "days":
        days_en = [e.value for e in WeekDayEnum]
        selected_days = updates.get("days", [])
        if message.text in days_en:
            if message.text not in selected_days:
                selected_days.append(message.text)
            updates["days"] = selected_days
            days_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await state.update_data(edit_updates=updates)
            await message.answer("Добавьте ещё день или нажмите 'Done':", reply_markup=days_kb)
            return
        elif message.text == "Done":
            value = updates.get("days", [])
            if not value:
                main_kb = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="Create Habit")],
                        [KeyboardButton(text="List Habits")],
                        [KeyboardButton(text="Edit Habit")]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=False
                )
                await message.answer("Выберите хотя бы один день.", reply_markup=main_kb)
                return
        elif message.text == "Отмена":
            from .common import cancel_habit
            await cancel_habit(message, state)
            return
        else:
            days_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            main_kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Create Habit")],
                    [KeyboardButton(text="List Habits")],
                    [KeyboardButton(text="Edit Habit")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
            await message.answer("Пожалуйста, выберите день недели из списка:", reply_markup=days_kb)
            return
    else:
        value = message.text

    updates[field] = value
    idx += 1
    if idx < len(fields):
        next_field = fields[idx]
        await state.update_data(edit_field_idx=idx, edit_updates=updates)
        if next_field == "kind":
            kind_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="good"), KeyboardButton(text="bad")], [KeyboardButton(text="Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer("Выберите тип привычки:", reply_markup=kind_kb)
        elif next_field == "days":
            days_en = [e.value for e in WeekDayEnum]
            days_kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=day)] for day in days_en] + [[KeyboardButton(text="Done")], [KeyboardButton(text="Отмена")]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer("Выберите дни недели (нажимайте по одному, затем 'Done'):", reply_markup=days_kb)
        else:
            await message.answer(f"Введите новое значение для {next_field}:")
    else:
        await api_client.update_habit(habit_id=habit.id, user_id=habit.user_id, updates=updates)
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
        await message.answer("Привычка успешно обновлена!", reply_markup=main_kb)
