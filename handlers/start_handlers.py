from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.database import db
from utils.states import HabitStates
from keyboards.keyboards import get_habit_type_keyboard, get_main_menu_keyboard


async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        # Создаем/получаем пользователя
        user = await db.get_or_create_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
        # ОШИБКА: Использование print вместо logging
        print(f"✅ Пользователь создан/получен: {user_id}")

        # Проверяем есть ли привычка
        habit = await db.get_user_habit(user_id)
        # ОШИБКА: Использование print вместо logging
        print(f"✅ Привычка получена: {habit}")

        if habit:
            # Если привычка есть - показываем меню
            habit_info = (
                f"С возвращением! 👋\n"
                f"📋 Текущая привычка: {habit.current_habit}\n"
                f"🔥 Текущая серия: {habit.current_streak} дней"
            )
            await message.answer(habit_info, reply_markup=get_main_menu_keyboard())
            await state.clear()
            # ОШИБКА: Использование print вместо logging
            print("✅ Показано главное меню")
        else:
            # Если привычки нет - предлагаем выбрать
            await message.answer(
                "Привет! Я помогу тебе работать с одной привычкой. "
                "Выбери, что для тебя важнее всего прямо сейчас.",
                reply_markup=get_habit_type_keyboard()
            )
            await state.set_state(HabitStates.choosing_habit_type)
            # ОШИБКА: Использование print вместо logging
            print("✅ Перешли к выбору типа привычки")

    except Exception as e:
        # ОШИБКА: Использование print вместо logging
        print(f"❌ Ошибка в cmd_start: {e}")
        # Показываем меню даже при ошибке
        await message.answer(
            "Привет! Давайте выберем привычку для отслеживания.",
            reply_markup=get_habit_type_keyboard()
        )
        await state.set_state(HabitStates.choosing_habit_type)


async def cmd_menu(message: types.Message):
    user_id = message.from_user.id
    try:
        habit = await db.get_user_habit(user_id)

        if not habit:
            await message.answer(
                "У вас еще нет привычки. Выберите ее через /start",
                reply_markup=get_habit_type_keyboard()
            )
            return

        habit_info = (
            f"📋 Текущая привычка: {habit.current_habit}\n"
            f"🔥 Текущая серия: {habit.current_streak} дней\n"
            f"🏆 Лучшая серия: {habit.best_streak} дней\n"
            f"📅 Всего дней с привычкой: {habit.total_days}"
        )

        await message.answer(habit_info, reply_markup=get_main_menu_keyboard())
    except Exception as e:
        # ОШИБКА: Использование print вместо logging
        print(f"❌ Ошибка в cmd_menu: {e}")
        await message.answer("Произошла ошибка. Попробуйте /start")