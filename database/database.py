"""
SQLite база данных для Habit Tracker Bot
Упрощенная версия для отладки
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, func, and_, or_
from datetime import datetime, date, timedelta
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Базовый класс для моделей
Base = declarative_base()

# ======================
# МОДЕЛИ БАЗЫ ДАННЫХ
# ======================

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class UserHabit(Base):
    """Модель привычек пользователя"""
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    current_habit = Column(String(100), nullable=False)
    habit_type = Column(String(20), nullable=False)  # 'positive' или 'negative'
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    total_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_log_date = Column(DateTime)  # Добавляем поле для отслеживания последней записи

class HabitLog(Base):
    """Модель логов привычек"""
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    habit_name = Column(String(100), nullable=False)
    success = Column(Boolean, nullable=False)
    log_date = Column(DateTime, default=datetime.utcnow)

# ======================
# КЛАСС ДЛЯ РАБОТЫ С БД
# ======================

class SQLiteDatabase:
    """Класс для работы с SQLite"""

    def __init__(self):
        # Создаем асинхронный движок для SQLite
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=True,  # ВКЛЮЧАЕМ логи SQL запросов для отладки
            connect_args={"check_same_thread": False}  # Для SQLite
        )

        # Создаем фабрику сессий
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def init_models(self):
        """Создание всех таблиц в базе данных"""
        try:
            async with self.engine.begin() as conn:
                # Создаем все таблицы
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Таблицы SQLite успешно созданы")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц: {e}")
            return False

    # ======================
    # МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
    # ======================

    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None):
        """Получить или создать пользователя"""
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                user = result.scalar_one_or_none()

                if user:
                    # Обновляем данные если они изменились
                    if username and user.username != username:
                        user.username = username
                    if first_name and user.first_name != first_name:
                        user.first_name = first_name
                    await session.commit()
                    return user
                else:
                    # Создаем нового пользователя
                    user = User(
                        user_id=user_id,
                        username=username,
                        first_name=first_name
                    )
                    session.add(user)
                    await session.commit()
                    logger.info(f"✅ Новый пользователь создан: {user_id}")
                    return user

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Ошибка при работе с пользователем {user_id}: {e}")
                raise

    async def get_user(self, user_id: int):
        """Получить пользователя по ID"""
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"❌ Ошибка получения пользователя {user_id}: {e}")
                return None

    # ======================
    # МЕТОДЫ ДЛЯ ПРИВЫЧЕК
    # ======================

    async def get_user_habit(self, user_id: int):
        """Получить привычку пользователя"""
        async with self.async_session() as session:
            try:
                from sqlalchemy import select
                result = await session.execute(
                    select(UserHabit).where(UserHabit.user_id == user_id)
                )
                return result.scalar_one_or_none()
            except Exception as e:
                logger.error(f"❌ Ошибка получения привычки пользователя {user_id}: {e}")
                return None

    async def create_user_habit(self, user_id: int, habit_name: str, habit_type: str):
        """Создать или обновить привычку пользователя"""
        async with self.async_session() as session:
            try:
                # Удаляем старую привычку если есть
                existing_habit = await self.get_user_habit(user_id)
                if existing_habit:
                    await session.delete(existing_habit)

                # Создаем новую привычку
                habit = UserHabit(
                    user_id=user_id,
                    current_habit=habit_name,
                    habit_type=habit_type,
                    current_streak=0,
                    best_streak=0,
                    total_days=0,
                    last_log_date=None
                )
                session.add(habit)
                await session.commit()
                logger.info(f"✅ Привычка создана: {user_id} - {habit_name}")
                return habit
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Ошибка создания привычки для {user_id}: {e}")
                raise

    async def update_habit_streak_simple(self, user_id: int, success: bool):
        """Упрощенная версия обновления серии - для отладки"""
        async with self.async_session() as session:
            try:
                # Получаем привычку
                from sqlalchemy import select
                result = await session.execute(
                    select(UserHabit).where(UserHabit.user_id == user_id)
                )
                habit = result.scalar_one_or_none()

                if not habit:
                    logger.warning(f"⚠️ Привычка не найдена для пользователя {user_id}")
                    return None

                print(f"🔄 Обновление серии для {user_id}: текущая серия={habit.current_streak}, успех={success}")

                if success:
                    # Увеличиваем серию
                    habit.current_streak += 1
                    habit.total_days += 1

                    # Обновляем лучшую серию
                    if habit.current_streak > habit.best_streak:
                        habit.best_streak = habit.current_streak

                    print(f"✅ Серия увеличена: {habit.current_streak} дней")
                else:
                    # Сброс серии
                    habit.current_streak = 0
                    print(f"🔄 Серия сброшена")

                # Обновляем дату последнего лога
                habit.last_log_date = datetime.now()

                await session.commit()
                return habit

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Ошибка обновления серии для {user_id}: {e}")
                return None

    # ======================
    # МЕТОДЫ ДЛЯ ЛОГОВ
    # ======================

    async def add_habit_log_simple(self, user_id: int, habit_name: str, success: bool):
        """Упрощенная версия добавления лога - для отладки"""
        async with self.async_session() as session:
            try:
                print(f"📝 Добавление лога для {user_id}: {habit_name}, успех={success}")

                # Создаем новый лог
                log = HabitLog(
                    user_id=user_id,
                    habit_name=habit_name,
                    success=success,
                    log_date=datetime.now()
                )
                session.add(log)
                await session.commit()
                print(f"✅ Лог добавлен: {user_id} - {habit_name} - успех={success}")

                # Обновляем серию
                updated_habit = await self.update_habit_streak_simple(user_id, success)

                if updated_habit:
                    print(f"📊 Серия обновлена: {updated_habit.current_streak} дней")
                    return updated_habit
                else:
                    print(f"⚠️ Не удалось обновить серию")
                    return None

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Ошибка добавления лога для {user_id}: {e}")
                return None

    async def get_habit_stats(self, user_id: int):
        """Получить статистику привычки"""
        async with self.async_session() as session:
            try:
                from sqlalchemy import select, func, and_

                # Получаем привычку
                habit = await self.get_user_habit(user_id)
                if not habit:
                    return None

                print(f"📊 Получение статистики для {user_id}: текущая серия={habit.current_streak}")

                # Получаем общее количество успешных дней
                result = await session.execute(
                    select(func.count(HabitLog.id))
                    .where(and_(
                        HabitLog.user_id == user_id,
                        HabitLog.habit_name == habit.current_habit,
                        HabitLog.success == True
                    ))
                )
                total_success = result.scalar() or 0

                return {
                    'habit': habit,
                    'total_success': total_success,
                    'success_rate': (total_success / habit.total_days * 100) if habit.total_days > 0 else 0
                }
            except Exception as e:
                logger.error(f"❌ Ошибка получения статистики для {user_id}: {e}")
                return None

# Глобальный экземпляр БД
db = SQLiteDatabase()