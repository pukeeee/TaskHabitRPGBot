from .base import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardBuilder
)
from app.l10n import Message
import os
import html
from config import IMG_FOLDER

async def startReplyKb(language_code: str) -> ReplyKeyboardMarkup:
    todoButton = Message.get_message(language_code, "taskTrackerButton")
    habitButton = Message.get_message(language_code, "habitTrackerButton")
    profile = Message.get_message(language_code, "profileButton")
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=todoButton), KeyboardButton(text=habitButton)],
            [KeyboardButton(text=profile)]
        ],
        resize_keyboard=True
    )



async def profileInLineKB(language_code: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=Message.get_message(language_code, "leaderboardButton"),
            callback_data="leaderboard"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=Message.get_message(language_code, "changeCharacterButton"),
            callback_data="changeAvatar"
        ),
        InlineKeyboardButton(
            text=Message.get_message(language_code, "changeNameButton"),
            callback_data="changeName"
        )
    )
    return keyboard.as_markup()

async def avatarNavigationKB(language_code: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⬅️", callback_data="prev_img"),
        InlineKeyboardButton(text="➡️", callback_data="next_img")
    )
    keyboard.row(InlineKeyboardButton(
        text=Message.get_message(language_code, "done"),
        callback_data="done_img"
    ))
    return keyboard.as_markup()

# ... остальные функции для профиля 