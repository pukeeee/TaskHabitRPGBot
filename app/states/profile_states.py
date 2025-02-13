from aiogram.fsm.state import State, StatesGroup


class Profile(StatesGroup):
    setName = State()
    setAvatar = State()
    editAvatar = State()
    changeName = State()