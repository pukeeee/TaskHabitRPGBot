from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import SQLAlchemyError
from aiogram.fsm.context import FSMContext
from app.l10n.l10n import Message as L10nMessage
from database.repositories import (
    setUser,
    getUserDB,
    resetHabit
)
from aiogram.enums.parse_mode import ParseMode
from app.states import User, Profile
from app.core.utils.config import CHANNEL
from app.keyboards import startReplyKb

router = Router()



@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, state: FSMContext, language_code: str):
    """Проверка подписки пользователя на канал"""
    try:
        user_id = callback.from_user.id
        bot = callback.bot
        channel_id = CHANNEL

        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        
        if member.status in ["member", "administrator", "creator"]:
            user = await getUserDB(user_id)
    
            if user and user.user_name and user.avatar:  # Проверяем что пользователь полностью настроен
                await callback.message.answer(
                    text=L10nMessage.get_message(language_code, "start"),
                    parse_mode=ParseMode.HTML,
                    reply_markup=await startReplyKb(language_code)
                )
                await state.set_state(User.startMenu)
            else:
                # Для нового пользователя или если не заполнены данные
                await state.set_state(Profile.setName)
                await callback.message.answer(
                    text=L10nMessage.get_message(language_code, "newCharacter"),
                    parse_mode=ParseMode.HTML
                )
        else:
            await callback.answer(
                L10nMessage.get_message(language_code, "subscription"),
                show_alert=True
            )
            
    except TelegramBadRequest as e:
        print(f"Telegram error in subscription check: {e}")
        await callback.answer(
            L10nMessage.get_message(language_code, "subscription"),
            show_alert=True
        )
    except Exception as e:
        print(f"Error in subscription check: {e}")
        await callback.answer(
            L10nMessage.get_message(language_code, "subscription"),
            show_alert=True
        )