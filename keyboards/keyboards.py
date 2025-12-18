from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Сменить привычку"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="📋 Текущая привычка")]
        ],
        resize_keyboard=True
    )

def get_habit_type_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отказаться от"), KeyboardButton(text="✅ Приобрести")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def get_negative_habits_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Курение"), KeyboardButton(text="Алкоголь")],
            [KeyboardButton(text="Телефон допоздна"), KeyboardButton(text="Прокрастинация")],
            [KeyboardButton(text="Недостаток сна"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def get_positive_habits_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Зарядка утром"), KeyboardButton(text="Медитация")],
            [KeyboardButton(text="Пить воду"), KeyboardButton(text="Чтение книг")],
            [KeyboardButton(text="Режим питания"), KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )

def get_daily_check_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Сделал(а)"), KeyboardButton(text="❌ Не сделал(а)")]
        ],
        resize_keyboard=True
    )

def get_negative_check_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да, удалось!"), KeyboardButton(text="❌ Нет, не удалось")]
        ],
        resize_keyboard=True
    )

def get_confirmation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да, сменить"), KeyboardButton(text="❌ Нет, остаться")]
        ],
        resize_keyboard=True
    )