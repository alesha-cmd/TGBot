from aiogram import types, F
from aiogram.fsm.context import FSMContext
from database.database import db
from utils.states import HabitStates
from keyboards.keyboards import get_main_menu_keyboard, get_confirmation_keyboard, get_habit_type_keyboard
from handlers.start_handler import cmd_menu

async def show_current_habit(message: types.Message):
    await cmd_menu(message)


async def show_statistics(message: types.Message):
    user_id = message.from_user.id
    habit = await db.get_user_habit(user_id)

    if not habit:
        await message.answer("Сначала выбери привычку через /start")
        return

    stats = (
        f"📊 Статистика по привычке '{habit.current_habit}':\n"
        f"🔥 Текущая серия: {habit.current_streak} дней\n"
        f"🏆 Лучшая серия: {habit.best_streak} дней\n"
        f"📅 Всего дней с привычкой: {habit.total_days}"
    )
    await message.answer(stats)


async def change_habit_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit = await db.get_user_habit(user_id)

    if not habit:
        await message.answer("Сначала выбери привычку через /start")
        return

    await message.answer(
        f"Ты уверен? Текущая серия из {habit.current_streak} дней будет сброшена.",
        reply_markup=get_confirmation_keyboard()
    )
    await state.set_state(HabitStates.confirming_change)


async def confirm_habit_change(message: types.Message, state: FSMContext):
    await message.answer("Хорошо! Давай выберем новую цель.",
                         reply_markup=get_habit_type_keyboard())
    await state.set_state(HabitStates.choosing_habit_type)


async def cancel_habit_change(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit = await db.get_user_habit(user_id)
    await message.answer(f"Отлично! Продолжаем работать над '{habit.current_habit}'.",
                         reply_markup=get_main_menu_keyboard())
    await state.clear()