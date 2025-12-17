import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.database import db
from handlers.start_handler import cmd_start, cmd_menu
from handlers.menu_handlers import (
    show_current_habit, show_statistics, change_habit_start,
    confirm_habit_change, cancel_habit_change
)
from handlers.habit_handlers import (
    go_back, process_habit_type, process_negative_habit,
    process_positive_habit, process_daily_check
)
from utils.states import HabitStates

from services.reminder_service import set_bot
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Устанавливаем бота в сервис напоминаний
set_bot(bot)

# Регистрация обработчиков
def register_handlers():
    # Команды
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_menu, Command("menu"))

    # Главное меню
    dp.message.register(show_current_habit, F.text == "📋 Текущая привычка")
    dp.message.register(show_statistics, F.text == "📊 Статистика")
    dp.message.register(change_habit_start, F.text == "🔄 Сменить привычку")

    # Смена привычки
    dp.message.register(confirm_habit_change, HabitStates.confirming_change, F.text == "✅ Да, сменить")
    dp.message.register(cancel_habit_change, HabitStates.confirming_change, F.text == "❌ Нет, остаться")

    # Навигация
    dp.message.register(go_back, F.text == "🔙 Назад")

    # Выбор привычек
    dp.message.register(process_habit_type, HabitStates.choosing_habit_type,
                        F.text.in_(["❌ Отказаться от", "✅ Приобрести"]))
    dp.message.register(process_negative_habit, HabitStates.choosing_negative_habit,
                        F.text.in_(["Курение", "Алкоголь", "Телефон допоздна", "Прокрастинация", "Недостаток сна"]))
    dp.message.register(process_positive_habit, HabitStates.choosing_positive_habit,
                        F.text.in_(["Зарядка утром", "Медитация", "Пить воду", "Чтение книг", "Режим питания"]))

    # Ежедневные проверки
    dp.message.register(process_daily_check,
                        F.text.in_(["✅ Сделал(а)", "❌ Не сделал(а)", "✅ Да, удалось!", "❌ Нет, не удалось"]))


async def main():
    logger.info("Starting bot...")
    from services.reminder_service import set_bot
    set_bot(bot)
    # Инициализация БД
    await db.init_models()
    logger.info("Database initialized")

    # Регистрация обработчиков
    register_handlers()

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())