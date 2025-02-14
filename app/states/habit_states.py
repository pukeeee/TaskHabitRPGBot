from aiogram.fsm.state import State, StatesGroup


class Habit(StatesGroup):
    habitText = State()
    choosingDays = State()
    setExp = State()
    editHabitText = State()
    editDays = State()
    editExp = State()