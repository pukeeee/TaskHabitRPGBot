from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from app.messages import Message
from database.requests import getTask

async def tasks(tg_id):
    tasks = await getTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text = task.task, callback_data = f"task_{task.id}"))
    return keyboard.adjust(1).as_markup()

async def replyKb(language_code: str):
    button_text = Message.get_message(language_code, "taskListButton")
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = button_text)]],
                                                    resize_keyboard = True)
    return replyKeyboard