from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import app.keyboards as kb
from sqlalchemy.exc import SQLAlchemyError
from aiogram.fsm.context import FSMContext
from app.l10n import Message as L10nMessage
from database.repositories import (
    setUser,
    getUserDB,
    resetHabit
)
from aiogram.enums.parse_mode import ParseMode
from app.fsm import UserState, UserRPG
from config import CHANNEL
from app.handlers.commands import startCommand
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
                await state.set_state(UserState.startMenu)
            else:
                # Для нового пользователя или если не заполнены данные
                await state.set_state(UserRPG.setName)
                await callback.message.answer(
                    text=L10nMessage.get_message(language_code, "newCharacter"),
                    parse_mode=ParseMode.HTML
                )
        else:
            await callback.answer(
                "Для использования бота необходимо подписаться на канал",
                show_alert=True
            )
            
    except TelegramBadRequest as e:
        print(f"Telegram error in subscription check: {e}")
        await callback.answer(
            "Ошибка при проверке подписки. Убедитесь, что вы подписаны на канал",
            show_alert=True
        )
    except Exception as e:
        print(f"Error in subscription check: {e}")
        await callback.answer(
            "Произошла ошибка при проверке подписки",
            show_alert=True
        )