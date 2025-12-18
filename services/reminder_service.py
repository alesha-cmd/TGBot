"""
Сервис напоминаний для бота
"""
import logging
from aiogram import Bot
import asyncio
from datetime import datetime
from typing import Dict, Set
from keyboards.keyboards import get_daily_check_keyboard, get_negative_check_keyboard

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик если его нет
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Глобальная переменная для бота
bot_instance: Bot = None

# Хранилище активных задач напоминаний
active_reminders: Dict[int, asyncio.Task] = {}
# Словарь для хранения информации о привычках пользователей
user_habits: Dict[int, dict] = {}
# Множество для отслеживания пользователей, у которых уже запущены напоминания
active_users: Set[int] = set()
# Счетчик отправок напоминаний для каждого пользователя
reminder_counts: Dict[int, int] = {}


def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot


async def schedule_reminders(user_id: int, habit: str, habit_type: str):
    """
    Запланировать напоминания для пользователя
    Теперь напоминания будут приходить регулярно ДЛЯ ВСЕХ типов привычек
    """
    logger.info(f"📅 Запланированы напоминания для {user_id}: {habit} ({habit_type})")

    # Сохраняем информацию о привычке
    user_habits[user_id] = {
        'habit': habit,
        'habit_type': habit_type
    }

    # Инициализируем счетчик отправок
    reminder_counts[user_id] = 0

    # Если у пользователя уже есть активные напоминания, останавливаем их
    if user_id in active_reminders:
        await stop_reminders(user_id)

    # Запускаем цикл напоминаний
    task = asyncio.create_task(
        reminder_loop(user_id, habit, habit_type)
    )
    active_reminders[user_id] = task
    active_users.add(user_id)

    # Отправляем первое напоминание сразу
    await send_reminder(user_id, habit, habit_type)


async def stop_reminders(user_id: int):
    """Остановить напоминания для пользователя"""
    if user_id in active_reminders:
        active_reminders[user_id].cancel()
        del active_reminders[user_id]

    if user_id in active_users:
        active_users.remove(user_id)

    if user_id in user_habits:
        del user_habits[user_id]

    if user_id in reminder_counts:
        del reminder_counts[user_id]

    logger.info(f"⏹️ Напоминания остановлены для пользователя {user_id}")


async def reminder_loop(user_id: int, habit: str, habit_type: str):
    """
    Основной цикл отправки напоминаний
    Отправляет напоминания каждые 30 секунд для ВСЕХ типов привычек
    """
    try:
        while True:
            # Ждем 30 секунд между напоминаниями
            await asyncio.sleep(30)

            # Проверяем, не отменена ли задача
            if user_id not in active_users:
                break

            # Отправляем напоминание для ЛЮБОГО типа привычки
            await send_reminder(user_id, habit, habit_type)

    except asyncio.CancelledError:
        # Задача была отменена - нормальное завершение
        logger.info(f"🔇 Цикл напоминаний отменен для {user_id}")
        if user_id in active_users:
            active_users.remove(user_id)
    except Exception as e:
        logger.error(f"❌ Ошибка в цикле напоминаний для {user_id}: {e}")
        if user_id in active_users:
            active_users.remove(user_id)


async def send_reminder(user_id: int, habit: str, habit_type: str):
    """Отправка одного напоминания для ЛЮБОГО типа привычки"""
    global bot_instance

    if not bot_instance:
        logger.error("❌ Бот не установлен в reminder_service")
        return

    try:
        current_time = datetime.now().strftime('%H:%M:%S')

        # Увеличиваем счетчик отправок
        reminder_counts[user_id] = reminder_counts.get(user_id, 0) + 1
        send_count = reminder_counts[user_id]

        if habit_type == "negative":
            # Для отрицательных привычек
            await bot_instance.send_message(
                user_id,
                f"🔔 Напоминание: сегодня ваша цель - день без '{habit}'! Ты справишься! 💪\n"
                f"⏰ Время: {current_time}\n"
                f"🔁 Отправка №{send_count}",
                reply_markup=get_negative_check_keyboard()
            )
        else:
            # Для положительных привычек
            morning_habits = ["Зарядка утром", "Пить воду", "Режим питания"]

            if habit in morning_habits:
                message = f"🌅 Доброе утро! Не забудь про '{habit}' сегодня!\n⏰ {current_time}"
            else:
                message = f"🌙 Добрый вечер! Самое время для '{habit}'!\n⏰ {current_time}"

            # Добавляем счетчик отправок
            message += f"\n🔁 Отправка №{send_count}"

            await bot_instance.send_message(
                user_id,
                message,
                reply_markup=get_daily_check_keyboard()
            )

        logger.info(f"✅ Напоминание отправлено пользователю {user_id} ({habit_type}) в {current_time}, отправка №{send_count}")

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке напоминания {user_id}: {e}")


async def send_demo_reminder(user_id: int, habit: str, habit_type: str):
    """
    Демонстрационное напоминание (через 5 секунд) - один раз
    ИСПОЛЬЗОВАТЬ ТОЛЬКО ДЛЯ ТЕСТОВ, а не для реальных напоминаний!
    """
    global bot_instance

    logger.info(f"🧪 Запуск демо-напоминания для пользователя {user_id}")

    await asyncio.sleep(5)  # Ждем 5 секунд для демонстрации

    if not bot_instance:
        logger.error("❌ Бот не установлен в reminder_service")
        return

    try:
        if habit_type == "negative":
            await bot_instance.send_message(
                user_id,
                f"🔔 Демо-напоминание: сегодня ваша цель - день без '{habit}'! 💪\n"
                f"⚠️ Это демо-версия (только один раз)",
                reply_markup=get_negative_check_keyboard()
            )
        else:
            await bot_instance.send_message(
                user_id,
                f"🔔 Демо-напоминание: не забудь про '{habit}' сегодня! ✅\n"
                f"⚠️ Это демо-версия (только один раз)",
                reply_markup=get_daily_check_keyboard()
            )

        logger.info(f"✅ Демо-напоминание отправлено пользователю {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке демо-напоминания: {e}")


async def send_morning_reminder(user_id: int, habit: str):
    """Утреннее напоминание"""
    if bot_instance:
        await bot_instance.send_message(
            user_id,
            f"🌅 Доброе утро! Напоминаю: сегодня цель - день без '{habit}'!",
            reply_markup=get_negative_check_keyboard()
        )


async def send_evening_check(user_id: int, habit: str):
    """Вечерняя проверка"""
    if bot_instance:
        await bot_instance.send_message(
            user_id,
            f"🌙 Привет! Как прошел день? Удалось избежать '{habit}'?",
            reply_markup=get_negative_check_keyboard()
        )


async def get_active_users():
    """Получить список пользователей с активными напоминаниями"""
    return list(active_users)


async def is_user_active(user_id: int):
    """Проверить, есть ли у пользователя активные напоминания"""
    return user_id in active_users


async def cleanup_user_reminders(user_id: int):
    """
    Очистить все напоминания пользователя при выходе из привычки
    Вызывайте эту функцию при удалении/остановке привычки!
    """
    await stop_reminders(user_id)
    logger.info(f"🧹 Очищены напоминания для пользователя {user_id}")