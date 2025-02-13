from aiogram.fsm.state import State, StatesGroup


class Habit(StatesGroup):
    habitText = State()
    choosingDays = State()
    setExp = State()
    edithabitText = State()
    editDays = State()
    editExp = State()