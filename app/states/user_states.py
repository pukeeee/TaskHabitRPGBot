from aiogram.fsm.state import State, StatesGroup


class User(StatesGroup):
    startMenu = State()
    todo = State()
    habits = State()