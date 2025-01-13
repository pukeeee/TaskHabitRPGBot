from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    startMenu = State()
    todo = State()
    habits = State()


class HabitState(StatesGroup):
    habitText = State()
    choosingDays = State()
    setExp = State()
    edithabitText = State()
    editDays = State()
    editExp = State()

class TaskState(StatesGroup):
    taskEdit = State()


class UserRPG(StatesGroup):
    setName = State()
    setRace = State()
    setSex = State()
    setClass = State()
    changeName = State()
    changeAvatar = State()