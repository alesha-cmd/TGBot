from aiogram import types, F
from aiogram.fsm.context import FSMContext
from database.database import db
from utils.states import HabitStates
from keyboards.keyboards import (
    get_main_menu_keyboard, get_habit_type_keyboard,
    get_negative_habits_keyboard, get_positive_habits_keyboard,
    get_daily_check_keyboard, get_negative_check_keyboard
)
from services.reminder_service import schedule_reminders


async def go_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state in [HabitStates.choosing_negative_habit, HabitStates.choosing_positive_habit]:
        await message.answer("Выбери тип привычки:", reply_markup=get_habit_type_keyboard())
        await state.set_state(HabitStates.choosing_habit_type)


async def process_habit_type(message: types.Message, state: FSMContext):
    if message.text == "❌ Отказаться от":
        await message.answer("Выбери привычку, от которой хочешь отказаться:",
                             reply_markup=get_negative_habits_keyboard())
        await state.set_state(HabitStates.choosing_negative_habit)
    else:
        await message.answer("Выбери привычку, которую хочешь приобрести:",
                             reply_markup=get_positive_habits_keyboard())
        await state.set_state(HabitStates.choosing_positive_habit)


async def process_negative_habit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit = message.text

    await db.create_user_habit(user_id, habit, "negative")

    await message.answer(
        f"Отлично! Теперь мы будем каждый день отслеживать: {habit}.\n"
        f"Я буду напоминать тебе утром и спрашивать вечером о результате.",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

    # Запускаем напоминания
    await schedule_reminders(user_id, habit, "negative")


async def process_positive_habit(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit = message.text

    await db.create_user_habit(user_id, habit, "positive")

    await message.answer(
        f"Отлично! Теперь мы будем каждый день отслеживать: {habit}.\n"
        f"Я буду напоминать тебе в подходящее время.",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

    # Запускаем напоминания
    await schedule_reminders(user_id, habit, "positive")


async def process_daily_check(message: types.Message):
    user_id = message.from_user.id
    habit = await db.get_user_habit(user_id)

    if not habit:
        await message.answer("Сначала выбери привычку через /start")
        return

    success = message.text in ["✅ Сделал(а)", "✅ Да, удалось!"]

    # Используем упрощенную версию для отладки
    updated_habit = await db.add_habit_log_simple(user_id, habit.current_habit, success)

    if updated_habit:
        if success:
            response = f"Отлично! Ты молодец. Твоя серия: {updated_habit.current_streak} дней подряд!"
        else:
            response = "Бывает. Главное — не сдаваться. Завтра новый день!"
    else:
        response = "Произошла ошибка при сохранении результата. Попробуй еще раз."

    await message.answer(response, reply_markup=get_main_menu_keyboard())