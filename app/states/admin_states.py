from aiogram.fsm.state import State, StatesGroup


class Admin(StatesGroup):
    admin = State()
    broadcast = State()
    broadcast_text = State()
    broadcast_pic = State()