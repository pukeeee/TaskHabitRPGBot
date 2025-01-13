from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.messages import Message
from aiogram.fsm.context import FSMContext
from database.requests import getTask, getHabits, getTodayHabits
import html
from datetime import datetime
from config import IMG_FOLDER
import os



async def startReplyKb(language_code: str):
    todoButton = Message.get_message(language_code, "taskTrackerButton")
    habitButton = Message.get_message(language_code, "habitTrackerButton")
    profile = Message.get_message(language_code, "profileButton")
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = todoButton), KeyboardButton(text = habitButton)], [KeyboardButton(text = profile)]],
                                                    resize_keyboard = True)
    return replyKeyboard


#############
"""Profile"""
#############


async def regRase():
    keyboard = InlineKeyboardBuilder()
    items = os.listdir(IMG_FOLDER)
    
    for item in items:
        item_path =  os.path.join(IMG_FOLDER, item)
        if os.path.isdir(item_path):
            normalized_name = html.escape(item.strip())
            keyboard.add(InlineKeyboardButton(text = normalized_name,
                                            callback_data = f"raseFolder_{item}"
                                        )
                                    )
    keyboard.adjust(1)
    return keyboard.as_markup()



async def regSex(state):
    data = await state.get_data()
    selected_race_folder = data.get('selected_race_folder')
    keyboard = InlineKeyboardBuilder()
    race_path = os.path.join(IMG_FOLDER, selected_race_folder)
    items = os.listdir(race_path)
    
    for item in items:
        item_path = os.path.join(race_path, item)
        if os.path.isdir(item_path):
            normalized_name = html.escape(item.strip())
            keyboard.add(InlineKeyboardButton(text = normalized_name,
                                                callback_data = f"sexFolder_{item}"
                                            ))
    keyboard.add(InlineKeyboardButton(text = "🔙 Back", callback_data = "backToRace"))
    keyboard.adjust(1)
    return keyboard.as_markup()



async def regClass(state):
    data = await state.get_data()
    selected_race_folder = data.get('selected_race_folder')
    selected_sex_folder = data.get('selected_sex_folder')
    keyboard = InlineKeyboardBuilder()
    class_path = os.path.join(IMG_FOLDER, selected_race_folder, selected_sex_folder)
    items = os.listdir(class_path)
    
    for item in items:
        item_path = os.path.join(class_path, item)
        if os.path.isdir(item_path):
            normalized_name = html.escape(item.strip())
            keyboard.add(InlineKeyboardButton(
                text = normalized_name,
                callback_data = f"classFolder_{item}"
            ))
    keyboard.add(InlineKeyboardButton(text = "🔙 Back", callback_data = "backToSex"))
    keyboard.adjust(1)
    return keyboard.as_markup()



async def profileInLineKB():
    leaderBoardButton = InlineKeyboardButton(text = "Leaderboard", callback_data = "leaderboard")
    changeName = InlineKeyboardButton(text = "Change Name", callback_data = "changeName")
    changeAvatar = InlineKeyboardButton(text = "Change Character", callback_data = "changeAvatar")
    keyboard = InlineKeyboardMarkup(inline_keyboard = [[leaderBoardButton],
                                                    [changeAvatar, changeName]])
    return keyboard



async def avatarNavigationKB():
    backButton = InlineKeyboardButton(text = "⬅️ Назад", callback_data = "prev_img")
    nextButton = InlineKeyboardButton(text = "Вперед ➡️", callback_data = "next_img")
    doneButton = InlineKeyboardButton(text = "Готово", callback_data = "done_img")
    back = InlineKeyboardButton(text = "🔙 Back", callback_data = "backToClass")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[backButton, nextButton],
                                                    [doneButton],
                                                    [back]])
    return keyboard


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



async def taskListKB(language_code: str):
    editButton = InlineKeyboardButton(text = Message.get_message(language_code, "editTaskButton"), callback_data = "editTasks")
    deleteButton = InlineKeyboardButton(text = Message.get_message(language_code, "deleteTaskButton"), callback_data = "deleteTasks")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[editButton, deleteButton]])
    return keyboard



async def todoReplyKB(language_code: str):
    taskListButton = Message.get_message(language_code, "taskListButton")
    backToMain = Message.get_message(language_code, "homeButton")
    info = Message.get_message(language_code, "infoButton")
    addTaskButton = Message.get_message(language_code, "addTaskButton")
    doneTasksButton = Message.get_message(language_code, "doneTasksButton")
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = addTaskButton)],
                                                    [KeyboardButton(text = doneTasksButton), KeyboardButton(text = taskListButton)], 
                                                    [KeyboardButton(text = info), KeyboardButton(text = backToMain)]],
                                                    resize_keyboard = True)
    return replyKeyboard



async def addTaskReplyKB(language_code: str):
    backToMain = Message.get_message(language_code, "homeButton")
    backToTask = Message.get_message(language_code, "backToTaskButton")
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = backToTask)], 
                                                    [KeyboardButton(text = backToMain)]
                                                    ],resize_keyboard = True)
    return replyKeyboard


############
"""Habits"""
############


async def habitsReplyKB(language_code: str):
    habitListButton = Message.get_message(language_code, "habitListButton")
    todayHabits = Message.get_message(language_code, "todayHabitsButton")
    backToMain = Message.get_message(language_code, "homeButton")
    addHabit = Message.get_message(language_code, "addHabitButton")
    info = "Info"
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = addHabit)],
                                                    [KeyboardButton(text = habitListButton), KeyboardButton(text = todayHabits)],
                                                    [KeyboardButton(text = info) ,KeyboardButton(text = backToMain)]
                                                    ],resize_keyboard = True)
    return replyKeyboard



async def addHabitReplyKB(language_code: str):
    backToMain = Message.get_message(language_code, "homeButton")
    backToHabit = Message.get_message(language_code, "backToHabitButton")
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = backToHabit)], 
                                                    [KeyboardButton(text = backToMain)]
                                                    ],resize_keyboard = True)
    return replyKeyboard



async def habitsList(tg_id, language_code: str):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.row(InlineKeyboardButton(text = Message.get_message(language_code, "editHabitButton"), callback_data = "editHabits"),
                InlineKeyboardButton(text = Message.get_message(language_code, "deleteHabitButton"), callback_data = "deleteHabits"))
    return keyboard.as_markup()



async def deleteHabits(tg_id):
    habits = await getHabits(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for habit in habits:
        keyboard.add(InlineKeyboardButton(text = habit.name, callback_data = f"delhabit_{habit.id}"))
    keyboard.add(InlineKeyboardButton(text = "🔙 Back", callback_data = "backToHabitsList"))
    return keyboard.adjust(1).as_markup()



async def editHabits(tg_id):
    habits = await getHabits(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for habit in habits:
        keyboard.add(InlineKeyboardButton(text = habit.name, callback_data = f"edithabit_{habit.id}"))
    keyboard.add(InlineKeyboardButton(text = "🔙 Back", callback_data = "backToHabitsList"))
    return keyboard.adjust(1).as_markup()



async def selectWeekdaysKB(language_code: str, selected_days = None):
    if selected_days is None:
        selected_days = []
    
    days = [
        ("mon", "habitDays_mon"),
        ("tue", "habitDays_tue"),
        ("wed", "habitDays_wed"),
        ("thu", "habitDays_thu"),
        ("fri", "habitDays_fri"),
        ("sat", "habitDays_sat"),
        ("sun", "habitDays_sun")
    ]
    
    keyboard = InlineKeyboardBuilder()
    for dayName, dayCode in days:
        localizationDay = Message.get_message(language_code, dayName)
        buttonText = f"✅ {localizationDay}" if dayCode.split("_")[1] in selected_days else localizationDay
        keyboard.add(InlineKeyboardButton(text = buttonText, callback_data = dayCode))
    keyboard.add(InlineKeyboardButton(text = Message.get_message(language_code, "done"), callback_data = "habitDays_done"))
    keyboard.adjust(2)
    return keyboard.as_markup()



async def todayHabits(tg_id, language_code: str):
    currentDay = datetime.today().weekday()
    habits = await getTodayHabits(tg_id)
    keyboard = InlineKeyboardBuilder()

    today_habits = []
    for habit in habits:
        if len(habit.days_of_week) == 7 and habit.days_of_week[currentDay] == '1':
            today_habits.append(habit)

    if today_habits:
        for habit in today_habits:
            keyboard.add(InlineKeyboardButton(text = habit.name, callback_data = f"completedHabit_{habit.id}"))
    else:
        keyboard.add(InlineKeyboardButton(text = "No habits for today", callback_data = "no_today_habits"))
    return keyboard.adjust(1).as_markup()

