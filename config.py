import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = "sqlite+aiosqlite:///habits.db"

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("""
❌ BOT_TOKEN не найден в переменных окружения!

1. Убедитесь, что у вас есть файл .env
2. Добавьте в него строку:
   BOT_TOKEN=ваш_токен_бота_здесь

3. Получите токен у @BotFather в Telegram
""")