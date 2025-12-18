import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from .models import Base
from config import DATABASE_URL

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Класс для управления миграциями базы данных"""

    async def add_last_log_date_column(self):
        """Добавить столбец last_log_date в таблицу user_habits"""
        return await self.add_column_if_not_exists("user_habits", "last_log_date", "DATETIME")
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=False)

    async def init_database(self):
        """Инициализация базы данных (создание всех таблиц)"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ База данных успешно инициализирована")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            return False

    async def check_tables(self):
        """Проверка существования таблиц"""
        tables = ['users', 'user_habits', 'habit_logs']
        missing_tables = []

        async with self.engine.connect() as conn:
            for table in tables:
                try:
                    result = await conn.execute(
                        text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    )
                    if not result.fetchone():
                        missing_tables.append(table)
                except Exception as e:
                    logger.error(f"Ошибка проверки таблицы {table}: {e}")

        if missing_tables:
            logger.warning(f"⚠️ Отсутствующие таблицы: {missing_tables}")
            return False
        return True

    async def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str):
        """Добавить столбец если он не существует"""
        try:
            async with self.engine.connect() as conn:
                # Проверяем существование столбца
                result = await conn.execute(
                    text(f"PRAGMA table_info({table_name})")
                )
                columns = [row[1] for row in result.fetchall()]

                if column_name not in columns:
                    await conn.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    )
                    await conn.commit()
                    logger.info(f"✅ Добавлен столбец {column_name} в таблицу {table_name}")
                    return True
                else:
                    logger.info(f"ℹ️ Столбец {column_name} уже существует в {table_name}")
                    return False
        except Exception as e:
            logger.error(f"❌ Ошибка добавления столбца {column_name}: {e}")
            return False

    async def create_index(self, table_name: str, column_name: str, index_name: str = None):
        """Создать индекс для ускорения запросов"""
        if not index_name:
            index_name = f"idx_{table_name}_{column_name}"

        try:
            async with self.engine.connect() as conn:
                await conn.execute(
                    text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})")
                )
                await conn.commit()
                logger.info(f"✅ Создан индекс {index_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания индекса {index_name}: {e}")
            return False

    async def migrate_v1_to_v2(self):
        """Пример миграции с версии 1 на версию 2"""
        logger.info("🔄 Выполнение миграции v1 → v2")

        # 1. Добавляем новые столбцы
        await self.add_column_if_not_exists("user_habits", "notes", "TEXT")
        await self.add_column_if_not_exists("habit_logs", "comment", "TEXT")
        await self.add_column_if_not_exists("user_habits", "last_log_date", "DATETIME")  # Добавлено

        # 2. Создаем индексы для ускорения
        await self.create_index("habit_logs", "user_id")
        await self.create_index("habit_logs", "log_date")

        logger.info("✅ Миграция v1 → v2 завершена")
        return True

    async def backup_database(self, backup_path: str = "habits_backup.db"):
        """Создание резервной копии базы данных"""
        import shutil
        import os

        try:
            # SQLite база - просто копируем файл
            if os.path.exists("habits.db"):
                shutil.copy2("habits.db", backup_path)
                logger.info(f"✅ Резервная копия создана: {backup_path}")
                return True
            else:
                logger.warning("⚠️ Файл базы данных не найден для резервного копирования")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка создания резервной копии: {e}")
            return False

    async def run_all_migrations(self):
        """Запуск всех необходимых миграций"""
        logger.info("🚀 Запуск миграций базы данных...")

        # 1. Создаем резервную копию
        await self.backup_database()

        # 2. Проверяем/создаем таблицы
        if not await self.check_tables():
            logger.info("🔄 Создаем таблицы...")
            await self.init_database()

        # 3. Выполняем миграции по версиям
        await self.migrate_v1_to_v2()

        logger.info("🎉 Все миграции выполнены успешно!")
        return True


# Создание мигратора для использования в других файлах
migrator = DatabaseMigrator()


# Функция для запуска из командной строки
async def main():
    """Основная функция для запуска миграций"""
    print("=== Управление миграциями базы данных ===")
    print("1. Инициализировать базу данных")
    print("2. Проверить таблицы")
    print("3. Выполнить все миграции")
    print("4. Создать резервную копию")

    choice = input("Выберите действие (1-4): ").strip()

    if choice == "1":
        await migrator.init_database()
    elif choice == "2":
        if await migrator.check_tables():
            print("✅ Все таблицы существуют")
        else:
            print("⚠️ Некоторые таблицы отсутствуют")
    elif choice == "3":
        await migrator.run_all_migrations()
    elif choice == "4":
        await migrator.backup_database()
    else:
        print("❌ Неверный выбор")


if __name__ == "__main__":
    asyncio.run(main())