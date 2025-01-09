from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.messages import Message
from database.requests import getTask, getHabits

async def startReplyKb(language_code: str):
    todoButton = "Task Tracker"
    habitButton = "Habit Tracker"
    profile = "My profile"
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = todoButton), KeyboardButton(text = habitButton)], [KeyboardButton(text = profile)]],
                                                    resize_keyboard = True)
    return replyKeyboard

###########
"""Tasks"""
###########

async def delTasks(tg_id):
    tasks = await getTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text = task.task, callback_data = f"deltask_{task.id}"))
    return keyboard.adjust(1).as_markup()

async def editTasks(tg_id):
    tasks = await getTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text = task.task, callback_data = f"edittask_{task.id}"))
    return keyboard.adjust(1).as_markup()

async def todoReplyKB(language_code: str):
    taskListButton = "My tasks"
    backToMain = "🏠 Home"
    info = "Info"
    editTask = "Edit task"
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = editTask), KeyboardButton(text = taskListButton)], 
                                                    [KeyboardButton(text = info), KeyboardButton(text = backToMain)]],
                                                    resize_keyboard = True)
    return replyKeyboard

############
"""habits"""
############

async def habitsReplyKB(language_code: str):
    habitListButton = "My habits"
    todayHabits = "Today habits"
    backToMain = "🏠 Home"
    addHabit = "Add habit"
    info = "Info"
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = addHabit)],
                                                    [KeyboardButton(text = habitListButton), KeyboardButton(text = todayHabits)],
                                                    [KeyboardButton(text = info) ,KeyboardButton(text = backToMain)]
                                                    ],resize_keyboard = True)
    return replyKeyboard

async def addHabitReplyKB(language_code: str):
    backToMain = "🏠 Home"
    backToHabit = "🔙 Habit"
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = backToHabit)], 
                                                    [KeyboardButton(text = backToMain)]
                                                    ],resize_keyboard = True)
    return replyKeyboard

async def delHabits(tg_id):
    habits = await getHabits(tg_id)
    keyboard = InlineKeyboardBuilder()
    for habit in habits:
        keyboard.add(InlineKeyboardButton(text = habit.name, callback_data = f"delhabit_{habit.id}"))
    return keyboard.adjust(1).as_markup()