from aiogram.fsm.state import State, StatesGroup

class HabitStates(StatesGroup):
    choosing_habit_type = State()
    choosing_negative_habit = State()
    choosing_positive_habit = State()
    confirming_change = State()
