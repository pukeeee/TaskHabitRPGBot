from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import app.keyboards as kb
from config import CHANNEL


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware для проверки подписки пользователя на канал"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет подписку пользователя на канал
        
        Args:
            handler: Следующий обработчик
            event: Входящее событие
            data: Дополнительные данные
        """
        # Пропускаем команду /start и проверку подписки
        if isinstance(event, Message) and event.text and event.text.startswith("/info"):
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        user_id = event.from_user.id
        bot = event.bot

        # try:
        # Проверяем статус подписки
        member = await bot.get_chat_member(chat_id=CHANNEL, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return await handler(event, data)
        else:
            # Отправляем сообщение о необходимости подписки
            if isinstance(event, Message):
                await event.answer(
                    "Для использования бота необходимо подписаться на канал",
                    reply_markup=await kb.subscriptionKeyboard()
                )
            elif isinstance(event, CallbackQuery):
                if event.data == "check_subscription":
                    await event.answer(
                        "Для использования бота необходимо подписаться на канал",
                        show_alert=True
                    )
                else:
                    await event.message.answer(
                        "Для использования бота необходимо подписаться на канал",
                        reply_markup=await kb.subscriptionKeyboard()
                    )
                    await event.answer()
            return
                
        # except Exception as e:
        #     print(f"Error in subscription middleware: {e}")
        #     if isinstance(event, Message):
        #         await event.answer(
        #             "Для использования бота необходимо подписаться на канал",
        #             reply_markup=await kb.subscriptionKeyboard()
        #         )
        #     elif isinstance(event, CallbackQuery):
        #         if event.data == "check_subscription":
        #             await event.answer(
        #                 "Ошибка при проверке подписки",
        #                 show_alert=True
        #             )
        #         else:
        #             await event.message.answer(
        #                 "Для использования бота необходимо подписаться на канал",
        #                 reply_markup=await kb.subscriptionKeyboard()
        #             )
        #             await event.answer()
        #     return 