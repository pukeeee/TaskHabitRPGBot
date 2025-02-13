from aiogram.fsm.state import State, StatesGroup


class Task(StatesGroup):
    taskEdit = State()
    addTask = State()
    setExp = State()
    editExp = State()