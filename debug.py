import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_database_structure():
    """Проверить структуру базы данных"""
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.connect() as conn:
            # Проверим таблицу user_habits
            print("\n=== Структура таблицы user_habits ===")
            result = await conn.execute(
                text("PRAGMA table_info(user_habits)")
            )
            columns = []
            for row in result.fetchall():
                columns.append(row[1])
                print(f"  {row[1]} ({row[2]})")

            # Проверим, есть ли last_log_date
            if "last_log_date" not in columns:
                print("\n⚠️ ОШИБКА: Столбец last_log_date отсутствует!")
                print("Добавляем столбец...")

                await conn.execute(
                    text("ALTER TABLE user_habits ADD COLUMN last_log_date DATETIME")
                )
                await conn.commit()
                print("✅ Столбец last_log_date добавлен")

            # Проверим данные для пользователя (вставьте свой user_id)
            user_id = input("\nВведите ваш user_id для проверки: ").strip()
            if user_id:
                result = await conn.execute(
                    text(f"SELECT * FROM user_habits WHERE user_id = {user_id}")
                )
                habit = result.fetchone()
                if habit:
                    print(f"\n=== Данные привычки для user_id {user_id} ===")
                    print(f"ID: {habit[0]}")
                    print(f"user_id: {habit[1]}")
                    print(f"current_habit: {habit[2]}")
                    print(f"habit_type: {habit[3]}")
                    print(f"current_streak: {habit[4]}")
                    print(f"best_streak: {habit[5]}")
                    print(f"total_days: {habit[6]}")
                    print(f"created_at: {habit[7]}")
                    print(f"updated_at: {habit[8]}")
                    print(f"last_log_date: {habit[9] if len(habit) > 9 else 'НЕТ СТОЛБЦА'}")
                else:
                    print(f"⚠️ Привычка для user_id {user_id} не найдена")

                # Проверим логи
                result = await conn.execute(
                    text(f"SELECT * FROM habit_logs WHERE user_id = {user_id} ORDER BY log_date DESC")
                )
                logs = result.fetchall()
                print(f"\n=== Логи для user_id {user_id} ({len(logs)} записей) ===")
                for log in logs:
                    print(f"  {log[5]} - {log[3]} - успех: {log[4]}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await engine.dispose()


async def fix_database():
    """Исправить структуру базы данных"""
    engine = create_async_engine(DATABASE_URL, echo=False)

    try:
        async with engine.connect() as conn:
            # 1. Добавить last_log_date если его нет
            result = await conn.execute(
                text("PRAGMA table_info(user_habits)")
            )
            columns = [row[1] for row in result.fetchall()]

            if "last_log_date" not in columns:
                print("Добавляем столбец last_log_date...")
                await conn.execute(
                    text("ALTER TABLE user_habits ADD COLUMN last_log_date DATETIME")
                )
                await conn.commit()
                print("✅ Столбец last_log_date добавлен")

            # 2. Проверить индексы
            print("\n=== Индексы базы данных ===")
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='index'")
            )
            indexes = result.fetchall()
            for idx in indexes:
                print(f"  {idx[0]}")

            print("\n✅ База данных проверена и исправлена")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await engine.dispose()


async def main():
    print("=== Отладка базы данных ===")
    print("1. Проверить структуру базы")
    print("2. Исправить структуру базы")
    print("3. Создать тестовые данные")

    choice = input("Выберите действие (1-3): ").strip()

    if choice == "1":
        await check_database_structure()
    elif choice == "2":
        await fix_database()
    elif choice == "3":
        await create_test_data()
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    asyncio.run(main())