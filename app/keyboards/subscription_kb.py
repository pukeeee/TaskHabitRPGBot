from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import CHANNEL

CHANNEL_ID = f"{CHANNEL}"


async def subscriptionKeyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Subscribe to the channel", url=f"https://t.me/{CHANNEL}")],
            [InlineKeyboardButton(text="Check subscription", callback_data="check_subscription")]
        ]
    )
    return keyboard