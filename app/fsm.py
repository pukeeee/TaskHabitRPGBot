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
    addTask = State()


class UserRPG(StatesGroup):
    setName = State()
    setAvatar = State()
    changeName = State()
    changeAvatar = State()


class Admin(StatesGroup):
    admin = State()
    broadcast = State()
    broadcast_text = State()
    broadcast_pic = State()
