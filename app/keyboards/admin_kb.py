from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


async def adminKb():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Broadcast",
            callback_data="broadcast"
        )
    )
    return keyboard.as_markup()



async def broadcastTypeKeyboard():
    """Клавиатура выбора типа рассылки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Text only", callback_data="broadcast_text"),
                InlineKeyboardButton(text="With picture", callback_data="broadcast_pic")
            ],
            [
                InlineKeyboardButton(text="Back", callback_data="back_to_admin")
            ]
        ]
    )
    return keyboard



async def checkBroadcastKeyboard():
    """Клавиатура подтверждения рассылки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Send", callback_data="send_broadcast"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_broadcast")
            ]
        ]
    )
    return keyboard