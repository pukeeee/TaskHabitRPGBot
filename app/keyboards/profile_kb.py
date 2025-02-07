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

async def regRase() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    items = os.listdir(IMG_FOLDER)
    
    for item in items:
        item_path = os.path.join(IMG_FOLDER, item)
        if os.path.isdir(item_path):
            normalized_name = html.escape(item.strip())
            keyboard.add(InlineKeyboardButton(
                text=normalized_name,
                callback_data=f"raseFolder_{item}"
            ))
    
    keyboard.adjust(1)
    return keyboard.as_markup()

async def regSex(state) -> InlineKeyboardMarkup:
    data = await state.get_data()
    selected_race_folder = data.get('selected_race_folder')
    keyboard = InlineKeyboardBuilder()
    race_path = os.path.join(IMG_FOLDER, selected_race_folder)
    items = os.listdir(race_path)
    
    for item in items:
        item_path = os.path.join(race_path, item)
        if os.path.isdir(item_path):
            normalized_name = html.escape(item.strip())
            keyboard.add(InlineKeyboardButton(
                text=normalized_name,
                callback_data=f"sexFolder_{item}"
            ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToRace"
    ))
    keyboard.adjust(1)
    return keyboard.as_markup()

async def regClass(state) -> InlineKeyboardMarkup:
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
                text=normalized_name,
                callback_data=f"classFolder_{item}"
            ))
    
    keyboard.add(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToSex"
    ))
    keyboard.adjust(1)
    return keyboard.as_markup()

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
    keyboard.row(InlineKeyboardButton(
        text="🔙 Back",
        callback_data="backToClass"
    ))
    return keyboard.as_markup()

# ... остальные функции для профиля 