from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    startMenu = State()
    todo = State()
    habits = State()
    
class HabitState(StatesGroup):
    habitText = State()
    choosingDays = State()
    setExp = State()
    
class TaskState(StatesGroup):
    taskEdit = State()