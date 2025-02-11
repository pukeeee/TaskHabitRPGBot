from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.l10n import Message
from database.repositories import getHabits, getTodayHabits
from datetime import datetime

async def habitsReplyKB(language_code: str) -> ReplyKeyboardMarkup:
    habitListButton = Message.get_message(language_code, "habitListButton")
    todayHabits = Message.get_message(language_code, "todayHabitsButton")
    backToMain = Message.get_message(language_code, "homeButton")
    addHabit = Message.get_message(language_code, "addHabitButton")
    statistic = "Statistic"
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=addHabit)],
            [KeyboardButton(text=habitListButton), KeyboardButton(text=todayHabits)],
            [KeyboardButton(text=statistic), KeyboardButton(text=backToMain)]
        ],
        resize_keyboard=True
    )

async def addHabitReplyKB(language_code: str) -> ReplyKeyboardMarkup:
    backToMain = Message.get_message(language_code, "homeButton")
    backToHabit = Message.get_message(language_code, "backToHabitButton")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=backToHabit)],
            [KeyboardButton(text=backToMain)]
        ],
        resize_keyboard=True
    )

async def habitsList(tg_id: int, language_code: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=Message.get_message(language_code, "editHabitButton"),
            callback_data="editHabits"
        ),
        InlineKeyboardButton(
            text=Message.get_message(language_code, "deleteHabitButton"),
            callback_data="deleteHabits"
        )
    )
    return keyboard.as_markup()

async def deleteHabits(tg_id: int) -> InlineKeyboardMarkup:
    habits = await getHabits(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for habit in habits:
        keyboard.add(InlineKeyboardButton(
            text=habit.name,
            callback_data=f"delhabit_{habit.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToHabitsList"
    ))
    return keyboard.adjust(1).as_markup()

async def editHabits(tg_id: int) -> InlineKeyboardMarkup:
    habits = await getHabits(tg_id)
    keyboard = InlineKeyboardBuilder()
    
    for habit in habits:
        keyboard.add(InlineKeyboardButton(
            text=habit.name,
            callback_data=f"edithabit_{habit.id}"
        ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToHabitsList"
    ))
    return keyboard.adjust(1).as_markup()

async def selectWeekdaysKB(language_code: str, selected_days=None) -> InlineKeyboardMarkup:
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
        keyboard.add(InlineKeyboardButton(
            text=buttonText,
            callback_data=dayCode
        ))
    
    keyboard.add(InlineKeyboardButton(
        text=Message.get_message(language_code, "done"),
        callback_data="habitDays_done"
    ))
    keyboard.adjust(2)
    return keyboard.as_markup()

async def todayHabits(tg_id: int, language_code: str) -> InlineKeyboardMarkup:
    currentDay = datetime.today().weekday()
    habits = await getTodayHabits(tg_id)
    keyboard = InlineKeyboardBuilder()

    today_habits = []
    for habit in habits:
        if len(habit.days_of_week) == 7 and habit.days_of_week[currentDay] == '1':
            today_habits.append(habit)

    if today_habits:
        for habit in today_habits:
            button_text = f"{habit.name}  |  +{habit.experience_points} ✨"
            keyboard.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"completedHabit_{habit.id}_{habit.experience_points}"
            ))
    else:
        keyboard.add(InlineKeyboardButton(
            text="No habits for today",
            callback_data="no_today_habits"
        ))
    
    return keyboard.adjust(1).as_markup()

# ... остальные функции для привычек 