from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)


class UserHabit(Base):
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    current_habit = Column(String(100))
    habit_type = Column(String(20))  # 'positive' or 'negative'
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)
    total_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_log_date = Column(DateTime)  # Добавлено


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    habit_name = Column(String(100))
    success = Column(Boolean)
    log_date = Column(DateTime, default=datetime.utcnow)