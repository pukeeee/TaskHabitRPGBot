from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.requests import getTask

async def tasks(tg_id):
    tasks = await getTask(tg_id)
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text = task.task, callback_data = f"task_{task.id}"))
    return keyboard.adjust(1).as_markup()

async def replyKb():
    replyKeyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "My tasks")]],
                                    resize_keyboard = True)
    return replyKeyboard